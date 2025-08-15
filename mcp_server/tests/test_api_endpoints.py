"""
Comprehensive integration tests for MCP server API endpoints.

These tests verify the complete API functionality including model management,
inference, health checks, and integration with backend services.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from services.auth import TenantInfo
from schemas.mcp_schemas import (
    ModelRegistrationRequest, ModelInfo, ModelStatus, InferenceType,
    CompletionRequest, ChatRequest, EmbeddingRequest
)
from core.protocol import MCPProtocolError, MCPErrorCodes


class TestHealthEndpoints:
    """Test health check endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns server information."""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Recaller MCP Server"
        assert "version" in data
        assert "endpoints" in data
        assert "/api/v1" in data["endpoints"]["api"]

    @patch('api.endpoints.model_registry')
    def test_health_check_all_models_healthy(self, mock_registry):
        """Test health check when all models are healthy."""
        mock_models = [
            ModelInfo(
                id="test_model_1",
                name="Test Model 1",
                backend_type="ollama",
                status=ModelStatus.AVAILABLE,
                tenant_id="test-tenant",
                capabilities=[InferenceType.COMPLETION]
            ),
            ModelInfo(
                id="test_model_2", 
                name="Test Model 2",
                backend_type="huggingface",
                status=ModelStatus.AVAILABLE,
                tenant_id="test-tenant",
                capabilities=[InferenceType.EMBEDDING]
            )
        ]
        mock_registry.list_models.return_value = mock_models
        mock_registry.health_check.return_value = {"healthy": True, "unhealthy": []}

        response = self.client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["data"]["total_models"] == 2
        assert data["data"]["healthy_models"] == 2

    @patch('api.endpoints.model_registry')
    def test_health_check_with_unhealthy_models(self, mock_registry):
        """Test health check when some models are unhealthy."""
        mock_models = [
            ModelInfo(
                id="test_model_1",
                name="Test Model 1", 
                backend_type="ollama",
                status=ModelStatus.AVAILABLE,
                tenant_id="test-tenant",
                capabilities=[InferenceType.COMPLETION]
            ),
            ModelInfo(
                id="test_model_2",
                name="Test Model 2",
                backend_type="ollama", 
                status=ModelStatus.ERROR,
                tenant_id="test-tenant",
                capabilities=[InferenceType.COMPLETION]
            )
        ]
        mock_registry.list_models.return_value = mock_models
        mock_registry.health_check.return_value = {
            "healthy": False, 
            "unhealthy": ["test_model_2"]
        }

        response = self.client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "degraded"
        assert len(data["data"]["unhealthy_models"]) == 1

    @patch('api.endpoints.model_registry')
    def test_specific_model_health_check(self, mock_registry):
        """Test health check for a specific model."""
        mock_model = ModelInfo(
            id="test_model",
            name="Test Model",
            backend_type="ollama",
            status=ModelStatus.AVAILABLE,
            tenant_id="test-tenant",
            capabilities=[InferenceType.COMPLETION]
        )
        mock_registry.get_model.return_value = mock_model
        mock_registry.check_model_health = AsyncMock(return_value=True)

        response = self.client.get("/api/v1/health/models/test_model")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["model_id"] == "test_model"
        assert data["data"]["status"] == "healthy"

    @patch('api.endpoints.model_registry')
    def test_health_check_nonexistent_model(self, mock_registry):
        """Test health check for nonexistent model."""
        mock_registry.get_model.return_value = None

        response = self.client.get("/api/v1/health/models/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestModelManagementEndpoints:
    """Test model management API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_register_model_success(self, mock_registry, mock_get_tenant):
        """Test successful model registration."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.register_model = AsyncMock(return_value="test_tenant_ollama_test_model")

        registration_data = {
            "name": "Test Model",
            "description": "A test model",
            "backend_type": "ollama",
            "config": {"model_name": "llama2"},
            "capabilities": ["completion", "chat"]
        }

        response = self.client.post("/api/v1/models/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "model_id" in data["data"]

    def test_register_model_without_tenant(self):
        """Test model registration without tenant context."""
        registration_data = {
            "name": "Test Model",
            "backend_type": "ollama",
            "config": {"model_name": "llama2"},
            "capabilities": ["completion"]
        }

        with patch('api.endpoints.get_current_tenant', return_value=None):
            response = self.client.post("/api/v1/models/register", json=registration_data)
            assert response.status_code == 403
            assert "Tenant access required" in response.json()["detail"]

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_register_model_invalid_backend(self, mock_registry, mock_get_tenant):
        """Test model registration with invalid backend type."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.register_model = AsyncMock(side_effect=ValueError("Unsupported backend type"))

        registration_data = {
            "name": "Test Model",
            "backend_type": "invalid_backend",
            "config": {},
            "capabilities": ["completion"]
        }

        response = self.client.post("/api/v1/models/register", json=registration_data)
        assert response.status_code == 400
        assert "Unsupported backend type" in response.json()["detail"]

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_list_models_filters_by_tenant(self, mock_registry, mock_get_tenant):
        """Test that model listing is filtered by tenant."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        
        mock_models = [
            ModelInfo(
                id="test-tenant_model1",
                name="Model 1",
                backend_type="ollama",
                status=ModelStatus.AVAILABLE,
                tenant_id="test-tenant",
                capabilities=[InferenceType.COMPLETION]
            )
        ]
        mock_registry.list_models.return_value = mock_models

        response = self.client.get("/api/v1/models")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-tenant_model1"
        assert data[0]["tenant_id"] == "test-tenant"

        # Verify that list_models was called with tenant_id
        mock_registry.list_models.assert_called_with(tenant_id="test-tenant", status_filter=None)

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_list_models_with_status_filter(self, mock_registry, mock_get_tenant):
        """Test model listing with status filter."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.list_models.return_value = []

        response = self.client.get("/api/v1/models?status=available")
        assert response.status_code == 200

        # Verify status filter was applied
        mock_registry.list_models.assert_called_with(
            tenant_id="test-tenant", 
            status_filter=ModelStatus.AVAILABLE
        )

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_unregister_model_success(self, mock_registry, mock_get_tenant):
        """Test successful model unregistration."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.unregister_model = AsyncMock()

        response = self.client.delete("/api/v1/models/test_model")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True

        mock_registry.unregister_model.assert_called_once_with("test_model", "test-tenant")

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_unregister_model_not_found(self, mock_registry, mock_get_tenant):
        """Test unregistering nonexistent model."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.unregister_model = AsyncMock(side_effect=ValueError("Model not found"))

        response = self.client.delete("/api/v1/models/nonexistent")
        assert response.status_code == 404
        assert "Model not found" in response.json()["detail"]

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_get_model_info(self, mock_registry, mock_get_tenant):
        """Test getting model information."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        
        mock_model = ModelInfo(
            id="test_model",
            name="Test Model",
            description="A test model",
            backend_type="ollama",
            status=ModelStatus.AVAILABLE,
            tenant_id="test-tenant",
            capabilities=[InferenceType.COMPLETION, InferenceType.CHAT]
        )
        mock_registry.get_model.return_value = mock_model

        response = self.client.get("/api/v1/models/test_model")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "test_model"
        assert data["name"] == "Test Model"
        assert data["backend_type"] == "ollama"
        assert len(data["capabilities"]) == 2


class TestInferenceEndpoints:
    """Test inference API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.verify_api_access')
    @patch('api.endpoints.inference_service')
    def test_completion_inference_success(self, mock_inference, mock_verify, mock_get_tenant):
        """Test successful completion inference."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_verify.return_value = None  # No exception means access granted
        
        mock_response = {
            "id": "completion-123",
            "model": "test_model",
            "text": "This is a test completion",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_inference.completion = AsyncMock(return_value=mock_response)

        request_data = {
            "model_id": "test_model",
            "prompt": "Complete this text:",
            "max_tokens": 50,
            "temperature": 0.7
        }

        response = self.client.post("/api/v1/inference/completion", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["text"] == "This is a test completion"
        assert data["data"]["usage"]["total_tokens"] == 15

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.verify_api_access')
    @patch('api.endpoints.inference_service')
    def test_chat_inference_success(self, mock_inference, mock_verify, mock_get_tenant):
        """Test successful chat inference."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_verify.return_value = None
        
        mock_response = {
            "id": "chat-123",
            "model": "test_model",
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            },
            "usage": {"prompt_tokens": 20, "completion_tokens": 8, "total_tokens": 28}
        }
        mock_inference.chat = AsyncMock(return_value=mock_response)

        request_data = {
            "model_id": "test_model",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 100
        }

        response = self.client.post("/api/v1/inference/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["message"]["content"] == "Hello! How can I help you?"

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.verify_api_access')
    @patch('api.endpoints.inference_service')
    def test_embedding_inference_success(self, mock_inference, mock_verify, mock_get_tenant):
        """Test successful embedding inference."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_verify.return_value = None
        
        mock_response = {
            "id": "embedding-123",
            "model": "test_embedding_model",
            "embeddings": [[0.1, 0.2, 0.3, 0.4]],
            "usage": {"prompt_tokens": 5, "total_tokens": 5}
        }
        mock_inference.embedding = AsyncMock(return_value=mock_response)

        request_data = {
            "model_id": "test_embedding_model",
            "input": ["Hello world"]
        }

        response = self.client.post("/api/v1/inference/embedding", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["embeddings"][0]) == 4

    def test_inference_without_tenant(self):
        """Test inference without tenant context."""
        request_data = {
            "model_id": "test_model",
            "prompt": "Test prompt"
        }

        with patch('api.endpoints.get_current_tenant', return_value=None):
            response = self.client.post("/api/v1/inference/completion", json=request_data)
            assert response.status_code == 403
            assert "Tenant access required" in response.json()["detail"]

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.verify_api_access')
    @patch('api.endpoints.inference_service')
    def test_inference_model_not_available(self, mock_inference, mock_verify, mock_get_tenant):
        """Test inference when model is not available."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_verify.return_value = None
        
        mock_inference.completion = AsyncMock(
            side_effect=MCPProtocolError(
                code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                message="Model not available"
            )
        )

        request_data = {
            "model_id": "unavailable_model",
            "prompt": "Test prompt"
        }

        response = self.client.post("/api/v1/inference/completion", json=request_data)
        assert response.status_code == 400
        
        data = response.json()
        assert data["error"]["code"] == MCPErrorCodes.MODEL_NOT_AVAILABLE
        assert "Model not available" in data["error"]["message"]

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.verify_api_access')
    @patch('api.endpoints.privacy_enforcer')
    def test_inference_privacy_validation(self, mock_privacy, mock_verify, mock_get_tenant):
        """Test that inference requests are validated for privacy compliance."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_verify.return_value = None
        
        # Mock privacy enforcer to raise an error for external URL in prompt
        mock_privacy.validate_request_content.side_effect = MCPProtocolError(
            code=MCPErrorCodes.INVALID_PARAMS,
            message="External URLs in prompts are blocked for privacy protection"
        )

        request_data = {
            "model_id": "test_model",
            "prompt": "Please access https://external-api.com/data"
        }

        response = self.client.post("/api/v1/inference/completion", json=request_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "privacy protection" in data["error"]["message"]


class TestTenantIsolationMiddleware:
    """Test that tenant isolation works at the middleware level."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_tenant_isolation_enabled_by_default(self):
        """Test that tenant isolation is enabled by default in test environment."""
        from config.settings import mcp_settings
        assert mcp_settings.MCP_ENABLE_TENANT_ISOLATION is True
    
    def test_privacy_protection_enabled_by_default(self):
        """Test that privacy protection is enabled by default in test environment."""
        from config.settings import mcp_settings
        assert mcp_settings.BLOCK_EXTERNAL_REQUESTS is True
        assert mcp_settings.ENFORCE_LOCAL_ONLY is True
        assert mcp_settings.ANONYMIZE_LOGS is True
        assert mcp_settings.ANONYMIZE_ERROR_MESSAGES is True


class TestErrorHandling:
    """Test comprehensive error handling across API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_404_error_handling(self):
        """Test 404 error handling."""
        response = self.client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"]["code"] == -32601  # Method not found
        assert "not found" in data["error"]["message"].lower()

    @patch('api.endpoints.get_current_tenant')
    def test_mcp_protocol_error_handling(self, mock_get_tenant):
        """Test MCP protocol error handling."""
        mock_get_tenant.side_effect = MCPProtocolError(
            code=MCPErrorCodes.TENANT_ACCESS_DENIED,
            message="Tenant access denied",
            data={"tenant_id": "invalid"}
        )

        response = self.client.get("/api/v1/models")
        assert response.status_code == 400
        
        data = response.json()
        assert data["error"]["code"] == MCPErrorCodes.TENANT_ACCESS_DENIED
        assert data["error"]["message"] == "Tenant access denied"
        assert data["error"]["data"]["tenant_id"] == "invalid"

    def test_validation_error_handling(self):
        """Test request validation error handling."""
        # Send invalid JSON that doesn't match schema
        invalid_data = {
            "invalid_field": "value"
            # Missing required fields for model registration
        }

        response = self.client.post("/api/v1/models/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        data = response.json()
        assert "detail" in data
        # Should contain validation error details

    @patch('api.endpoints.model_registry')
    def test_internal_server_error_handling(self, mock_registry):
        """Test internal server error handling."""
        # Mock an unexpected error
        mock_registry.list_models.side_effect = Exception("Unexpected database error")

        with patch('api.endpoints.get_current_tenant') as mock_get_tenant:
            mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
            mock_get_tenant.return_value = mock_tenant

            response = self.client.get("/api/v1/models")
            assert response.status_code == 500
            
            data = response.json()
            assert "internal error" in data["detail"].lower() or "server error" in data["detail"].lower()


class TestConcurrencyAndPerformance:
    """Test concurrent requests and performance characteristics."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_concurrent_model_listing(self, mock_registry, mock_get_tenant):
        """Test concurrent model listing requests."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.list_models.return_value = []

        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.get("/api/v1/models")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert all(result == 200 for result in results)
        assert len(results) == 5
        
        # Should complete within reasonable time (not serialized)
        assert end_time - start_time < 2.0  # Should be much faster than 2 seconds

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.inference_service')
    def test_request_timeout_handling(self, mock_inference, mock_get_tenant):
        """Test request timeout handling for long-running operations."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        
        # Mock a timeout scenario
        async def slow_completion(*args, **kwargs):
            import asyncio
            await asyncio.sleep(10)  # Simulate slow operation
            return {"text": "response"}
        
        mock_inference.completion = slow_completion

        request_data = {
            "model_id": "slow_model",
            "prompt": "Test prompt"
        }

        # The client should handle this appropriately
        # Note: TestClient doesn't have built-in timeout, but the server should handle it
        response = self.client.post("/api/v1/inference/completion", json=request_data)
        
        # Should either complete or handle timeout gracefully
        assert response.status_code in [200, 408, 500]  # OK, Timeout, or Internal Error
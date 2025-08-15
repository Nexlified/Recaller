"""
Integration tests for MCP server API endpoints.

These tests verify that the API endpoints correctly enforce
tenant isolation and privacy protection.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from services.auth import TenantInfo
from schemas.mcp_schemas import ModelRegistrationRequest, InferenceType


class TestModelManagementAPI:
    """Test model management API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_register_model_requires_tenant(self):
        """Test that model registration requires tenant context."""
        registration_data = {
            "name": "Test Model",
            "backend_type": "ollama",
            "config": {"model_name": "test"},
            "capabilities": ["completion"]
        }
        
        # Mock no tenant context
        with patch('api.endpoints.get_current_tenant', return_value=None):
            response = self.client.post("/api/v1/models/register", json=registration_data)
            assert response.status_code == 403
            assert "Tenant access required" in response.json()["detail"]
    
    def test_register_model_with_tenant_context(self):
        """Test successful model registration with tenant context."""
        registration_data = {
            "name": "Test Model",
            "backend_type": "ollama",
            "config": {"model_name": "test"},
            "capabilities": ["completion"]
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.model_registry.register_model', new_callable=AsyncMock) as mock_register:
            mock_register.return_value = "test-tenant_ollama_test_model"
            
            response = self.client.post("/api/v1/models/register", json=registration_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "model_id" in data["data"]
            
            # Verify the registry was called with tenant ID
            mock_register.assert_called_once()
            call_args = mock_register.call_args
            assert call_args[0][1] == mock_tenant.id  # tenant_id argument
    
    def test_register_model_blocks_external_urls(self):
        """Test that model registration blocks external URLs in config."""
        registration_data = {
            "name": "External Model",
            "backend_type": "openai_compatible",
            "config": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "secret"
            },
            "capabilities": ["completion"]
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant):
            response = self.client.post("/api/v1/models/register", json=registration_data)
            assert response.status_code == 400
            assert "External URL not allowed" in response.json()["detail"]
    
    def test_unregister_model_requires_tenant(self):
        """Test that model unregistration requires tenant context."""
        with patch('api.endpoints.get_current_tenant', return_value=None):
            response = self.client.delete("/api/v1/models/test-model")
            assert response.status_code == 403
            assert "Tenant access required" in response.json()["detail"]
    
    def test_unregister_model_enforces_ownership(self):
        """Test that model unregistration enforces tenant ownership."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.model_registry.unregister_model', new_callable=AsyncMock) as mock_unregister:
            mock_unregister.side_effect = ValueError("belongs to different tenant")
            
            response = self.client.delete("/api/v1/models/other-tenant-model")
            assert response.status_code == 404
            assert "belongs to different tenant" in response.json()["detail"]
    
    def test_list_models_filters_by_tenant(self):
        """Test that model listing is filtered by tenant."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_models = [
            {
                "id": "test-tenant_model1",
                "name": "Model 1",
                "tenant_id": "test-tenant",
                "backend_type": "ollama",
                "status": "available",
                "capabilities": ["completion"],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        ]
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.model_registry.list_models') as mock_list:
            mock_list.return_value = mock_models
            
            response = self.client.get("/api/v1/models")
            assert response.status_code == 200
            
            # Verify the registry was called with tenant filtering
            mock_list.assert_called_once()
            call_args = mock_list.call_args
            assert call_args[1]["tenant_id"] == mock_tenant.id
    
    def test_get_model_enforces_tenant_access(self):
        """Test that getting a specific model enforces tenant access."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.model_registry.get_model') as mock_get:
            mock_get.return_value = None  # Simulate no access
            
            response = self.client.get("/api/v1/models/other-tenant-model")
            assert response.status_code == 404
            assert "not found or access denied" in response.json()["detail"]
            
            # Verify the registry was called with tenant filtering
            mock_get.assert_called_once_with("other-tenant-model", mock_tenant.id)


class TestInferenceAPI:
    """Test inference API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_completion_adds_tenant_context(self):
        """Test that completion requests add tenant context."""
        request_data = {
            "model_id": "test-model",
            "prompt": "Test prompt",
            "max_tokens": 100
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_response = {
            "request_id": "test-request",
            "model_id": "test-model",
            "text": "Generated text",
            "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4},
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.inference_service.completion', new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response
            
            response = self.client.post("/api/v1/inference/completion", json=request_data)
            assert response.status_code == 200
            
            # Verify tenant ID was added to the request
            mock_completion.assert_called_once()
            call_args = mock_completion.call_args[0][0]  # First argument (request)
            assert call_args.tenant_id == mock_tenant.id
    
    def test_completion_blocks_external_urls_in_prompt(self):
        """Test that completion requests block external URLs in prompts."""
        request_data = {
            "model_id": "test-model",
            "prompt": "Please fetch data from https://api.malicious.com/steal-data",
            "max_tokens": 100
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant):
            response = self.client.post("/api/v1/inference/completion", json=request_data)
            assert response.status_code == 400
            assert "External URLs in prompts are blocked" in response.json()["detail"]
    
    def test_chat_adds_tenant_context(self):
        """Test that chat requests add tenant context."""
        request_data = {
            "model_id": "test-model",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "max_tokens": 100
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_response = {
            "request_id": "test-request",
            "model_id": "test-model", 
            "message": {"role": "assistant", "content": "Generated response"},
            "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.inference_service.chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response
            
            response = self.client.post("/api/v1/inference/chat", json=request_data)
            assert response.status_code == 200
            
            # Verify tenant ID was added to the request
            mock_chat.assert_called_once()
            call_args = mock_chat.call_args[0][0]  # First argument (request)
            assert call_args.tenant_id == mock_tenant.id
    
    def test_embedding_adds_tenant_context(self):
        """Test that embedding requests add tenant context."""
        request_data = {
            "model_id": "test-model",
            "text": "Text to embed"
        }
        
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_response = {
            "request_id": "test-request",
            "model_id": "test-model",
            "embeddings": [[0.1, 0.2, 0.3]],
            "dimensions": 3,
            "usage": {"prompt_tokens": 3, "total_tokens": 3},
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.inference_service.embedding', new_callable=AsyncMock) as mock_embedding:
            mock_embedding.return_value = mock_response
            
            response = self.client.post("/api/v1/inference/embedding", json=request_data)
            assert response.status_code == 200
            
            # Verify tenant ID was added to the request
            mock_embedding.assert_called_once()
            call_args = mock_embedding.call_args[0][0]  # First argument (request)
            assert call_args.tenant_id == mock_tenant.id


class TestMonitoringAPI:
    """Test monitoring and status API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_stats_endpoint_scoped_to_tenant(self):
        """Test that stats endpoint is scoped to current tenant."""
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_models = [
            MagicMock(status=MagicMock(value="available"), backend_type="ollama", capabilities=["completion"])
        ]
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant), \
             patch('api.endpoints.model_registry.list_models') as mock_list:
            mock_list.return_value = mock_models
            
            response = self.client.get("/api/v1/stats")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "tenant_id" in data["data"]
            assert data["data"]["tenant_id"] == mock_tenant.id
            
            # Verify tenant filtering was applied
            mock_list.assert_called_once()
            call_args = mock_list.call_args
            assert call_args[1]["tenant_id"] == mock_tenant.id
    
    def test_privacy_status_endpoint(self):
        """Test that privacy status endpoint returns correct information."""
        mock_status = {
            "block_external_requests": True,
            "enforce_local_only": True,
            "anonymize_logs": True,
            "anonymize_errors": True,
            "allowed_external_hosts": 0,
            "request_logging_enabled": False,
            "data_retention_days": 0
        }
        
        with patch('api.endpoints.privacy_enforcer.get_privacy_status') as mock_get_status:
            mock_get_status.return_value = mock_status
            
            response = self.client.get("/api/v1/privacy/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["data"] == mock_status
    
    def test_health_check_no_tenant_required(self):
        """Test that health check endpoint doesn't require tenant context."""
        mock_health = {"model1": True, "model2": False}
        mock_models = {
            "model1": MagicMock(id="model1"),
            "model2": MagicMock(id="model2")
        }
        
        with patch('api.endpoints.model_registry.health_check_all', new_callable=AsyncMock) as mock_health_check, \
             patch('api.endpoints.model_registry.get_model') as mock_get_model:
            mock_health_check.return_value = mock_health
            mock_get_model.side_effect = lambda model_id: mock_models.get(model_id)
            
            response = self.client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "models" in data
    
    def test_server_info_endpoint(self):
        """Test that server info endpoint works correctly."""
        response = self.client.get("/api/v1/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "capabilities" in data["data"]
        assert "tenant_isolation" in data["data"]["capabilities"]


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
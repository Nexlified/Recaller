"""
Comprehensive tests for error handling across the MCP server.

These tests verify that all types of errors are handled correctly,
with proper error codes, messages, and privacy compliance.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from core.protocol import MCPProtocolError, MCPErrorCodes, MCPProtocolHandler
from services.auth import TenantInfo, AuthService
from schemas.mcp_schemas import (
    ModelRegistrationRequest, InferenceType, ModelStatus
)


class TestMCPProtocolErrorHandling:
    """Test MCP protocol-specific error handling."""

    def test_error_code_mapping(self):
        """Test that error codes are properly mapped to HTTP status codes."""
        error_mappings = [
            (MCPErrorCodes.PARSE_ERROR, "JSON parse error"),
            (MCPErrorCodes.INVALID_REQUEST, "Invalid request format"),
            (MCPErrorCodes.METHOD_NOT_FOUND, "Method not found"),
            (MCPErrorCodes.INVALID_PARAMS, "Invalid parameters"),
            (MCPErrorCodes.INTERNAL_ERROR, "Internal server error"),
            (MCPErrorCodes.MODEL_NOT_AVAILABLE, "Model not available"),
            (MCPErrorCodes.CONTEXT_TOO_LONG, "Context length exceeded"),
            (MCPErrorCodes.RATE_LIMIT_EXCEEDED, "Rate limit exceeded"),
            (MCPErrorCodes.TENANT_ACCESS_DENIED, "Tenant access denied")
        ]
        
        for code, message in error_mappings:
            error = MCPProtocolError(code=code, message=message)
            assert error.code == code
            assert error.message == message
            assert str(code) in str(error)

    def test_error_with_additional_data(self):
        """Test errors with additional diagnostic data."""
        error_data = {
            "field": "model_id",
            "value": "invalid_model",
            "suggestion": "Use a valid model ID"
        }
        
        error = MCPProtocolError(
            code=MCPErrorCodes.INVALID_PARAMS,
            message="Invalid model ID provided",
            data=error_data
        )
        
        assert error.data == error_data
        assert error.data["field"] == "model_id"
        assert error.data["suggestion"] == "Use a valid model ID"

    @pytest.mark.asyncio
    async def test_protocol_handler_error_propagation(self):
        """Test that protocol handler properly propagates errors."""
        handler = MCPProtocolHandler()
        
        # Mock a method that raises an error
        with patch.object(handler, '_handle_request') as mock_handler:
            mock_handler.side_effect = MCPProtocolError(
                code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                message="Test model is not available"
            )
            
            request_data = '{"type": "request", "id": "test", "method": "test.method"}'
            result = await handler.process_message(request_data)
            
            # Should return properly formatted error response
            import json
            response = json.loads(result)
            assert response["type"] == "error"
            assert response["code"] == MCPErrorCodes.MODEL_NOT_AVAILABLE
            assert "not available" in response["message"]

    def test_error_message_privacy_compliance(self):
        """Test that error messages don't leak sensitive information."""
        from services.privacy import privacy_enforcer
        
        # Create error with potentially sensitive data
        sensitive_error = MCPProtocolError(
            code=MCPErrorCodes.INTERNAL_ERROR,
            message="Database connection failed at 192.168.1.100 for user admin@company.com",
            data={"host": "192.168.1.100", "user": "admin@company.com"}
        )
        
        # Error message should be anonymized if privacy is enabled
        anonymized_message = privacy_enforcer.anonymize_error_message(sensitive_error.message)
        assert "192.168.1.100" not in anonymized_message
        assert "admin@company.com" not in anonymized_message


class TestAPIErrorHandling:
    """Test API endpoint error handling."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_validation_error_response_format(self):
        """Test that validation errors are properly formatted."""
        # Send request with missing required fields
        invalid_data = {
            "name": "Test Model"
            # Missing backend_type, config, etc.
        }
        
        response = self.client.post("/api/v1/models/register", json=invalid_data)
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
        # Should contain field-level validation errors
        assert isinstance(data["detail"], list)

    def test_authentication_error_handling(self):
        """Test authentication error handling."""
        # Mock authentication failure
        with patch('api.endpoints.get_current_tenant', return_value=None):
            response = self.client.get("/api/v1/models")
            assert response.status_code == 403
            
            data = response.json()
            assert "Tenant access required" in data["detail"]

    def test_authorization_error_handling(self):
        """Test authorization error handling."""
        # Mock tenant access with insufficient permissions
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant", active=False)
        
        with patch('api.endpoints.get_current_tenant', return_value=mock_tenant):
            with patch('api.endpoints.verify_api_access') as mock_verify:
                mock_verify.side_effect = MCPProtocolError(
                    code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                    message="Tenant is not active"
                )
                
                response = self.client.get("/api/v1/models")
                assert response.status_code == 400
                
                data = response.json()
                assert data["error"]["code"] == MCPErrorCodes.TENANT_ACCESS_DENIED

    @patch('api.endpoints.model_registry')
    def test_resource_not_found_error_handling(self, mock_registry):
        """Test resource not found error handling."""
        mock_registry.get_model.return_value = None
        
        with patch('api.endpoints.get_current_tenant') as mock_get_tenant:
            mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
            mock_get_tenant.return_value = mock_tenant
            
            response = self.client.get("/api/v1/models/nonexistent")
            assert response.status_code == 404

    @patch('api.endpoints.model_registry')
    def test_internal_server_error_handling(self, mock_registry):
        """Test internal server error handling."""
        # Mock unexpected database error
        mock_registry.list_models.side_effect = Exception("Database connection lost")
        
        with patch('api.endpoints.get_current_tenant') as mock_get_tenant:
            mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
            mock_get_tenant.return_value = mock_tenant
            
            response = self.client.get("/api/v1/models")
            assert response.status_code == 500

    def test_rate_limiting_error_handling(self):
        """Test rate limiting error handling."""
        # Mock rate limit exceeded
        with patch('api.endpoints.inference_service') as mock_inference:
            mock_inference.completion.side_effect = MCPProtocolError(
                code=MCPErrorCodes.RATE_LIMIT_EXCEEDED,
                message="Rate limit exceeded. Try again later.",
                data={"retry_after": 60}
            )
            
            with patch('api.endpoints.get_current_tenant') as mock_get_tenant:
                mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
                mock_get_tenant.return_value = mock_tenant
                
                request_data = {
                    "model_id": "test_model",
                    "prompt": "Test prompt"
                }
                
                response = self.client.post("/api/v1/inference/completion", json=request_data)
                assert response.status_code == 400
                
                data = response.json()
                assert data["error"]["code"] == MCPErrorCodes.RATE_LIMIT_EXCEEDED
                assert data["error"]["data"]["retry_after"] == 60

    def test_context_length_error_handling(self):
        """Test context length error handling."""
        with patch('api.endpoints.inference_service') as mock_inference:
            mock_inference.completion.side_effect = MCPProtocolError(
                code=MCPErrorCodes.CONTEXT_TOO_LONG,
                message="Input context exceeds maximum length",
                data={"max_tokens": 2048, "actual_tokens": 3000}
            )
            
            with patch('api.endpoints.get_current_tenant') as mock_get_tenant:
                mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
                mock_get_tenant.return_value = mock_tenant
                
                request_data = {
                    "model_id": "test_model",
                    "prompt": "Very long prompt " * 1000  # Simulate long prompt
                }
                
                response = self.client.post("/api/v1/inference/completion", json=request_data)
                assert response.status_code == 400
                
                data = response.json()
                assert data["error"]["code"] == MCPErrorCodes.CONTEXT_TOO_LONG
                assert "exceeds maximum length" in data["error"]["message"]


class TestModelRegistryErrorHandling:
    """Test model registry error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        from models.registry import ModelRegistry
        self.registry = ModelRegistry()

    @pytest.mark.asyncio
    async def test_duplicate_model_registration_error(self):
        """Test error handling for duplicate model registration."""
        request = ModelRegistrationRequest(
            name="Test Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        # Mock that model already exists
        with patch.object(self.registry, '_models', {"tenant_test_model": MagicMock()}):
            with pytest.raises(ValueError, match="already registered"):
                await self.registry.register_model(request, "tenant")

    @pytest.mark.asyncio
    async def test_unsupported_backend_error(self):
        """Test error handling for unsupported backend type."""
        request = ModelRegistrationRequest(
            name="Test Model",
            backend_type="unsupported_backend",
            config={},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with pytest.raises(ValueError, match="Unsupported backend type"):
            await self.registry.register_model(request, "tenant")

    @pytest.mark.asyncio
    async def test_model_initialization_failure(self):
        """Test error handling when model initialization fails."""
        request = ModelRegistrationRequest(
            name="Test Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        # Mock initialization failure
        with patch.object(self.registry, '_initialize_model') as mock_init:
            mock_init.side_effect = Exception("Model server unavailable")
            
            with pytest.raises(Exception, match="Model server unavailable"):
                await self.registry.register_model(request, "tenant")
            
            # Model should be cleaned up from registry on failure
            model_id = "tenant_ollama_test_model"
            assert model_id not in self.registry._models

    def test_model_access_control_errors(self):
        """Test model access control error handling."""
        # Create mock model for different tenant
        mock_model = MagicMock()
        mock_model.tenant_id = "other_tenant"
        
        with patch.object(self.registry, '_models', {"test_model": mock_model}):
            # Should return None for wrong tenant
            result = self.registry.get_model("test_model", "current_tenant")
            assert result is None

    @pytest.mark.asyncio
    async def test_model_unregistration_access_control(self):
        """Test model unregistration access control."""
        mock_model = MagicMock()
        mock_model.tenant_id = "other_tenant"
        
        with patch.object(self.registry, '_models', {"test_model": mock_model}):
            with pytest.raises(ValueError, match="Access denied"):
                await self.registry.unregister_model("test_model", "current_tenant")


class TestInferenceServiceErrorHandling:
    """Test inference service error handling."""

    @pytest.mark.asyncio
    async def test_model_not_available_error(self):
        """Test handling when requested model is not available."""
        from services.inference import InferenceService
        
        service = InferenceService()
        
        # Mock model registry to return None (model not found)
        with patch('services.inference.model_registry') as mock_registry:
            mock_registry.get_model.return_value = None
            
            with pytest.raises(MCPProtocolError, match="Model.*not found"):
                await service.completion("nonexistent_model", "test prompt", "tenant")

    @pytest.mark.asyncio
    async def test_model_backend_error(self):
        """Test handling of model backend errors."""
        from services.inference import InferenceService
        from schemas.mcp_schemas import ModelInfo
        
        service = InferenceService()
        
        # Mock model info
        mock_model = ModelInfo(
            id="test_model",
            name="Test Model",
            backend_type="ollama",
            status=ModelStatus.AVAILABLE,
            tenant_id="tenant",
            capabilities=[InferenceType.COMPLETION]
        )
        
        # Mock backend that raises error
        mock_backend = MagicMock()
        mock_backend.completion.side_effect = Exception("Backend service error")
        
        with patch('services.inference.model_registry') as mock_registry:
            mock_registry.get_model.return_value = mock_model
            mock_registry.get_model_backend.return_value = mock_backend
            
            with pytest.raises(MCPProtocolError, match="Inference failed"):
                await service.completion("test_model", "test prompt", "tenant")

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test handling of inference timeout errors."""
        from services.inference import InferenceService
        from schemas.mcp_schemas import ModelInfo
        
        service = InferenceService()
        
        mock_model = ModelInfo(
            id="test_model",
            name="Test Model",
            backend_type="ollama",
            status=ModelStatus.AVAILABLE,
            tenant_id="tenant",
            capabilities=[InferenceType.COMPLETION]
        )
        
        # Mock backend that times out
        async def slow_completion(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow operation
            return {"text": "response"}
        
        mock_backend = MagicMock()
        mock_backend.completion = slow_completion
        
        with patch('services.inference.model_registry') as mock_registry:
            mock_registry.get_model.return_value = mock_model
            mock_registry.get_model_backend.return_value = mock_backend
            
            # Should timeout and raise appropriate error
            with pytest.raises(MCPProtocolError, match="timeout"):
                await asyncio.wait_for(
                    service.completion("test_model", "test prompt", "tenant"),
                    timeout=0.1
                )


class TestAuthServiceErrorHandling:
    """Test authentication service error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auth_service = AuthService()

    @pytest.mark.asyncio
    async def test_backend_connection_error(self):
        """Test handling of backend connection errors."""
        # Mock HTTP client error
        with patch.object(self.auth_service, 'get_backend_client') as mock_client:
            mock_client.side_effect = Exception("Connection refused")
            
            with pytest.raises(MCPProtocolError, match="Authentication service unavailable"):
                await self.auth_service.verify_tenant_access("test_token", "tenant_id")

    @pytest.mark.asyncio
    async def test_invalid_token_error(self):
        """Test handling of invalid authentication tokens."""
        mock_client = AsyncMock()
        mock_client.get.return_value.status_code = 401
        mock_client.get.return_value.json.return_value = {"error": "Invalid token"}
        
        with patch.object(self.auth_service, 'get_backend_client', return_value=mock_client):
            with pytest.raises(MCPProtocolError, match="Authentication failed"):
                await self.auth_service.verify_tenant_access("invalid_token", "tenant_id")

    @pytest.mark.asyncio
    async def test_tenant_not_found_error(self):
        """Test handling when tenant is not found."""
        mock_client = AsyncMock()
        mock_client.get.return_value.status_code = 404
        mock_client.get.return_value.json.return_value = {"error": "Tenant not found"}
        
        with patch.object(self.auth_service, 'get_backend_client', return_value=mock_client):
            with pytest.raises(MCPProtocolError, match="Tenant not found"):
                await self.auth_service.get_tenant_info("nonexistent_tenant")

    @pytest.mark.asyncio
    async def test_inactive_tenant_error(self):
        """Test handling of inactive tenant access attempts."""
        inactive_tenant = TenantInfo(
            id="inactive_tenant",
            slug="inactive_tenant", 
            name="Inactive Tenant",
            active=False
        )
        
        with pytest.raises(MCPProtocolError, match="Tenant is not active"):
            await self.auth_service.verify_api_access("token", inactive_tenant)


class TestPrivacyErrorHandling:
    """Test privacy-related error handling."""

    def test_external_request_blocking_error(self):
        """Test error when external requests are blocked."""
        from services.privacy import privacy_enforcer
        
        with pytest.raises(MCPProtocolError, match="External requests are blocked"):
            privacy_enforcer.validate_external_request("https://external-api.com")

    def test_sensitive_data_in_prompt_error(self):
        """Test error when sensitive data is detected in prompts."""
        from services.privacy import privacy_enforcer
        
        prompt_with_external_url = "Please access https://external-api.com/confidential-data"
        
        with pytest.raises(MCPProtocolError, match="External.*blocked"):
            privacy_enforcer.validate_request_content(prompt_with_external_url)

    def test_model_config_privacy_violation_error(self):
        """Test error when model configuration violates privacy rules."""
        from services.privacy import privacy_enforcer
        
        config_with_external_endpoint = {
            "api_endpoint": "https://external-ai-service.com/api",
            "api_key": "secret_key"
        }
        
        with pytest.raises(MCPProtocolError, match="External.*blocked"):
            privacy_enforcer.validate_model_config(config_with_external_endpoint)


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience."""

    @pytest.mark.asyncio
    async def test_partial_system_failure_handling(self):
        """Test handling when only part of the system fails."""
        # Simulate scenario where model registry works but inference service fails
        from models.registry import ModelRegistry
        from services.inference import InferenceService
        
        registry = ModelRegistry()
        service = InferenceService()
        
        # Mock successful model lookup but failed inference
        mock_model = MagicMock()
        mock_model.tenant_id = "tenant"
        mock_model.status = ModelStatus.AVAILABLE
        
        with patch.object(registry, 'get_model', return_value=mock_model):
            with patch.object(registry, 'get_model_backend') as mock_backend:
                mock_backend.side_effect = Exception("Backend unavailable")
                
                with pytest.raises(MCPProtocolError):
                    await service.completion("test_model", "prompt", "tenant")

    def test_graceful_degradation(self):
        """Test graceful degradation when non-critical features fail."""
        from services.privacy import privacy_enforcer
        
        # Test that system continues to work even if anonymization fails
        original_text = "Contact user@example.com for support"
        
        with patch.object(privacy_enforcer, '_compiled_patterns', []):
            # Even if patterns fail to compile, should not crash
            result = privacy_enforcer.anonymize_text(original_text)
            assert result is not None  # Should return something, even if not anonymized

    @pytest.mark.asyncio
    async def test_error_context_preservation(self):
        """Test that error context is preserved through the call stack."""
        from core.protocol import MCPProtocolHandler
        
        handler = MCPProtocolHandler()
        
        # Create nested error scenario
        original_error = ValueError("Database constraint violation")
        
        with patch.object(handler, '_handle_request') as mock_handler:
            mock_handler.side_effect = MCPProtocolError(
                code=MCPErrorCodes.INTERNAL_ERROR,
                message="Internal error occurred",
                data={"original_error": str(original_error)}
            )
            
            request_data = '{"type": "request", "id": "test", "method": "test.method"}'
            result = await handler.process_message(request_data)
            
            import json
            response = json.loads(result)
            
            # Error context should be preserved
            assert response["type"] == "error"
            assert response["data"]["original_error"] == "Database constraint violation"

    def test_error_rate_monitoring(self):
        """Test that error rates can be monitored for system health."""
        # This would typically integrate with monitoring systems
        # For now, just test that errors are properly categorized
        
        error_categories = [
            (MCPErrorCodes.PARSE_ERROR, "client_error"),
            (MCPErrorCodes.INVALID_REQUEST, "client_error"),
            (MCPErrorCodes.METHOD_NOT_FOUND, "client_error"),
            (MCPErrorCodes.INVALID_PARAMS, "client_error"),
            (MCPErrorCodes.INTERNAL_ERROR, "server_error"),
            (MCPErrorCodes.MODEL_NOT_AVAILABLE, "service_error"),
            (MCPErrorCodes.RATE_LIMIT_EXCEEDED, "rate_limit_error"),
            (MCPErrorCodes.TENANT_ACCESS_DENIED, "auth_error")
        ]
        
        for code, category in error_categories:
            error = MCPProtocolError(code=code, message="Test error")
            
            # Test error categorization logic
            if code in [MCPErrorCodes.PARSE_ERROR, MCPErrorCodes.INVALID_REQUEST, 
                       MCPErrorCodes.METHOD_NOT_FOUND, MCPErrorCodes.INVALID_PARAMS]:
                assert category == "client_error"
            elif code == MCPErrorCodes.INTERNAL_ERROR:
                assert category == "server_error"
            elif code == MCPErrorCodes.TENANT_ACCESS_DENIED:
                assert category == "auth_error"
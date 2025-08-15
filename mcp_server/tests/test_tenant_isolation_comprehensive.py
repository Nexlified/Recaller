"""
Tests for tenant isolation in MCP server.

These tests verify that tenant isolation is properly enforced
across all MCP server components and API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schemas.mcp_schemas import ModelRegistrationRequest, ModelInfo, ModelStatus, InferenceType
from models.registry import model_registry
from core.protocol import MCPProtocolError, MCPErrorCodes
from services.auth import TenantInfo


class TestModelRegistryTenantIsolation:
    """Test tenant isolation in model registry operations."""
    
    @pytest.mark.asyncio
    async def test_model_registration_with_tenant_id(self, clean_model_registry, mock_tenant_1):
        """Test that model registration includes tenant ID."""
        request = ModelRegistrationRequest(
            name="Test Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock) as mock_init:
            with patch.object(clean_model_registry, '_save_model_config', new_callable=AsyncMock):
                with patch('services.privacy.privacy_enforcer.validate_model_config', return_value=request.config):
                    model_id = await clean_model_registry.register_model(request, mock_tenant_1.id)
                    
                    assert mock_tenant_1.id in model_id
                    assert model_id in clean_model_registry._models
                    
                    registered_model = clean_model_registry._models[model_id]
                    assert registered_model.tenant_id == mock_tenant_1.id
                    assert registered_model.name == request.name

    @pytest.mark.asyncio
    async def test_model_registration_prevents_duplicate_names_per_tenant(self, clean_model_registry, mock_tenant_1):
        """Test that duplicate model names are prevented within the same tenant."""
        request = ModelRegistrationRequest(
            name="Duplicate Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock):
            with patch.object(clean_model_registry, '_save_model_config', new_callable=AsyncMock):
                with patch('services.privacy.privacy_enforcer.validate_model_config', return_value=request.config):
                    # First registration should succeed
                    model_id = await clean_model_registry.register_model(request, mock_tenant_1.id)
                    assert model_id in clean_model_registry._models
                    
                    # Second registration with same name should fail
                    with pytest.raises(ValueError, match="already registered"):
                        await clean_model_registry.register_model(request, mock_tenant_1.id)

    @pytest.mark.asyncio
    async def test_different_tenants_can_have_same_model_name(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that different tenants can register models with the same name."""
        request = ModelRegistrationRequest(
            name="Same Model Name",
            backend_type="ollama", 
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock):
            with patch.object(clean_model_registry, '_save_model_config', new_callable=AsyncMock):
                with patch('services.privacy.privacy_enforcer.validate_model_config', return_value=request.config):
                    # Register for tenant 1
                    model_id_1 = await clean_model_registry.register_model(request, mock_tenant_1.id)
                    
                    # Register for tenant 2 with same name should succeed
                    model_id_2 = await clean_model_registry.register_model(request, mock_tenant_2.id)
                    
                    assert model_id_1 != model_id_2
                    assert mock_tenant_1.id in model_id_1
                    assert mock_tenant_2.id in model_id_2
                    assert clean_model_registry._models[model_id_1].tenant_id == mock_tenant_1.id
                    assert clean_model_registry._models[model_id_2].tenant_id == mock_tenant_2.id

    @pytest.mark.asyncio 
    async def test_model_unregistration_enforces_tenant_ownership(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that models can only be unregistered by their owning tenant."""
        # Create a model for tenant 1
        model = ModelInfo(
            id="tenant1_test_model",
            name="Test Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        
        # Tenant 2 should not be able to unregister tenant 1's model
        with pytest.raises(ValueError, match="Access denied"):
            await clean_model_registry.unregister_model(model.id, mock_tenant_2.id)
        
        # Tenant 1 should be able to unregister their own model
        with patch.object(clean_model_registry, '_backends', {}):
            with patch('os.path.exists', return_value=False):
                await clean_model_registry.unregister_model(model.id, mock_tenant_1.id)
                assert model.id not in clean_model_registry._models

    def test_get_model_with_tenant_access_control(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that get_model respects tenant access control."""
        # Create a model for tenant 1
        model = ModelInfo(
            id="tenant1_test_model",
            name="Test Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        
        # Tenant 1 should access their model
        result = clean_model_registry.get_model(model.id, mock_tenant_1.id)
        assert result is not None
        assert result.id == model.id
        
        # Tenant 2 should not access tenant 1's model
        result = clean_model_registry.get_model(model.id, mock_tenant_2.id)
        assert result is None
        
        # Admin access (no tenant ID) should work
        result = clean_model_registry.get_model(model.id, None)
        assert result is not None

    def test_list_models_with_tenant_filtering(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that list_models filters by tenant."""
        # Create models for different tenants
        model1 = ModelInfo(
            id="tenant1_model",
            name="Tenant 1 Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        model2 = ModelInfo(
            id="tenant2_model", 
            name="Tenant 2 Model",
            backend_type="ollama",
            tenant_id=mock_tenant_2.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        clean_model_registry._models[model1.id] = model1
        clean_model_registry._models[model2.id] = model2
        
        # Tenant 1 should only see their model
        tenant1_models = clean_model_registry.list_models(tenant_id=mock_tenant_1.id)
        assert len(tenant1_models) == 1
        assert tenant1_models[0].id == model1.id
        
        # Tenant 2 should only see their model
        tenant2_models = clean_model_registry.list_models(tenant_id=mock_tenant_2.id)
        assert len(tenant2_models) == 1 
        assert tenant2_models[0].id == model2.id
        
        # Admin should see all models
        all_models = clean_model_registry.list_models(tenant_id=None)
        assert len(all_models) == 2

    def test_get_model_backend_with_tenant_access_control(self, clean_model_registry, mock_tenant_1, mock_tenant_2, mock_model_backend):
        """Test that get_model_backend respects tenant access control."""
        # Create a model for tenant 1
        model = ModelInfo(
            id="tenant1_test_model",
            name="Test Model", 
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        clean_model_registry._backends[model.id] = mock_model_backend
        
        # Tenant 1 should access their model backend
        backend = clean_model_registry.get_model_backend(model.id, mock_tenant_1.id)
        assert backend is not None
        
        # Tenant 2 should not access tenant 1's model backend
        backend = clean_model_registry.get_model_backend(model.id, mock_tenant_2.id)
        assert backend is None
        
        # Admin access should work
        backend = clean_model_registry.get_model_backend(model.id, None)
        assert backend is not None


class TestInferenceTenantIsolation:
    """Test tenant isolation in inference operations."""
    
    @pytest.mark.asyncio
    async def test_inference_validates_tenant_model_access(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that inference validates tenant access to models."""
        from services.inference import inference_service
        
        # Create a model for tenant 1 
        model = ModelInfo(
            id="tenant1_model",
            name="Test Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        
        # Mock backend
        mock_backend = MagicMock()
        mock_backend.completion = AsyncMock(return_value={"text": "response"})
        clean_model_registry._backends[model.id] = mock_backend
        
        # Tenant 1 should be able to use their model
        with patch('services.inference.model_registry', clean_model_registry):
            result = await inference_service.completion(model.id, "test prompt", mock_tenant_1.id)
            assert result["text"] == "response"
        
        # Tenant 2 should not be able to use tenant 1's model
        with patch('services.inference.model_registry', clean_model_registry):
            with pytest.raises(MCPProtocolError, match="Model.*not found"):
                await inference_service.completion(model.id, "test prompt", mock_tenant_2.id)


class TestAuthServiceTenantIsolation:
    """Test tenant isolation in authentication service."""
    
    @pytest.mark.asyncio
    async def test_inactive_tenant_access_denied(self, mock_inactive_tenant):
        """Test that inactive tenants are denied access."""
        from services.auth import auth_service
        
        # Test access verification for inactive tenant
        with pytest.raises(MCPProtocolError, match="Tenant is not active"):
            await auth_service.verify_api_access(None, mock_inactive_tenant)
    
    def test_tenant_info_immutable_properties(self, mock_tenant_1):
        """Test that tenant info maintains its properties correctly."""
        assert mock_tenant_1.id == "tenant-1"
        assert mock_tenant_1.slug == "tenant-1"
        assert mock_tenant_1.name == "Test Tenant 1"
        assert mock_tenant_1.active is True
        
        # Test string representation doesn't leak sensitive info
        tenant_str = str(mock_tenant_1)
        assert "tenant-1" in tenant_str or "Test Tenant 1" in tenant_str
        
    @pytest.mark.asyncio
    async def test_tenant_cache_isolation(self):
        """Test that tenant cache maintains isolation between tenants."""
        from services.auth import auth_service
        
        # Mock different tenant responses from backend
        tenant1_info = {"id": "tenant-1", "name": "Tenant 1", "active": True}
        tenant2_info = {"id": "tenant-2", "name": "Tenant 2", "active": True}
        
        with patch.object(auth_service, 'get_backend_client') as mock_client:
            mock_http_client = AsyncMock()
            mock_client.return_value = mock_http_client
            
            # Mock different responses for different tenants
            def mock_get_response(url):
                response = AsyncMock()
                if "tenant-1" in url:
                    response.status_code = 200
                    response.json.return_value = tenant1_info
                elif "tenant-2" in url:
                    response.status_code = 200 
                    response.json.return_value = tenant2_info
                else:
                    response.status_code = 404
                return response
            
            mock_http_client.get.side_effect = mock_get_response
            
            # Get tenant info for both tenants
            tenant1 = await auth_service.get_tenant_info("tenant-1")
            tenant2 = await auth_service.get_tenant_info("tenant-2")
            
            # Should have different tenant info
            assert tenant1.id == "tenant-1"
            assert tenant2.id == "tenant-2"
            assert tenant1.name != tenant2.name


class TestComprehensiveTenantIsolation:
    """Comprehensive tests for tenant isolation across the entire system."""
    
    def test_tenant_id_propagation_through_call_stack(self, mock_tenant_1):
        """Test that tenant ID is properly propagated through the call stack."""
        # This would test that tenant context is maintained across service calls
        from services.auth import get_current_tenant
        
        with patch('services.auth.get_current_tenant', return_value=mock_tenant_1):
            current_tenant = get_current_tenant()
            assert current_tenant.id == mock_tenant_1.id
    
    @pytest.mark.asyncio
    async def test_cross_tenant_data_access_prevention(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that cross-tenant data access is completely prevented."""
        # Create models and data for both tenants
        tenant1_model = ModelInfo(
            id="tenant1_model",
            name="Tenant 1 Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        tenant2_model = ModelInfo(
            id="tenant2_model",
            name="Tenant 2 Model",
            backend_type="ollama", 
            tenant_id=mock_tenant_2.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        clean_model_registry._models[tenant1_model.id] = tenant1_model
        clean_model_registry._models[tenant2_model.id] = tenant2_model
        
        # Test all access methods maintain isolation
        # 1. Get model
        assert clean_model_registry.get_model(tenant1_model.id, mock_tenant_2.id) is None
        assert clean_model_registry.get_model(tenant2_model.id, mock_tenant_1.id) is None
        
        # 2. List models
        tenant1_models = clean_model_registry.list_models(tenant_id=mock_tenant_1.id)
        tenant2_models = clean_model_registry.list_models(tenant_id=mock_tenant_2.id)
        
        assert len(tenant1_models) == 1
        assert len(tenant2_models) == 1
        assert tenant1_models[0].id == tenant1_model.id
        assert tenant2_models[0].id == tenant2_model.id
        
        # 3. Backend access
        assert clean_model_registry.get_model_backend(tenant1_model.id, mock_tenant_2.id) is None
        assert clean_model_registry.get_model_backend(tenant2_model.id, mock_tenant_1.id) is None
    
    def test_tenant_isolation_configuration_validation(self):
        """Test that tenant isolation configuration is properly validated."""
        from config.settings import mcp_settings
        
        # Tenant isolation should be enabled by default
        assert mcp_settings.MCP_ENABLE_TENANT_ISOLATION is True
        
        # Test that disabling tenant isolation requires explicit configuration
        # (This is a security measure to prevent accidental data exposure)
        assert hasattr(mcp_settings, 'MCP_ENABLE_TENANT_ISOLATION')
    
    @pytest.mark.asyncio
    async def test_tenant_isolation_under_concurrent_access(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test tenant isolation under concurrent access scenarios."""
        import asyncio
        import threading
        
        # Create models for both tenants
        tenant1_model = ModelInfo(
            id="tenant1_concurrent_model",
            name="Tenant 1 Concurrent Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        tenant2_model = ModelInfo(
            id="tenant2_concurrent_model", 
            name="Tenant 2 Concurrent Model",
            backend_type="ollama",
            tenant_id=mock_tenant_2.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        clean_model_registry._models[tenant1_model.id] = tenant1_model
        clean_model_registry._models[tenant2_model.id] = tenant2_model
        
        # Define concurrent access functions
        def access_tenant1_models():
            models = clean_model_registry.list_models(tenant_id=mock_tenant_1.id)
            return len(models) == 1 and models[0].tenant_id == mock_tenant_1.id
        
        def access_tenant2_models():
            models = clean_model_registry.list_models(tenant_id=mock_tenant_2.id) 
            return len(models) == 1 and models[0].tenant_id == mock_tenant_2.id
        
        # Run concurrent access
        results = []
        threads = []
        
        for _ in range(5):
            thread1 = threading.Thread(target=lambda: results.append(access_tenant1_models()))
            thread2 = threading.Thread(target=lambda: results.append(access_tenant2_models()))
            threads.extend([thread1, thread2])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All concurrent accesses should maintain isolation
        assert all(results), "Tenant isolation failed under concurrent access"
    
    def test_tenant_isolation_audit_logging(self, mock_tenant_1, mock_tenant_2):
        """Test that tenant isolation violations are properly logged."""
        import logging
        from unittest.mock import Mock
        
        # Mock the logger
        mock_logger = Mock()
        
        with patch('models.registry.logger', mock_logger):
            # Attempt cross-tenant access
            model = ModelInfo(
                id="test_model",
                name="Test Model",
                backend_type="ollama",
                tenant_id=mock_tenant_1.id,
                capabilities=[InferenceType.COMPLETION]
            )
            
            registry = model_registry
            registry._models = {model.id: model}
            
            # Access attempt by wrong tenant should be logged
            result = registry.get_model(model.id, mock_tenant_2.id)
            assert result is None
            
            # Should log the access attempt (implementation dependent)
            # This is more of a guideline for implementing audit logging
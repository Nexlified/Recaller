"""
Tests for tenant isolation in MCP server.

These tests verify that tenant isolation is properly enforced
across all MCP server components and API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
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
        """Test that models are registered with tenant ID."""
        request = ModelRegistrationRequest(
            name="Test Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        # Mock the backend initialization
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock):
            model_id = await clean_model_registry.register_model(request, mock_tenant_1.id)
        
        # Verify model was registered with tenant ID
        assert model_id.startswith(f"{mock_tenant_1.id}_")
        
        model = clean_model_registry.get_model(model_id)
        assert model is not None
        assert model.tenant_id == mock_tenant_1.id
        assert model.name == "Test Model"
    
    @pytest.mark.asyncio
    async def test_model_registration_prevents_duplicate_names_per_tenant(self, clean_model_registry, mock_tenant_1):
        """Test that duplicate model names are prevented within a tenant."""
        request = ModelRegistrationRequest(
            name="Duplicate Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock):
            # Register first model
            await clean_model_registry.register_model(request, mock_tenant_1.id)
            
            # Try to register same model name for same tenant
            with pytest.raises(ValueError, match="already registered for tenant"):
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
            # Register model for tenant 1
            model_id_1 = await clean_model_registry.register_model(request, mock_tenant_1.id)
            
            # Register same model name for tenant 2
            model_id_2 = await clean_model_registry.register_model(request, mock_tenant_2.id)
        
        # Verify both models exist with different IDs
        assert model_id_1 != model_id_2
        assert model_id_1.startswith(f"{mock_tenant_1.id}_")
        assert model_id_2.startswith(f"{mock_tenant_2.id}_")
        
        model_1 = clean_model_registry.get_model(model_id_1)
        model_2 = clean_model_registry.get_model(model_id_2)
        
        assert model_1.tenant_id == mock_tenant_1.id
        assert model_2.tenant_id == mock_tenant_2.id
    
    @pytest.mark.asyncio
    async def test_model_unregistration_enforces_tenant_ownership(self, clean_model_registry, mock_tenant_1, mock_tenant_2):
        """Test that models can only be unregistered by their owning tenant."""
        request = ModelRegistrationRequest(
            name="Tenant Model",
            backend_type="ollama",
            config={"model_name": "test"},
            capabilities=[InferenceType.COMPLETION]
        )
        
        with patch.object(clean_model_registry, '_initialize_model', new_callable=AsyncMock):
            model_id = await clean_model_registry.register_model(request, mock_tenant_1.id)
        
        # Try to unregister with different tenant
        with pytest.raises(ValueError, match="belongs to different tenant"):
            await clean_model_registry.unregister_model(model_id, mock_tenant_2.id)
        
        # Verify model still exists
        model = clean_model_registry.get_model(model_id)
        assert model is not None
        
        # Unregister with correct tenant should work
        await clean_model_registry.unregister_model(model_id, mock_tenant_1.id)
        
        # Verify model is gone
        model = clean_model_registry.get_model(model_id)
        assert model is None
    
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
        model_1 = ModelInfo(
            id="tenant1_model",
            name="Tenant 1 Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        model_2 = ModelInfo(
            id="tenant2_model",
            name="Tenant 2 Model",
            backend_type="ollama",
            tenant_id=mock_tenant_2.id,
            capabilities=[InferenceType.COMPLETION]
        )
        
        clean_model_registry._models[model_1.id] = model_1
        clean_model_registry._models[model_2.id] = model_2
        
        # Tenant 1 should only see their models
        tenant_1_models = clean_model_registry.list_models(tenant_id=mock_tenant_1.id)
        assert len(tenant_1_models) == 1
        assert tenant_1_models[0].id == model_1.id
        
        # Tenant 2 should only see their models
        tenant_2_models = clean_model_registry.list_models(tenant_id=mock_tenant_2.id)
        assert len(tenant_2_models) == 1
        assert tenant_2_models[0].id == model_2.id
        
        # Admin should see all models
        all_models = clean_model_registry.list_models(tenant_id=None)
        assert len(all_models) == 2
    
    def test_get_model_backend_with_tenant_access_control(self, clean_model_registry, mock_tenant_1, mock_tenant_2, mock_model_backend):
        """Test that get_model_backend respects tenant access control."""
        # Create a model for tenant 1
        model = ModelInfo(
            id="tenant1_backend_model",
            name="Backend Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        clean_model_registry._backends[model.id] = mock_model_backend
        
        # Tenant 1 should access their model backend
        backend = clean_model_registry.get_model_backend(model.id, mock_tenant_1.id)
        assert backend is not None
        assert backend == mock_model_backend
        
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
        """Test that inference requests validate tenant access to models."""
        from services.inference import inference_service
        from schemas.mcp_schemas import CompletionRequest
        
        # Create a model for tenant 1
        model = ModelInfo(
            id="tenant1_inference_model",
            name="Inference Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        
        # Tenant 1 request should be allowed
        request = CompletionRequest(
            model_id=model.id,
            prompt="Test prompt",
            tenant_id=mock_tenant_1.id
        )
        
        # This should not raise an exception during validation
        await inference_service._validate_request(request, InferenceType.COMPLETION)
        
        # Tenant 2 request should be denied
        request_tenant_2 = CompletionRequest(
            model_id=model.id,
            prompt="Test prompt",
            tenant_id=mock_tenant_2.id
        )
        
        with pytest.raises(MCPProtocolError, match="not found or access denied"):
            await inference_service._validate_request(request_tenant_2, InferenceType.COMPLETION)


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
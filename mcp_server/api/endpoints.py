"""
MCP API endpoints for model management and inference.

This module provides REST API endpoints for the MCP server,
including model registration, discovery, and inference requests.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional, Dict, Any
import logging

try:
    from ..schemas.mcp_schemas import (
        ModelInfo, ModelRegistrationRequest, InferenceRequest,
        CompletionRequest, ChatRequest, EmbeddingRequest,
        CompletionResponse, ChatResponse, EmbeddingResponse,
        HealthCheckResponse, APIResponse, PaginatedResponse
    )
    from ..models.registry import model_registry
    from ..services.inference import inference_service
    from ..services.auth import get_current_tenant, verify_api_access
    from ..services.privacy import privacy_enforcer
    from ..core.protocol import MCPProtocolError
except ImportError:
    from schemas.mcp_schemas import (
        ModelInfo, ModelRegistrationRequest, InferenceRequest,
        CompletionRequest, ChatRequest, EmbeddingRequest,
        CompletionResponse, ChatResponse, EmbeddingResponse,
        HealthCheckResponse, APIResponse, PaginatedResponse
    )
    from models.registry import model_registry
    from services.inference import inference_service
    from services.auth import get_current_tenant, verify_api_access
    from services.privacy import privacy_enforcer
    from core.protocol import MCPProtocolError


logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Model Management Endpoints
@router.post("/models/register", response_model=APIResponse)
async def register_model(
    request: ModelRegistrationRequest,
    current_tenant = Depends(get_current_tenant)
):
    """Register a new model with the MCP server."""
    try:
        # Ensure tenant context is available
        if not current_tenant:
            raise HTTPException(status_code=403, detail="Tenant access required")
        
        model_id = await model_registry.register_model(request, current_tenant.id)
        return APIResponse(
            success=True,
            data={"model_id": model_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail="Failed to register model")


@router.delete("/models/{model_id}", response_model=APIResponse)
async def unregister_model(
    model_id: str,
    current_tenant = Depends(get_current_tenant)
):
    """Unregister a model from the MCP server."""
    try:
        # Ensure tenant context is available
        if not current_tenant:
            raise HTTPException(status_code=403, detail="Tenant access required")
        
        await model_registry.unregister_model(model_id, current_tenant.id)
        return APIResponse(success=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to unregister model {model_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unregister model")


@router.get("/models", response_model=List[ModelInfo])
async def list_models(
    status: Optional[str] = None,
    current_tenant = Depends(get_current_tenant)
):
    """List all registered models accessible by the current tenant."""
    try:
        status_filter = None
        if status:
            try:
                try:
                    from ..schemas.mcp_schemas import ModelStatus
                except ImportError:
                    from schemas.mcp_schemas import ModelStatus
                status_filter = ModelStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        # Get tenant ID for filtering (None if tenant isolation disabled)
        tenant_id = current_tenant.id if current_tenant else None
        
        models = model_registry.list_models(tenant_id=tenant_id, status_filter=status_filter)
        return models
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@router.get("/models/{model_id}", response_model=ModelInfo)
async def get_model(
    model_id: str,
    current_tenant = Depends(get_current_tenant)
):
    """Get information about a specific model."""
    # Get tenant ID for access control (None if tenant isolation disabled)
    tenant_id = current_tenant.id if current_tenant else None
    
    model = model_registry.get_model(model_id, tenant_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found or access denied")
    return model


# Inference Endpoints
@router.post("/inference/completion", response_model=CompletionResponse)
async def completion_inference(
    request: CompletionRequest,
    http_request: Request,
    current_tenant = Depends(get_current_tenant)
):
    """Perform text completion inference."""
    try:
        # Add tenant context
        request.tenant_id = current_tenant.id if current_tenant else None
        
        response = await inference_service.completion(request)
        return response
    except MCPProtocolError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Completion inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")


@router.post("/inference/chat", response_model=ChatResponse)
async def chat_inference(
    request: ChatRequest,
    http_request: Request,
    current_tenant = Depends(get_current_tenant)
):
    """Perform chat completion inference."""
    try:
        # Add tenant context
        request.tenant_id = current_tenant.id if current_tenant else None
        
        response = await inference_service.chat(request)
        return response
    except MCPProtocolError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Chat inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")


@router.post("/inference/embedding", response_model=EmbeddingResponse)
async def embedding_inference(
    request: EmbeddingRequest,
    http_request: Request,
    current_tenant = Depends(get_current_tenant)
):
    """Perform text embedding inference."""
    try:
        # Add tenant context
        request.tenant_id = current_tenant.id if current_tenant else None
        
        response = await inference_service.embedding(request)
        return response
    except MCPProtocolError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Embedding inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")


# Health Check Endpoints
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Perform health check on MCP server and models."""
    try:
        model_health = await model_registry.health_check_all()
        
        # Convert to health status objects
        try:
            from ..schemas.mcp_schemas import ModelHealthStatus, ModelStatus
        except ImportError:
            from schemas.mcp_schemas import ModelHealthStatus, ModelStatus
        model_statuses = []
        
        for model_id, is_healthy in model_health.items():
            model = model_registry.get_model(model_id)
            if model:
                status = ModelHealthStatus(
                    model_id=model_id,
                    status=ModelStatus.AVAILABLE if is_healthy else ModelStatus.ERROR
                )
                model_statuses.append(status)
        
        overall_status = "healthy" if all(model_health.values()) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            models=model_statuses
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/models/{model_id}", response_model=APIResponse)
async def model_health_check(model_id: str):
    """Perform health check on a specific model."""
    try:
        if not model_registry.get_model(model_id):
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        is_healthy = await model_registry.health_check_model(model_id)
        
        return APIResponse(
            success=True,
            data={
                "model_id": model_id,
                "healthy": is_healthy
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model health check failed for {model_id}: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Server Information Endpoints
@router.get("/info", response_model=APIResponse)
async def server_info():
    """Get MCP server information."""
    try:
        from ..config.settings import mcp_settings
        from .. import __version__
    except ImportError:
        from config.settings import mcp_settings
        import __init__
        __version__ = __init__.__version__
    
    return APIResponse(
        success=True,
        data={
            "version": __version__,
            "protocol_version": mcp_settings.MCP_PROTOCOL_VERSION,
            "server_name": "Recaller MCP Server",
            "capabilities": [
                "model_registration",
                "completion_inference",
                "chat_inference",
                "embedding_inference",
                "health_monitoring",
                "tenant_isolation"
            ]
        }
    )


# Statistics and Monitoring Endpoints
@router.get("/stats", response_model=APIResponse)
async def server_stats(current_tenant = Depends(get_current_tenant)):
    """Get server statistics and metrics scoped to current tenant."""
    try:
        # Get tenant ID for filtering (None if tenant isolation disabled)
        tenant_id = current_tenant.id if current_tenant else None
        
        models = model_registry.list_models(tenant_id=tenant_id)
        
        stats = {
            "total_models": len(models),
            "available_models": len([m for m in models if m.status.value == "available"]),
            "model_backends": {},
            "inference_types": set()
        }
        
        # Count by backend type
        for model in models:
            backend_type = model.backend_type
            stats["model_backends"][backend_type] = stats["model_backends"].get(backend_type, 0) + 1
            stats["inference_types"].update(model.capabilities)
        
        stats["inference_types"] = list(stats["inference_types"])
        
        # Add tenant info if available
        if current_tenant:
            stats["tenant_id"] = current_tenant.id
        
        return APIResponse(
            success=True,
            data=stats
        )
    except Exception as e:
        logger.error(f"Failed to get server stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Privacy Status Endpoint
@router.get("/privacy/status", response_model=APIResponse)
async def privacy_status():
    """Get privacy enforcement status and configuration."""
    try:
        status = privacy_enforcer.get_privacy_status()
        return APIResponse(
            success=True,
            data=status
        )
    except Exception as e:
        logger.error(f"Failed to get privacy status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get privacy status")

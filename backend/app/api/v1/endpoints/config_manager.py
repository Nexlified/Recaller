from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from app.core.configuration_manager import config_manager
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/configs")
def list_configurations(current_user: User = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List all available configuration files"""
    return config_manager.list_available_configs()

@router.get("/configs/{config_type}")
def get_configuration(
    config_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get specific configuration"""
    try:
        return config_manager.get_config(config_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_type}' not found")

@router.get("/configs/{config_type}/metadata")
def get_configuration_metadata(
    config_type: str,
    current_user: User = Depends(get_current_user)
) -> Optional[Dict[str, Any]]:
    """Get configuration metadata"""
    metadata = config_manager.get_config_metadata(config_type)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_type}' not found")
    return metadata.model_dump()

@router.post("/configs/reload")
def reload_configurations(current_user: User = Depends(get_current_user)) -> Dict[str, str]:
    """Reload all configurations (clear cache)"""
    config_manager.clear_cache()
    return {"message": "Configuration cache cleared successfully"}

@router.get("/configs/{config_type}/validate")
def validate_configuration(
    config_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Validate configuration structure"""
    try:
        config_data = config_manager.get_config(config_type)
        is_valid = config_manager.validate_config_structure(config_data)
        metadata = config_manager.get_config_metadata(config_type)
        return {
            "config_type": config_type,
            "valid": is_valid,
            "metadata": metadata.model_dump() if metadata else None
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_type}' not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
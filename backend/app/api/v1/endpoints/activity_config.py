from fastapi import APIRouter, Depends
from app.services.config_service import activity_config
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/activity-types")
def get_activity_types(current_user = Depends(get_current_user)):
    """Get available activity types and their configuration"""
    return activity_config.get_activity_types()

@router.get("/activity-templates")
def get_activity_templates(current_user = Depends(get_current_user)):
    """Get activity templates for quick creation"""
    return activity_config.get_activity_templates()

@router.get("/quality-scale")
def get_quality_scale(current_user = Depends(get_current_user)):
    """Get quality rating scale definitions"""
    return activity_config.get_quality_scale()

@router.get("/system-settings")
def get_system_settings(current_user = Depends(get_current_user)):
    """Get system configuration and limits"""
    config = activity_config.get_system_config()
    # Return only non-sensitive settings
    return {
        'limits': config.get('system', {}).get('limits', {}),
        'feature_flags': config.get('system', {}).get('feature_flags', {}),
        'privacy': config.get('system', {}).get('privacy', {})
    }
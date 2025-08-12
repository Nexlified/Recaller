"""Configuration API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.config_sync import ConfigSyncService
from app.schemas.config import (
    ConfigValueResponse, ConfigCategoryResponse, 
    ConfigTypeResponse, ConfigSyncRequest
)

router = APIRouter()


@router.get("/categories", response_model=List[ConfigCategoryResponse])
def get_config_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all configuration categories."""
    from app.models.config import ConfigCategory
    
    categories = db.query(ConfigCategory).filter(
        ConfigCategory.is_active == True
    ).order_by(ConfigCategory.sort_order, ConfigCategory.name).offset(skip).limit(limit).all()
    
    return categories


@router.get("/types", response_model=List[ConfigTypeResponse])
def get_config_types(
    category_key: Optional[str] = Query(None, description="Filter by category key"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get configuration types, optionally filtered by category."""
    from app.models.config import ConfigType, ConfigCategory
    
    query = db.query(ConfigType).join(ConfigCategory).filter(
        ConfigType.is_active == True,
        ConfigCategory.is_active == True
    )
    
    if category_key:
        query = query.filter(ConfigCategory.category_key == category_key)
    
    query = query.order_by(ConfigType.sort_order, ConfigType.name)
    config_types = query.offset(skip).limit(limit).all()
    
    return config_types


@router.get("/values", response_model=List[ConfigValueResponse])
def get_config_values(
    category_key: Optional[str] = Query(None, description="Filter by category key"),
    type_key: Optional[str] = Query(None, description="Filter by type key"),
    parent_id: Optional[int] = Query(None, description="Filter by parent value ID"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get configuration values with optional filtering."""
    sync_service = ConfigSyncService(db)
    
    try:
        # Use the service to get values with filtering
        all_values = sync_service.get_config_values(
            category_key=category_key, 
            type_key=type_key, 
            tenant_id=tenant_id
        )
        
        # Additional filtering for parent_id if specified
        if parent_id is not None:
            all_values = [v for v in all_values if v.get('parent_id') == parent_id]
        
        # Apply pagination
        paginated_values = all_values[skip:skip + limit]
        
        return paginated_values
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configuration values: {str(e)}")


@router.get("/values/{category_key}/{type_key}")
def get_values_by_type(
    category_key: str,
    type_key: str,
    tenant_id: Optional[int] = Query(None, description="Tenant ID for tenant-specific values"),
    db: Session = Depends(get_db)
):
    """Get configuration values for a specific category and type."""
    sync_service = ConfigSyncService(db)
    
    try:
        values = sync_service.get_config_values(
            category_key=category_key,
            type_key=type_key,
            tenant_id=tenant_id
        )
        
        if not values:
            raise HTTPException(
                status_code=404, 
                detail=f"No configuration values found for {category_key}.{type_key}"
            )
        
        return values
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configuration values: {str(e)}")


@router.post("/sync")
def sync_configurations(
    sync_request: ConfigSyncRequest,
    db: Session = Depends(get_db)
):
    """Trigger synchronization of YAML configuration files to database."""
    sync_service = ConfigSyncService(db)
    
    try:
        if sync_request.file_path:
            # Sync specific file
            from pathlib import Path
            import uuid
            
            file_path = Path(sync_request.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Configuration file not found")
            
            result = sync_service.sync_config_file(file_path, uuid.uuid4(), "api")
            return {
                "message": "Configuration file synced successfully",
                "result": result
            }
        else:
            # Sync all files
            results = sync_service.sync_all_configs("api")
            
            if results['failed'] > 0:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Sync completed with {results['failed']} failures. Check logs for details."
                )
            
            return {
                "message": "All configuration files synced successfully",
                "summary": {
                    "total_files": results['total_files'],
                    "successful": results['successful'],
                    "failed": results['failed']
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during sync: {str(e)}")


@router.get("/values/{category_key}/{type_key}/hierarchy")
def get_hierarchical_values(
    category_key: str,
    type_key: str,
    tenant_id: Optional[int] = Query(None, description="Tenant ID for tenant-specific values"),
    db: Session = Depends(get_db)
):
    """Get configuration values organized in hierarchical structure."""
    sync_service = ConfigSyncService(db)
    
    try:
        values = sync_service.get_config_values(
            category_key=category_key,
            type_key=type_key,
            tenant_id=tenant_id
        )
        
        if not values:
            raise HTTPException(
                status_code=404, 
                detail=f"No configuration values found for {category_key}.{type_key}"
            )
        
        # Organize into hierarchy
        hierarchy = []
        value_map = {v['id']: v for v in values}
        
        # Add children to their parents
        for value in values:
            value['children'] = []
        
        for value in values:
            if value['parent_id']:
                parent = value_map.get(value['parent_id'])
                if parent:
                    parent['children'].append(value)
            else:
                hierarchy.append(value)
        
        return hierarchy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hierarchical values: {str(e)}")


@router.get("/health")
def config_health_check():
    """Health check endpoint for configuration service."""
    return {"status": "healthy", "service": "configuration"}
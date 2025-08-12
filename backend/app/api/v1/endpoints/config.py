from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import config as config_crud
from app.schemas.config import (
    ConfigCategory, ConfigType, ConfigValue,
    ConfigCategoryCreate, ConfigTypeCreate, ConfigValueCreate,
    ConfigFilter, ConfigSearchRequest, ConfigHierarchyNode
)

router = APIRouter()


@router.get("/categories", response_model=List[ConfigCategory])
def get_config_categories(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve configuration categories.
    """
    categories = config_crud.get_config_categories(
        db=db, skip=skip, limit=limit, is_active=is_active
    )
    return categories


@router.get("/categories/{category_key}", response_model=ConfigCategory)
def get_config_category(
    request: Request,
    category_key: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific configuration category by key.
    """
    category = config_crud.get_config_category_by_key(db=db, category_key=category_key)
    if not category:
        raise HTTPException(status_code=404, detail="Configuration category not found")
    return category


@router.get("/types", response_model=List[ConfigType])
def get_config_types(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    category_key: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve configuration types.
    """
    types = config_crud.get_config_types(
        db=db, skip=skip, limit=limit, category_key=category_key, is_active=is_active
    )
    return types


@router.get("/types/{type_key}", response_model=ConfigType)
def get_config_type(
    request: Request,
    type_key: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific configuration type by key.
    """
    config_type = config_crud.get_config_type_by_key(db=db, type_key=type_key)
    if not config_type:
        raise HTTPException(status_code=404, detail="Configuration type not found")
    return config_type


@router.get("/types/{type_key}/values", response_model=List[ConfigValue])
def get_config_values(
    request: Request,
    type_key: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    is_active: Optional[bool] = Query(default=None),
    level: Optional[int] = Query(default=None),
    parent_value_id: Optional[int] = Query(default=None),
    tags: Optional[List[str]] = Query(default=None),
) -> Any:
    """
    Retrieve configuration values for a specific type.
    """
    # Check if type exists
    config_type = config_crud.get_config_type_by_key(db=db, type_key=type_key)
    if not config_type:
        raise HTTPException(status_code=404, detail="Configuration type not found")
    
    # Create filter
    filters = ConfigFilter(
        is_active=is_active,
        level=level,
        parent_value_id=parent_value_id,
        tags=tags
    )
    
    values = config_crud.get_config_values_by_type(
        db=db, type_key=type_key, filters=filters, skip=skip, limit=limit
    )
    return values


@router.get("/hierarchy/{type_key}", response_model=List[ConfigValue])
def get_config_hierarchy(
    request: Request,
    type_key: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get hierarchical configuration structure for a type.
    """
    # Check if type exists
    config_type = config_crud.get_config_type_by_key(db=db, type_key=type_key)
    if not config_type:
        raise HTTPException(status_code=404, detail="Configuration type not found")
    
    if config_type.data_type != 'hierarchical':
        raise HTTPException(
            status_code=400, 
            detail="Configuration type does not support hierarchy"
        )
    
    hierarchy = config_crud.get_config_hierarchy(db=db, type_key=type_key)
    return hierarchy


@router.get("/search", response_model=List[ConfigValue])
def search_config_values(
    request: Request,
    q: str = Query(..., description="Search query"),
    db: Session = Depends(deps.get_db),
    category_key: Optional[str] = None,
    type_key: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = Query(default=50, le=100),
) -> Any:
    """
    Search configuration values.
    """
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    results = config_crud.search_config_values(
        db=db,
        query_text=q,
        category_key=category_key,
        type_key=type_key,
        is_active=is_active,
        limit=limit
    )
    return results


# Admin endpoints for creating configurations (if needed)
@router.post("/categories", response_model=ConfigCategory)
def create_config_category(
    request: Request,
    category_in: ConfigCategoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    Create new configuration category.
    """
    # Check if category already exists
    existing = config_crud.get_config_category_by_key(db=db, category_key=category_in.category_key)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Configuration category with this key already exists"
        )
    
    category = config_crud.create_config_category(db=db, obj_in=category_in)
    return category


@router.post("/types", response_model=ConfigType)
def create_config_type(
    request: Request,
    type_in: ConfigTypeCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    Create new configuration type.
    """
    # Check if type already exists
    existing = config_crud.get_config_type_by_key(db=db, type_key=type_in.type_key)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Configuration type with this key already exists"
        )
    
    # Check if category exists
    category = config_crud.get_config_category(db=db, category_id=type_in.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Configuration category not found")
    
    config_type = config_crud.create_config_type(db=db, obj_in=type_in)
    return config_type


@router.post("/values", response_model=ConfigValue)
def create_config_value(
    request: Request,
    value_in: ConfigValueCreate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    Create new configuration value.
    """
    # Check if config type exists
    config_type = config_crud.get_config_type(db=db, type_id=value_in.config_type_id)
    if not config_type:
        raise HTTPException(status_code=400, detail="Configuration type not found")
    
    value = config_crud.create_config_value(db=db, obj_in=value_in)
    return value
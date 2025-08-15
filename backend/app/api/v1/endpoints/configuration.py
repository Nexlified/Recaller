from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps import get_tenant_context
from app.crud import configuration as config_crud
from app.models.user import User
from app.schemas import configuration as config_schemas

router = APIRouter()


# Configuration Categories Endpoints
@router.get("/categories", response_model=List[config_schemas.ConfigurationCategory])
def list_categories(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all configuration categories.
    """
    tenant_id = get_tenant_context(request)
    categories = config_crud.get_categories(
        db=db, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=limit, 
        active_only=active_only
    )
    return categories


@router.get("/categories/{key}", response_model=config_schemas.ConfigurationCategory)
def get_category(
    request: Request,
    key: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a configuration category by key.
    """
    tenant_id = get_tenant_context(request)
    category = config_crud.get_category_by_key(db=db, key=key, tenant_id=tenant_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Configuration category not found"
        )
    return category


@router.post("/categories", response_model=config_schemas.ConfigurationCategory)
def create_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_in: config_schemas.ConfigurationCategoryCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new configuration category.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    
    # Check if category with same key already exists
    existing_category = config_crud.get_category_by_key(
        db=db, key=category_in.key, tenant_id=tenant_id
    )
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Configuration category with this key already exists"
        )
    
    category = config_crud.create_category(
        db=db, obj_in=category_in, tenant_id=tenant_id
    )
    return category


@router.put("/categories/{key}", response_model=config_schemas.ConfigurationCategory)
def update_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    key: str,
    category_in: config_schemas.ConfigurationCategoryUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a configuration category.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    category = config_crud.get_category_by_key(db=db, key=key, tenant_id=tenant_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Configuration category not found"
        )
    
    if category.is_system:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify system configuration category"
        )
    
    category = config_crud.update_category(db=db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/categories/{key}", response_model=config_schemas.ConfigurationCategory)
def delete_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    key: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a configuration category.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    category = config_crud.delete_category(db=db, category_id=0, tenant_id=tenant_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Configuration category not found or cannot be deleted"
        )
    return category


# Configuration Types Endpoints
@router.get("/types", response_model=List[config_schemas.ConfigurationType])
def list_types(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all configuration types.
    """
    tenant_id = get_tenant_context(request)
    types = config_crud.get_types(
        db=db, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=limit,
        category_key=category,
        active_only=active_only
    )
    return types


@router.get("/types/{key}", response_model=config_schemas.ConfigurationType)
def get_type(
    request: Request,
    key: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a configuration type by key.
    """
    tenant_id = get_tenant_context(request)
    config_type = config_crud.get_type_by_key(db=db, key=key, tenant_id=tenant_id)
    if not config_type:
        raise HTTPException(
            status_code=404,
            detail="Configuration type not found"
        )
    return config_type


@router.get("/categories/{category}/types", response_model=List[config_schemas.ConfigurationType])
def get_types_by_category(
    request: Request,
    category: str,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get configuration types by category.
    """
    tenant_id = get_tenant_context(request)
    types = config_crud.get_types(
        db=db, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=limit,
        category_key=category,
        active_only=True
    )
    return types


@router.post("/types", response_model=config_schemas.ConfigurationType)
def create_type(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    type_in: config_schemas.ConfigurationTypeCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new configuration type.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    
    # Check if type with same key already exists
    existing_type = config_crud.get_type_by_key(
        db=db, key=type_in.key, tenant_id=tenant_id
    )
    if existing_type:
        raise HTTPException(
            status_code=400,
            detail="Configuration type with this key already exists"
        )
    
    # Verify category exists
    category = config_crud.get_category_by_id(
        db=db, category_id=type_in.category_id, tenant_id=tenant_id
    )
    if not category:
        raise HTTPException(
            status_code=400,
            detail="Configuration category not found"
        )
    
    config_type = config_crud.create_type(
        db=db, obj_in=type_in, tenant_id=tenant_id
    )
    return config_type


@router.put("/types/{key}", response_model=config_schemas.ConfigurationType)
def update_type(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    key: str,
    type_in: config_schemas.ConfigurationTypeUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a configuration type.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    config_type = config_crud.get_type_by_key(db=db, key=key, tenant_id=tenant_id)
    if not config_type:
        raise HTTPException(
            status_code=404,
            detail="Configuration type not found"
        )
    
    if config_type.is_system:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify system configuration type"
        )
    
    # If category_id is being updated, verify it exists
    if type_in.category_id:
        category = config_crud.get_category_by_id(
            db=db, category_id=type_in.category_id, tenant_id=tenant_id
        )
        if not category:
            raise HTTPException(
                status_code=400,
                detail="Configuration category not found"
            )
    
    config_type = config_crud.update_type(db=db, db_obj=config_type, obj_in=type_in)
    return config_type


@router.delete("/types/{key}", response_model=config_schemas.ConfigurationType)
def delete_type(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    key: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a configuration type.
    Requires superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    tenant_id = get_tenant_context(request)
    config_type = config_crud.get_type_by_key(db=db, key=key, tenant_id=tenant_id)
    if not config_type:
        raise HTTPException(
            status_code=404,
            detail="Configuration type not found"
        )
    
    deleted_type = config_crud.delete_type(
        db=db, type_id=config_type.id, tenant_id=tenant_id
    )
    if not deleted_type:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete system configuration type"
        )
    return deleted_type


# Configuration Values Endpoints
@router.get("/values", response_model=List[config_schemas.ConfigurationValue])
def list_values(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    parent_id: Optional[int] = Query(None),
    level: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List configuration values with optional filtering.
    """
    tenant_id = get_tenant_context(request)
    
    # If search or advanced filtering is needed, use search functionality
    if search or category or tags:
        search_tags = tags.split(',') if tags else None
        query = config_schemas.ConfigurationSearchQuery(
            q=search or "",
            category=category,
            type=type,
            active=active,
            tags=search_tags,
            level=level,
            parent_id=parent_id
        )
        values = config_crud.search_values(
            db=db, tenant_id=tenant_id, query=query, skip=skip, limit=limit
        )
    else:
        # Use simple listing
        values = config_crud.get_values(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            type_key=type,
            parent_id=parent_id,
            level=level,
            active_only=active if active is not None else True
        )
    
    return values


@router.get("/values/{value_id}", response_model=config_schemas.ConfigurationValue)
def get_value(
    request: Request,
    value_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a configuration value by ID.
    """
    tenant_id = get_tenant_context(request)
    value = config_crud.get_value_by_id(db=db, value_id=value_id, tenant_id=tenant_id)
    if not value:
        raise HTTPException(
            status_code=404,
            detail="Configuration value not found"
        )
    return value


@router.get("/types/{type_key}/values", response_model=List[config_schemas.ConfigurationValue])
def get_values_by_type(
    request: Request,
    type_key: str,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[int] = Query(None),
    level: Optional[int] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get configuration values by type.
    """
    tenant_id = get_tenant_context(request)
    values = config_crud.get_values(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        type_key=type_key,
        parent_id=parent_id,
        level=level,
        active_only=True
    )
    return values


@router.post("/values", response_model=config_schemas.ConfigurationValue)
def create_value(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    value_in: config_schemas.ConfigurationValueCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new configuration value.
    """
    tenant_id = get_tenant_context(request)
    
    # Verify type exists
    config_type = config_crud.get_type_by_id(
        db=db, type_id=value_in.type_id, tenant_id=tenant_id
    )
    if not config_type:
        raise HTTPException(
            status_code=400,
            detail="Configuration type not found"
        )
    
    # Verify parent exists if specified
    if value_in.parent_id:
        parent = config_crud.get_value_by_id(
            db=db, value_id=value_in.parent_id, tenant_id=tenant_id
        )
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent configuration value not found"
            )
        
        # Verify parent is of a hierarchical type
        if not parent.type.is_hierarchical:
            raise HTTPException(
                status_code=400,
                detail="Parent type does not support hierarchical values"
            )
    
    value = config_crud.create_value(
        db=db, obj_in=value_in, tenant_id=tenant_id
    )
    return value


@router.put("/values/{value_id}", response_model=config_schemas.ConfigurationValue)
def update_value(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    value_id: int,
    value_in: config_schemas.ConfigurationValueUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a configuration value.
    """
    tenant_id = get_tenant_context(request)
    value = config_crud.get_value_by_id(db=db, value_id=value_id, tenant_id=tenant_id)
    if not value:
        raise HTTPException(
            status_code=404,
            detail="Configuration value not found"
        )
    
    if value.is_system:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify system configuration value"
        )
    
    # Verify parent exists if being updated
    if value_in.parent_id:
        parent = config_crud.get_value_by_id(
            db=db, value_id=value_in.parent_id, tenant_id=tenant_id
        )
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent configuration value not found"
            )
    
    value = config_crud.update_value(db=db, db_obj=value, obj_in=value_in)
    return value


@router.delete("/values/{value_id}", response_model=config_schemas.ConfigurationValue)
def delete_value(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    value_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a configuration value.
    """
    tenant_id = get_tenant_context(request)
    deleted_value = config_crud.delete_value(
        db=db, value_id=value_id, tenant_id=tenant_id
    )
    if not deleted_value:
        raise HTTPException(
            status_code=404,
            detail="Configuration value not found or cannot be deleted"
        )
    return deleted_value


# Configuration Hierarchy Endpoints
@router.get("/hierarchy/{type_key}", response_model=List[config_schemas.ConfigurationHierarchy])
def get_hierarchy(
    request: Request,
    type_key: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get hierarchical structure for a configuration type.
    """
    tenant_id = get_tenant_context(request)
    
    # Get root level values for this type
    values = config_crud.get_values(
        db=db,
        tenant_id=tenant_id,
        type_key=type_key,
        level=0,
        active_only=True
    )
    
    def build_hierarchy(value):
        children = config_crud.get_values(
            db=db,
            tenant_id=tenant_id,
            parent_id=value.id,
            active_only=True
        )
        return config_schemas.ConfigurationHierarchy(
            id=value.id,
            key=value.key,
            display_name=value.display_name,
            level=value.level,
            parent_id=value.parent_id,
            children=[build_hierarchy(child) for child in children]
        )
    
    return [build_hierarchy(value) for value in values]


@router.get("/hierarchy/{type_key}/{parent_id}", response_model=List[config_schemas.ConfigurationValue])
def get_hierarchy_children(
    request: Request,
    type_key: str,
    parent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get children of a parent configuration value.
    """
    tenant_id = get_tenant_context(request)
    values = config_crud.get_values(
        db=db,
        tenant_id=tenant_id,
        type_key=type_key,
        parent_id=parent_id,
        active_only=True
    )
    return values


@router.get("/values/{value_id}/ancestors", response_model=List[config_schemas.ConfigurationValue])
def get_value_ancestors(
    request: Request,
    value_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all ancestors of a configuration value.
    """
    tenant_id = get_tenant_context(request)
    ancestors = config_crud.get_value_ancestors(
        db=db, value_id=value_id, tenant_id=tenant_id
    )
    return ancestors


@router.get("/values/{value_id}/descendants", response_model=List[config_schemas.ConfigurationValue])
def get_value_descendants(
    request: Request,
    value_id: int,
    db: Session = Depends(deps.get_db),
    max_depth: Optional[int] = Query(None, ge=1),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all descendants of a configuration value.
    """
    tenant_id = get_tenant_context(request)
    descendants = config_crud.get_value_descendants(
        db=db, value_id=value_id, tenant_id=tenant_id, max_depth=max_depth
    )
    return descendants


@router.post("/values/{value_id}/move", response_model=config_schemas.ConfigurationValue)
def move_value(
    request: Request,
    value_id: int,
    new_parent_id: Optional[int] = Body(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Move a configuration value to a new parent.
    """
    tenant_id = get_tenant_context(request)
    moved_value = config_crud.move_value(
        db=db, value_id=value_id, new_parent_id=new_parent_id, tenant_id=tenant_id
    )
    if not moved_value:
        raise HTTPException(
            status_code=404,
            detail="Configuration value not found"
        )
    return moved_value


# Configuration Search & Filter Endpoints
@router.get("/search", response_model=List[config_schemas.ConfigurationValue])
def search_configurations(
    request: Request,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    tags: Optional[str] = Query(None),
    level: Optional[int] = Query(None),
    parent_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search across all configurations.
    """
    tenant_id = get_tenant_context(request)
    search_tags = tags.split(',') if tags else None
    
    query = config_schemas.ConfigurationSearchQuery(
        q=q,
        category=category,
        type=type,
        active=active,
        tags=search_tags,
        level=level,
        parent_id=parent_id
    )
    
    values = config_crud.search_values(
        db=db, tenant_id=tenant_id, query=query, skip=skip, limit=limit
    )
    return values


# Configuration Translation Endpoints
@router.get("/values/{value_id}/translations", response_model=List[config_schemas.ConfigurationTranslation])
def get_value_translations(
    request: Request,
    value_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all translations for a configuration value.
    """
    tenant_id = get_tenant_context(request)
    translations = config_crud.get_translations(
        db=db, value_id=value_id, tenant_id=tenant_id
    )
    return translations


@router.get("/values/{value_id}/translations/{language_code}", response_model=config_schemas.ConfigurationTranslation)
def get_value_translation(
    request: Request,
    value_id: int,
    language_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific translation for a configuration value.
    """
    tenant_id = get_tenant_context(request)
    translation = config_crud.get_translation(
        db=db, value_id=value_id, language_code=language_code, tenant_id=tenant_id
    )
    if not translation:
        raise HTTPException(
            status_code=404,
            detail="Translation not found"
        )
    return translation


@router.post("/values/{value_id}/translations", response_model=config_schemas.ConfigurationTranslation)
def create_value_translation(
    request: Request,
    value_id: int,
    *,
    db: Session = Depends(deps.get_db),
    translation_in: config_schemas.ConfigurationTranslationCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a translation for a configuration value.
    """
    tenant_id = get_tenant_context(request)
    
    # Verify value exists
    value = config_crud.get_value_by_id(db=db, value_id=value_id, tenant_id=tenant_id)
    if not value:
        raise HTTPException(
            status_code=404,
            detail="Configuration value not found"
        )
    
    # Check if translation already exists
    existing = config_crud.get_translation(
        db=db, value_id=value_id, language_code=translation_in.language_code, tenant_id=tenant_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Translation for this language already exists"
        )
    
    translation = config_crud.create_translation(
        db=db, obj_in=translation_in, tenant_id=tenant_id
    )
    return translation


@router.put("/values/{value_id}/translations/{language_code}", response_model=config_schemas.ConfigurationTranslation)
def update_value_translation(
    request: Request,
    value_id: int,
    language_code: str,
    *,
    db: Session = Depends(deps.get_db),
    translation_in: config_schemas.ConfigurationTranslationUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a translation for a configuration value.
    """
    tenant_id = get_tenant_context(request)
    translation = config_crud.get_translation(
        db=db, value_id=value_id, language_code=language_code, tenant_id=tenant_id
    )
    if not translation:
        raise HTTPException(
            status_code=404,
            detail="Translation not found"
        )
    
    translation = config_crud.update_translation(
        db=db, db_obj=translation, obj_in=translation_in
    )
    return translation


@router.delete("/values/{value_id}/translations/{language_code}", response_model=config_schemas.ConfigurationTranslation)
def delete_value_translation(
    request: Request,
    value_id: int,
    language_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a translation for a configuration value.
    """
    tenant_id = get_tenant_context(request)
    deleted_translation = config_crud.delete_translation(
        db=db, value_id=value_id, language_code=language_code, tenant_id=tenant_id
    )
    if not deleted_translation:
        raise HTTPException(
            status_code=404,
            detail="Translation not found"
        )
    return deleted_translation


# Configuration Management Endpoints
@router.get("/health", response_model=config_schemas.ConfigurationHealth)
def get_configuration_health(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get configuration system health status.
    """
    tenant_id = get_tenant_context(request)
    
    # Get counts
    categories = config_crud.get_categories(db=db, tenant_id=tenant_id, active_only=False)
    types = config_crud.get_types(db=db, tenant_id=tenant_id, active_only=False)
    all_values = config_crud.get_values(db=db, tenant_id=tenant_id, active_only=False)
    active_values = config_crud.get_values(db=db, tenant_id=tenant_id, active_only=True)
    
    issues = []
    status = "healthy"
    
    # Basic health checks
    if len(categories) == 0:
        issues.append("No configuration categories found")
        status = "warning"
    
    if len(types) == 0:
        issues.append("No configuration types found")
        status = "warning"
    
    if len(all_values) == 0:
        issues.append("No configuration values found")
        status = "warning"
    
    if len(issues) > 2:
        status = "error"
    
    return config_schemas.ConfigurationHealth(
        status=status,
        total_categories=len(categories),
        total_types=len(types),
        total_values=len(all_values),
        active_values=len(active_values),
        inactive_values=len(all_values) - len(active_values),
        issues=issues
    )
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, text

from app.models.configuration import (
    ConfigurationCategory, 
    ConfigurationType, 
    ConfigurationValue, 
    ConfigurationTranslation
)
from app.schemas.configuration import (
    ConfigurationCategoryCreate, 
    ConfigurationCategoryUpdate,
    ConfigurationTypeCreate, 
    ConfigurationTypeUpdate,
    ConfigurationValueCreate, 
    ConfigurationValueUpdate,
    ConfigurationTranslationCreate, 
    ConfigurationTranslationUpdate,
    ConfigurationSearchQuery,
    ConfigurationFilter
)


# Configuration Category CRUD
def get_category_by_key(db: Session, key: str, tenant_id: int) -> Optional[ConfigurationCategory]:
    return db.query(ConfigurationCategory).filter(
        ConfigurationCategory.key == key,
        ConfigurationCategory.tenant_id == tenant_id
    ).first()


def get_category_by_id(db: Session, category_id: int, tenant_id: int) -> Optional[ConfigurationCategory]:
    return db.query(ConfigurationCategory).filter(
        ConfigurationCategory.id == category_id,
        ConfigurationCategory.tenant_id == tenant_id
    ).first()


def get_categories(
    db: Session, 
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[ConfigurationCategory]:
    query = db.query(ConfigurationCategory).filter(
        ConfigurationCategory.tenant_id == tenant_id
    )
    
    if active_only:
        query = query.filter(ConfigurationCategory.is_active == True)
    
    return query.order_by(ConfigurationCategory.sort_order, ConfigurationCategory.name)\
               .offset(skip).limit(limit).all()


def create_category(
    db: Session, 
    obj_in: ConfigurationCategoryCreate, 
    tenant_id: int
) -> ConfigurationCategory:
    db_obj = ConfigurationCategory(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_category(
    db: Session, 
    db_obj: ConfigurationCategory, 
    obj_in: Union[ConfigurationCategoryUpdate, Dict[str, Any]]
) -> ConfigurationCategory:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_category(db: Session, category_id: int, tenant_id: int) -> Optional[ConfigurationCategory]:
    category = get_category_by_id(db, category_id, tenant_id)
    if category and not category.is_system:
        db.delete(category)
        db.commit()
        return category
    return None


# Configuration Type CRUD
def get_type_by_key(db: Session, key: str, tenant_id: int) -> Optional[ConfigurationType]:
    return db.query(ConfigurationType).filter(
        ConfigurationType.key == key,
        ConfigurationType.tenant_id == tenant_id
    ).first()


def get_type_by_id(db: Session, type_id: int, tenant_id: int) -> Optional[ConfigurationType]:
    return db.query(ConfigurationType).filter(
        ConfigurationType.id == type_id,
        ConfigurationType.tenant_id == tenant_id
    ).first()


def get_types(
    db: Session, 
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100,
    category_key: Optional[str] = None,
    active_only: bool = True
) -> List[ConfigurationType]:
    query = db.query(ConfigurationType).options(
        joinedload(ConfigurationType.category)
    ).filter(
        ConfigurationType.tenant_id == tenant_id
    )
    
    if category_key:
        query = query.join(ConfigurationCategory).filter(
            ConfigurationCategory.key == category_key
        )
    
    if active_only:
        query = query.filter(ConfigurationType.is_active == True)
    
    return query.order_by(ConfigurationType.sort_order, ConfigurationType.name)\
               .offset(skip).limit(limit).all()


def create_type(
    db: Session, 
    obj_in: ConfigurationTypeCreate, 
    tenant_id: int
) -> ConfigurationType:
    db_obj = ConfigurationType(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_type(
    db: Session, 
    db_obj: ConfigurationType, 
    obj_in: Union[ConfigurationTypeUpdate, Dict[str, Any]]
) -> ConfigurationType:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_type(db: Session, type_id: int, tenant_id: int) -> Optional[ConfigurationType]:
    config_type = get_type_by_id(db, type_id, tenant_id)
    if config_type and not config_type.is_system:
        db.delete(config_type)
        db.commit()
        return config_type
    return None


# Configuration Value CRUD
def get_value_by_id(db: Session, value_id: int, tenant_id: int) -> Optional[ConfigurationValue]:
    return db.query(ConfigurationValue).options(
        joinedload(ConfigurationValue.type),
        joinedload(ConfigurationValue.parent),
        joinedload(ConfigurationValue.children),
        joinedload(ConfigurationValue.translations)
    ).filter(
        ConfigurationValue.id == value_id,
        ConfigurationValue.tenant_id == tenant_id
    ).first()


def get_values(
    db: Session, 
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100,
    type_key: Optional[str] = None,
    parent_id: Optional[int] = None,
    level: Optional[int] = None,
    active_only: bool = True,
    include_translations: bool = False
) -> List[ConfigurationValue]:
    query = db.query(ConfigurationValue).options(
        joinedload(ConfigurationValue.type).joinedload(ConfigurationType.category)
    )
    
    if include_translations:
        query = query.options(joinedload(ConfigurationValue.translations))
    
    query = query.filter(ConfigurationValue.tenant_id == tenant_id)
    
    if type_key:
        query = query.join(ConfigurationType).filter(
            ConfigurationType.key == type_key
        )
    
    if parent_id is not None:
        query = query.filter(ConfigurationValue.parent_id == parent_id)
    
    if level is not None:
        query = query.filter(ConfigurationValue.level == level)
    
    if active_only:
        query = query.filter(ConfigurationValue.is_active == True)
    
    return query.order_by(ConfigurationValue.sort_order, ConfigurationValue.display_name)\
               .offset(skip).limit(limit).all()


def create_value(
    db: Session, 
    obj_in: ConfigurationValueCreate, 
    tenant_id: int
) -> ConfigurationValue:
    # Calculate level and path for hierarchical values
    level = 0
    path = obj_in.key
    
    if obj_in.parent_id:
        parent = get_value_by_id(db, obj_in.parent_id, tenant_id)
        if parent:
            level = parent.level + 1
            path = f"{parent.path}/{obj_in.key}" if parent.path else obj_in.key
    
    db_obj = ConfigurationValue(
        **obj_in.model_dump(),
        level=level,
        path=path,
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_value(
    db: Session, 
    db_obj: ConfigurationValue, 
    obj_in: Union[ConfigurationValueUpdate, Dict[str, Any]]
) -> ConfigurationValue:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Handle path updates if parent_id or key changes
    if 'parent_id' in update_data or 'key' in update_data:
        new_key = update_data.get('key', db_obj.key)
        new_parent_id = update_data.get('parent_id', db_obj.parent_id)
        
        level = 0
        path = new_key
        
        if new_parent_id:
            parent = get_value_by_id(db, new_parent_id, db_obj.tenant_id)
            if parent:
                level = parent.level + 1
                path = f"{parent.path}/{new_key}" if parent.path else new_key
        
        update_data['level'] = level
        update_data['path'] = path
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_value(db: Session, value_id: int, tenant_id: int) -> Optional[ConfigurationValue]:
    value = get_value_by_id(db, value_id, tenant_id)
    if value and not value.is_system:
        db.delete(value)
        db.commit()
        return value
    return None


# Configuration Value Search and Filtering
def search_values(
    db: Session,
    tenant_id: int,
    query: ConfigurationSearchQuery,
    skip: int = 0,
    limit: int = 100
) -> List[ConfigurationValue]:
    db_query = db.query(ConfigurationValue).options(
        joinedload(ConfigurationValue.type).joinedload(ConfigurationType.category)
    ).filter(ConfigurationValue.tenant_id == tenant_id)
    
    # Text search across multiple fields
    if query.q:
        search_filter = or_(
            ConfigurationValue.key.ilike(f'%{query.q}%'),
            ConfigurationValue.display_name.ilike(f'%{query.q}%'),
            ConfigurationValue.description.ilike(f'%{query.q}%'),
            ConfigurationValue.value.ilike(f'%{query.q}%')
        )
        db_query = db_query.filter(search_filter)
    
    # Filter by category
    if query.category:
        db_query = db_query.join(ConfigurationType).join(ConfigurationCategory)\
                           .filter(ConfigurationCategory.key == query.category)
    
    # Filter by type
    if query.type:
        db_query = db_query.join(ConfigurationType)\
                           .filter(ConfigurationType.key == query.type)
    
    # Filter by active status
    if query.active is not None:
        db_query = db_query.filter(ConfigurationValue.is_active == query.active)
    
    # Filter by level
    if query.level is not None:
        db_query = db_query.filter(ConfigurationValue.level == query.level)
    
    # Filter by parent
    if query.parent_id is not None:
        db_query = db_query.filter(ConfigurationValue.parent_id == query.parent_id)
    
    # Filter by tags (JSON array contains)
    if query.tags:
        for tag in query.tags:
            db_query = db_query.filter(
                func.json_array_contains(ConfigurationValue.tags, tag)
            )
    
    return db_query.order_by(ConfigurationValue.sort_order, ConfigurationValue.display_name)\
                   .offset(skip).limit(limit).all()


def filter_values(
    db: Session,
    tenant_id: int,
    filters: ConfigurationFilter,
    skip: int = 0,
    limit: int = 100
) -> List[ConfigurationValue]:
    # Convert filter to search query for reuse
    search_query = ConfigurationSearchQuery(
        q=filters.search or "",
        category=filters.category,
        type=filters.type,
        active=filters.active,
        tags=filters.tags,
        level=filters.level,
        parent_id=filters.parent_id
    )
    return search_values(db, tenant_id, search_query, skip, limit)


# Configuration Translation CRUD
def get_translation(
    db: Session, 
    value_id: int, 
    language_code: str, 
    tenant_id: int
) -> Optional[ConfigurationTranslation]:
    return db.query(ConfigurationTranslation).filter(
        ConfigurationTranslation.value_id == value_id,
        ConfigurationTranslation.language_code == language_code,
        ConfigurationTranslation.tenant_id == tenant_id
    ).first()


def get_translations(
    db: Session, 
    value_id: int, 
    tenant_id: int
) -> List[ConfigurationTranslation]:
    return db.query(ConfigurationTranslation).filter(
        ConfigurationTranslation.value_id == value_id,
        ConfigurationTranslation.tenant_id == tenant_id
    ).order_by(ConfigurationTranslation.language_code).all()


def create_translation(
    db: Session, 
    obj_in: ConfigurationTranslationCreate, 
    tenant_id: int
) -> ConfigurationTranslation:
    db_obj = ConfigurationTranslation(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_translation(
    db: Session, 
    db_obj: ConfigurationTranslation, 
    obj_in: Union[ConfigurationTranslationUpdate, Dict[str, Any]]
) -> ConfigurationTranslation:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_translation(
    db: Session, 
    value_id: int, 
    language_code: str, 
    tenant_id: int
) -> Optional[ConfigurationTranslation]:
    translation = get_translation(db, value_id, language_code, tenant_id)
    if translation:
        db.delete(translation)
        db.commit()
        return translation
    return None


# Hierarchical operations
def get_value_ancestors(
    db: Session, 
    value_id: int, 
    tenant_id: int
) -> List[ConfigurationValue]:
    """Get all ancestors of a configuration value."""
    value = get_value_by_id(db, value_id, tenant_id)
    if not value or not value.path:
        return []
    
    # Split path and build ancestor queries
    path_parts = value.path.split('/')
    ancestors = []
    
    for i in range(len(path_parts) - 1):
        ancestor_path = '/'.join(path_parts[:i+1])
        ancestor = db.query(ConfigurationValue).filter(
            ConfigurationValue.path == ancestor_path,
            ConfigurationValue.tenant_id == tenant_id
        ).first()
        if ancestor:
            ancestors.append(ancestor)
    
    return ancestors


def get_value_descendants(
    db: Session, 
    value_id: int, 
    tenant_id: int,
    max_depth: Optional[int] = None
) -> List[ConfigurationValue]:
    """Get all descendants of a configuration value."""
    value = get_value_by_id(db, value_id, tenant_id)
    if not value:
        return []
    
    query = db.query(ConfigurationValue).filter(
        ConfigurationValue.path.like(f"{value.path}/%"),
        ConfigurationValue.tenant_id == tenant_id
    )
    
    if max_depth is not None:
        query = query.filter(ConfigurationValue.level <= value.level + max_depth)
    
    return query.order_by(ConfigurationValue.path).all()


def move_value(
    db: Session,
    value_id: int,
    new_parent_id: Optional[int],
    tenant_id: int
) -> Optional[ConfigurationValue]:
    """Move a configuration value to a new parent."""
    value = get_value_by_id(db, value_id, tenant_id)
    if not value:
        return None
    
    # Update the value with new parent
    update_data = {'parent_id': new_parent_id}
    return update_value(db, value, update_data)


# Enhanced CRUD operations for Phase 2
def get_config_values_hierarchical(
    db: Session,
    config_type_id: int,
    tenant_id: int,
    parent_id: Optional[int] = None,
    include_inactive: bool = False
) -> List[ConfigurationValue]:
    """Get configuration values in hierarchical structure"""
    query = db.query(ConfigurationValue).filter(
        and_(
            ConfigurationValue.type_id == config_type_id,
            ConfigurationValue.tenant_id == tenant_id,
            ConfigurationValue.parent_id == parent_id
        )
    )
    
    if not include_inactive:
        query = query.filter(ConfigurationValue.is_active == True)
    
    return query.order_by(ConfigurationValue.sort_order, ConfigurationValue.display_name).all()


def update_config_value_bulk(
    db: Session,
    config_type_id: int,
    tenant_id: int,
    updates: List[Dict[str, Any]]
) -> int:
    """Bulk update configuration values"""
    updated_count = 0
    
    for update_data in updates:
        value_id = update_data.get('id')
        if not value_id:
            continue
            
        value = db.query(ConfigurationValue).filter(
            and_(
                ConfigurationValue.id == value_id,
                ConfigurationValue.type_id == config_type_id,
                ConfigurationValue.tenant_id == tenant_id
            )
        ).first()
        
        if value:
            for field, new_value in update_data.items():
                if field != 'id' and hasattr(value, field):
                    setattr(value, field, new_value)
            updated_count += 1
    
    db.commit()
    return updated_count


def get_config_statistics(db: Session, tenant_id: int) -> Dict[str, Any]:
    """Get configuration statistics for tenant"""
    from app.models.configuration import ConfigurationImport
    
    stats = {
        'categories': db.query(ConfigurationCategory).filter(
            ConfigurationCategory.tenant_id == tenant_id
        ).count(),
        'types': db.query(ConfigurationType).filter(
            ConfigurationType.tenant_id == tenant_id
        ).count(),
        'values': db.query(ConfigurationValue).filter(
            ConfigurationValue.tenant_id == tenant_id
        ).count(),
        'active_values': db.query(ConfigurationValue).filter(
            and_(
                ConfigurationValue.tenant_id == tenant_id,
                ConfigurationValue.is_active == True
            )
        ).count(),
        'imports': db.query(ConfigurationImport).filter(
            ConfigurationImport.tenant_id == tenant_id
        ).count(),
        'successful_imports': db.query(ConfigurationImport).filter(
            and_(
                ConfigurationImport.tenant_id == tenant_id,
                ConfigurationImport.import_status == 'success'
            )
        ).count()
    }
    
    return stats
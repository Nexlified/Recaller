from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.config import ConfigCategory, ConfigType, ConfigValue
from app.schemas.config import (
    ConfigCategoryCreate, ConfigCategoryUpdate,
    ConfigTypeCreate, ConfigTypeUpdate,
    ConfigValueCreate, ConfigValueUpdate,
    ConfigFilter
)


# Configuration Category CRUD
def get_config_category(db: Session, category_id: int) -> Optional[ConfigCategory]:
    return db.query(ConfigCategory).filter(ConfigCategory.id == category_id).first()


def get_config_category_by_key(db: Session, category_key: str) -> Optional[ConfigCategory]:
    return db.query(ConfigCategory).filter(ConfigCategory.category_key == category_key).first()


def get_config_categories(
    db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[ConfigCategory]:
    query = db.query(ConfigCategory)
    if is_active is not None:
        query = query.filter(ConfigCategory.is_active == is_active)
    return query.order_by(ConfigCategory.sort_order, ConfigCategory.name).offset(skip).limit(limit).all()


def create_config_category(db: Session, obj_in: ConfigCategoryCreate) -> ConfigCategory:
    db_obj = ConfigCategory(
        category_key=obj_in.category_key,
        name=obj_in.name,
        description=obj_in.description,
        sort_order=obj_in.sort_order,
        is_active=obj_in.is_active,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_config_category(
    db: Session, db_obj: ConfigCategory, obj_in: Union[ConfigCategoryUpdate, Dict[str, Any]]
) -> ConfigCategory:
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


# Configuration Type CRUD
def get_config_type(db: Session, type_id: int) -> Optional[ConfigType]:
    return db.query(ConfigType).filter(ConfigType.id == type_id).first()


def get_config_type_by_key(db: Session, type_key: str) -> Optional[ConfigType]:
    return db.query(ConfigType).filter(ConfigType.type_key == type_key).first()


def get_config_types(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_key: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[ConfigType]:
    query = db.query(ConfigType)
    
    if category_key:
        query = query.join(ConfigCategory).filter(ConfigCategory.category_key == category_key)
    
    if is_active is not None:
        query = query.filter(ConfigType.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def create_config_type(db: Session, obj_in: ConfigTypeCreate) -> ConfigType:
    db_obj = ConfigType(
        type_key=obj_in.type_key,
        name=obj_in.name,
        description=obj_in.description,
        data_type=obj_in.data_type,
        max_level=obj_in.max_level,
        allows_custom_values=obj_in.allows_custom_values,
        category_id=obj_in.category_id,
        is_active=obj_in.is_active,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# Configuration Value CRUD
def get_config_value(db: Session, value_id: int) -> Optional[ConfigValue]:
    return db.query(ConfigValue).filter(ConfigValue.id == value_id).first()


def get_config_values_by_type(
    db: Session,
    type_key: str,
    filters: Optional[ConfigFilter] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ConfigValue]:
    query = db.query(ConfigValue).join(ConfigType).filter(ConfigType.type_key == type_key)
    
    if filters:
        if filters.is_active is not None:
            query = query.filter(ConfigValue.is_active == filters.is_active)
        if filters.level is not None:
            query = query.filter(ConfigValue.level == filters.level)
        if filters.parent_value_id is not None:
            query = query.filter(ConfigValue.parent_value_id == filters.parent_value_id)
        if filters.tags:
            # Filter by tags (assuming tags are stored as JSON array)
            for tag in filters.tags:
                query = query.filter(func.json_extract(ConfigValue.tags, f'$[*]').like(f'%{tag}%'))
    
    return query.order_by(ConfigValue.sort_order, ConfigValue.display_name).offset(skip).limit(limit).all()


def get_config_hierarchy(db: Session, type_key: str) -> List[ConfigValue]:
    """Get hierarchical configuration values with children loaded"""
    return db.query(ConfigValue).join(ConfigType).filter(
        ConfigType.type_key == type_key,
        ConfigValue.parent_value_id.is_(None),
        ConfigValue.is_active == True
    ).order_by(ConfigValue.sort_order, ConfigValue.display_name).all()


def search_config_values(
    db: Session,
    query_text: str,
    category_key: Optional[str] = None,
    type_key: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = 50
) -> List[ConfigValue]:
    """Search configuration values by display name or description"""
    query = db.query(ConfigValue).join(ConfigType).join(ConfigCategory)
    
    # Search in display_name and description
    search_filter = or_(
        ConfigValue.display_name.ilike(f'%{query_text}%'),
        ConfigValue.description.ilike(f'%{query_text}%'),
        ConfigValue.value_key.ilike(f'%{query_text}%')
    )
    query = query.filter(search_filter)
    
    if category_key:
        query = query.filter(ConfigCategory.category_key == category_key)
    
    if type_key:
        query = query.filter(ConfigType.type_key == type_key)
    
    if is_active is not None:
        query = query.filter(ConfigValue.is_active == is_active)
    
    return query.order_by(ConfigValue.display_name).limit(limit).all()


def create_config_value(db: Session, obj_in: ConfigValueCreate) -> ConfigValue:
    db_obj = ConfigValue(
        config_type_id=obj_in.config_type_id,
        value_key=obj_in.value_key,
        display_name=obj_in.display_name,
        description=obj_in.description,
        sort_order=obj_in.sort_order,
        level=obj_in.level,
        parent_value_id=obj_in.parent_value_id,
        metadata=obj_in.extra_data,
        tags=obj_in.tags,
        is_active=obj_in.is_active,
        is_system=obj_in.is_system,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_config_value(
    db: Session, db_obj: ConfigValue, obj_in: Union[ConfigValueUpdate, Dict[str, Any]]
) -> ConfigValue:
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
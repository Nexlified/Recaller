"""CRUD operations for configuration management"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.config import (
    ConfigCategory,
    ConfigType,
    ConfigValue,
    ConfigValueTranslation,
    ConfigValueDependency,
    ConfigSyncHistory,
    ConfigChangeLog,
    ConfigUsageStats,
)


class CRUDConfigCategory:
    """CRUD operations for ConfigCategory"""
    
    def get(self, db: Session, id: int) -> Optional[ConfigCategory]:
        return db.query(ConfigCategory).filter(ConfigCategory.id == id).first()
    
    def get_by_key(self, db: Session, category_key: str) -> Optional[ConfigCategory]:
        return db.query(ConfigCategory).filter(ConfigCategory.category_key == category_key).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ConfigCategory]:
        return db.query(ConfigCategory).filter(ConfigCategory.is_active == True).order_by(ConfigCategory.sort_order).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, category_key: str, name: str, **kwargs) -> ConfigCategory:
        db_obj = ConfigCategory(category_key=category_key, name=name, **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDConfigType:
    """CRUD operations for ConfigType"""
    
    def get(self, db: Session, id: int) -> Optional[ConfigType]:
        return db.query(ConfigType).filter(ConfigType.id == id).first()
    
    def get_by_key(self, db: Session, type_key: str, category_id: int) -> Optional[ConfigType]:
        return db.query(ConfigType).filter(
            ConfigType.type_key == type_key,
            ConfigType.category_id == category_id
        ).first()
    
    def get_by_category(self, db: Session, category_id: int) -> List[ConfigType]:
        return db.query(ConfigType).filter(
            ConfigType.category_id == category_id,
            ConfigType.is_active == True
        ).order_by(ConfigType.sort_order).all()
    
    def create(self, db: Session, *, category_id: int, type_key: str, name: str, **kwargs) -> ConfigType:
        db_obj = ConfigType(category_id=category_id, type_key=type_key, name=name, **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDConfigValue:
    """CRUD operations for ConfigValue"""
    
    def get(self, db: Session, id: int) -> Optional[ConfigValue]:
        return db.query(ConfigValue).filter(ConfigValue.id == id).first()
    
    def get_by_key(self, db: Session, value_key: str, config_type_id: int, tenant_id: Optional[int] = None) -> Optional[ConfigValue]:
        return db.query(ConfigValue).filter(
            ConfigValue.value_key == value_key,
            ConfigValue.config_type_id == config_type_id,
            ConfigValue.tenant_id == tenant_id
        ).first()
    
    def get_by_type(self, db: Session, config_type_id: int, tenant_id: Optional[int] = None) -> List[ConfigValue]:
        query = db.query(ConfigValue).filter(
            ConfigValue.config_type_id == config_type_id,
            ConfigValue.is_active == True
        )
        if tenant_id is not None:
            query = query.filter(ConfigValue.tenant_id == tenant_id)
        return query.order_by(ConfigValue.sort_order).all()
    
    def get_hierarchical(self, db: Session, config_type_id: int, parent_id: Optional[int] = None, tenant_id: Optional[int] = None) -> List[ConfigValue]:
        query = db.query(ConfigValue).filter(
            ConfigValue.config_type_id == config_type_id,
            ConfigValue.parent_value_id == parent_id,
            ConfigValue.is_active == True
        )
        if tenant_id is not None:
            query = query.filter(ConfigValue.tenant_id == tenant_id)
        return query.order_by(ConfigValue.sort_order).all()
    
    def create(self, db: Session, *, config_type_id: int, value_key: str, display_name: str, tenant_id: Optional[int] = None, **kwargs) -> ConfigValue:
        db_obj = ConfigValue(
            config_type_id=config_type_id,
            value_key=value_key,
            display_name=display_name,
            tenant_id=tenant_id,
            **kwargs
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instances
config_category = CRUDConfigCategory()
config_type = CRUDConfigType()
config_value = CRUDConfigValue()
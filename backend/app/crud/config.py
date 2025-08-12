from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.config import ConfigType, ConfigValue, ConfigSyncSession, ConfigChange
from app.schemas.config import (
    ConfigTypeCreate, 
    ConfigTypeUpdate,
    ConfigValueCreate, 
    ConfigValueUpdate,
    ConfigSyncSessionCreate,
    ConfigSyncSessionUpdate,
    ConfigChangeCreate
)


class CRUDConfigType:
    def get(self, db: Session, id: int, tenant_id: int) -> Optional[ConfigType]:
        return db.query(ConfigType).filter(
            and_(ConfigType.id == id, ConfigType.tenant_id == tenant_id)
        ).first()

    def get_by_name(self, db: Session, name: str, tenant_id: int) -> Optional[ConfigType]:
        return db.query(ConfigType).filter(
            and_(ConfigType.name == name, ConfigType.tenant_id == tenant_id)
        ).first()

    def get_multi(self, db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[ConfigType]:
        return db.query(ConfigType).filter(
            ConfigType.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: ConfigTypeCreate, tenant_id: int) -> ConfigType:
        db_obj = ConfigType(
            tenant_id=tenant_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ConfigType, obj_in: ConfigTypeUpdate) -> ConfigType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int, tenant_id: int) -> ConfigType:
        obj = db.query(ConfigType).filter(
            and_(ConfigType.id == id, ConfigType.tenant_id == tenant_id)
        ).first()
        db.delete(obj)
        db.commit()
        return obj


class CRUDConfigValue:
    def get(self, db: Session, id: int, tenant_id: int) -> Optional[ConfigValue]:
        return db.query(ConfigValue).filter(
            and_(ConfigValue.id == id, ConfigValue.tenant_id == tenant_id)
        ).first()

    def get_by_key(self, db: Session, key: str, config_type_id: int, tenant_id: int) -> Optional[ConfigValue]:
        return db.query(ConfigValue).filter(
            and_(
                ConfigValue.key == key, 
                ConfigValue.config_type_id == config_type_id,
                ConfigValue.tenant_id == tenant_id
            )
        ).first()

    def get_by_config_type(self, db: Session, config_type_id: int, tenant_id: int) -> List[ConfigValue]:
        return db.query(ConfigValue).filter(
            and_(
                ConfigValue.config_type_id == config_type_id,
                ConfigValue.tenant_id == tenant_id
            )
        ).all()

    def get_multi(self, db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[ConfigValue]:
        return db.query(ConfigValue).filter(
            ConfigValue.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: ConfigValueCreate, tenant_id: int) -> ConfigValue:
        db_obj = ConfigValue(
            tenant_id=tenant_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ConfigValue, obj_in: ConfigValueUpdate) -> ConfigValue:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int, tenant_id: int) -> ConfigValue:
        obj = db.query(ConfigValue).filter(
            and_(ConfigValue.id == id, ConfigValue.tenant_id == tenant_id)
        ).first()
        db.delete(obj)
        db.commit()
        return obj


class CRUDConfigSyncSession:
    def get(self, db: Session, id: int, tenant_id: int) -> Optional[ConfigSyncSession]:
        return db.query(ConfigSyncSession).filter(
            and_(ConfigSyncSession.id == id, ConfigSyncSession.tenant_id == tenant_id)
        ).first()

    def get_by_session_id(self, db: Session, session_id: str, tenant_id: int) -> Optional[ConfigSyncSession]:
        return db.query(ConfigSyncSession).filter(
            and_(ConfigSyncSession.session_id == session_id, ConfigSyncSession.tenant_id == tenant_id)
        ).first()

    def get_multi(self, db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[ConfigSyncSession]:
        return db.query(ConfigSyncSession).filter(
            ConfigSyncSession.tenant_id == tenant_id
        ).order_by(ConfigSyncSession.started_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: ConfigSyncSessionCreate, tenant_id: int) -> ConfigSyncSession:
        db_obj = ConfigSyncSession(
            tenant_id=tenant_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ConfigSyncSession, obj_in: ConfigSyncSessionUpdate) -> ConfigSyncSession:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDConfigChange:
    def get_by_session(self, db: Session, sync_session_id: int, tenant_id: int) -> List[ConfigChange]:
        return db.query(ConfigChange).filter(
            and_(
                ConfigChange.sync_session_id == sync_session_id,
                ConfigChange.tenant_id == tenant_id
            )
        ).all()

    def create(self, db: Session, obj_in: ConfigChangeCreate, tenant_id: int) -> ConfigChange:
        db_obj = ConfigChange(
            tenant_id=tenant_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instances
config_type = CRUDConfigType()
config_value = CRUDConfigValue()
config_sync_session = CRUDConfigSyncSession()
config_change = CRUDConfigChange()
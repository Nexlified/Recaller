from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


# Base schemas
class ConfigTypeBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    schema_version: str = "1.0"
    is_active: bool = True


class ConfigTypeCreate(ConfigTypeBase):
    config_file_path: Optional[str] = None


class ConfigTypeUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    schema_version: Optional[str] = None
    is_active: Optional[bool] = None
    config_file_path: Optional[str] = None


class ConfigType(ConfigTypeBase):
    id: int
    tenant_id: int
    last_sync_at: Optional[datetime] = None
    last_sync_checksum: Optional[str] = None
    config_file_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Config Value schemas
class ConfigValueBase(BaseModel):
    key: str
    display_name: str
    description: Optional[str] = None
    parent_value_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True
    is_system: bool = False
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigValueCreate(ConfigValueBase):
    config_type_id: int


class ConfigValueUpdate(BaseModel):
    key: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    parent_value_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigValue(ConfigValueBase):
    id: int
    tenant_id: int
    config_type_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sync Session schemas
class ConfigSyncSessionBase(BaseModel):
    session_id: str
    status: str
    sync_type: str
    files_processed: int = 0
    changes_made: int = 0
    errors_count: int = 0
    error_details: Optional[Dict[str, Any]] = None


class ConfigSyncSessionCreate(ConfigSyncSessionBase):
    pass


class ConfigSyncSessionUpdate(BaseModel):
    status: Optional[str] = None
    files_processed: Optional[int] = None
    changes_made: Optional[int] = None
    errors_count: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None


class ConfigSyncSession(ConfigSyncSessionBase):
    id: int
    tenant_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Config Change schemas
class ConfigChangeBase(BaseModel):
    change_type: str  # 'create', 'update', 'delete'
    table_name: str
    record_id: Optional[int] = None
    field_name: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    config_file_path: Optional[str] = None


class ConfigChangeCreate(ConfigChangeBase):
    sync_session_id: int


class ConfigChange(ConfigChangeBase):
    id: int
    tenant_id: int
    sync_session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Sync Result schemas for API responses
class FileSyncResult(BaseModel):
    file_path: str
    status: str  # 'success', 'error', 'no_changes'
    changes_count: int = 0
    error_message: Optional[str] = None
    changes: List[str] = []


class SyncResult(BaseModel):
    session_id: str
    status: str  # 'completed', 'failed', 'partial'
    files_processed: int
    total_changes: int
    errors_count: int
    file_results: List[FileSyncResult] = []
    error_details: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# YAML Configuration schemas (for validation)
class YAMLConfigValue(BaseModel):
    key: str
    display_name: str
    description: Optional[str] = None
    parent_key: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class YAMLConfigFile(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    version: str = "1.0"
    values: List[YAMLConfigValue]
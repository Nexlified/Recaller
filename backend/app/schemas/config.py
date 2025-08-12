"""Pydantic schemas for configuration management"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# Base Schemas
class ConfigCategoryBase(BaseModel):
    category_key: str
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    icon: Optional[str] = None
    color: Optional[str] = None
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigCategoryCreate(ConfigCategoryBase):
    pass


class ConfigCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigCategory(ConfigCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# Config Type Schemas
class ConfigTypeBase(BaseModel):
    type_key: str
    name: str
    description: Optional[str] = None
    data_type: str = "enum"
    max_level: int = 1
    allows_custom_values: bool = False
    sort_order: int = 0
    is_active: bool = True
    is_system: bool = False
    source_file: Optional[str] = None
    sync_version: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigTypeCreate(ConfigTypeBase):
    category_id: int


class ConfigTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    max_level: Optional[int] = None
    allows_custom_values: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    source_file: Optional[str] = None
    sync_version: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    config_metadata: Optional[Dict[str, Any]] = None


class ConfigType(ConfigTypeBase):
    id: int
    category_id: int
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# Config Value Schemas
class ConfigValueBase(BaseModel):
    value_key: str
    display_name: str
    description: Optional[str] = None
    hierarchy_path: Optional[str] = None
    level: int = 1
    has_children: bool = False
    children_count: int = 0
    value_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_properties: Optional[Dict[str, Any]] = None
    sort_order: int = 0
    is_active: bool = True
    is_system: bool = False
    is_custom: bool = False
    source_file: Optional[str] = None
    sync_version: Optional[str] = None


class ConfigValueCreate(ConfigValueBase):
    config_type_id: int
    tenant_id: Optional[int] = None
    parent_value_id: Optional[int] = None
    created_by: Optional[int] = None


class ConfigValueUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    hierarchy_path: Optional[str] = None
    has_children: Optional[bool] = None
    children_count: Optional[int] = None
    value_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_properties: Optional[Dict[str, Any]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    source_file: Optional[str] = None
    sync_version: Optional[str] = None
    updated_by: Optional[int] = None


class ConfigValue(ConfigValueBase):
    id: int
    config_type_id: int
    tenant_id: Optional[int] = None
    parent_value_id: Optional[int] = None
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = {"from_attributes": True}


# Config Value Translation Schemas
class ConfigValueTranslationBase(BaseModel):
    language_code: str
    display_name: str
    description: Optional[str] = None
    translation_quality: str = "manual"
    last_reviewed_at: Optional[datetime] = None


class ConfigValueTranslationCreate(ConfigValueTranslationBase):
    config_value_id: int
    translated_by: Optional[int] = None


class ConfigValueTranslationUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    translation_quality: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None


class ConfigValueTranslation(ConfigValueTranslationBase):
    id: int
    config_value_id: int
    translated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# Config Value Dependency Schemas
class ConfigValueDependencyBase(BaseModel):
    dependency_type: str
    description: Optional[str] = None
    dependency_metadata: Optional[Dict[str, Any]] = None


class ConfigValueDependencyCreate(ConfigValueDependencyBase):
    source_value_id: int
    target_value_id: int


class ConfigValueDependency(ConfigValueDependencyBase):
    id: int
    source_value_id: int
    target_value_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Config Sync History Schemas
class ConfigSyncHistoryBase(BaseModel):
    source_file: str
    sync_action: str
    sync_status: str
    changes_summary: Optional[Dict[str, Any]] = None
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_deleted: int = 0
    records_skipped: int = 0
    errors: Optional[Dict[str, Any]] = None
    warnings: Optional[Dict[str, Any]] = None
    source_version: Optional[str] = None
    target_version: Optional[str] = None
    checksum: Optional[str] = None
    duration_ms: Optional[int] = None
    memory_usage_mb: Optional[int] = None
    triggered_by: Optional[str] = None
    execution_context: Optional[Dict[str, Any]] = None


class ConfigSyncHistoryCreate(ConfigSyncHistoryBase):
    config_type_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None


class ConfigSyncHistory(ConfigSyncHistoryBase):
    id: int
    sync_session_id: str
    config_type_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None
    executed_at: datetime
    
    model_config = {"from_attributes": True}


# Config Usage Stats Schemas
class ConfigUsageStatsBase(BaseModel):
    usage_count: int = 0
    context_type: Optional[str] = None
    context_count: int = 0
    daily_usage: int = 0
    weekly_usage: int = 0
    monthly_usage: int = 0


class ConfigUsageStatsCreate(ConfigUsageStatsBase):
    config_value_id: int
    tenant_id: Optional[int] = None


class ConfigUsageStatsUpdate(ConfigUsageStatsBase):
    usage_count: Optional[int] = None
    context_count: Optional[int] = None
    daily_usage: Optional[int] = None
    weekly_usage: Optional[int] = None
    monthly_usage: Optional[int] = None


class ConfigUsageStats(ConfigUsageStatsBase):
    id: int
    config_value_id: int
    tenant_id: Optional[int] = None
    last_used_at: Optional[datetime] = None
    first_used_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
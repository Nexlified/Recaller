"""Pydantic schemas for configuration management."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ConfigCategoryBase(BaseModel):
    category_key: str
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class ConfigCategoryResponse(ConfigCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigTypeBase(BaseModel):
    type_key: str
    name: str
    description: Optional[str] = None
    data_type: str = "enum"
    sort_order: int = 0
    is_active: bool = True


class ConfigTypeResponse(ConfigTypeBase):
    id: int
    category_id: int
    source_file: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    sync_version: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigValueBase(BaseModel):
    value_key: str
    display_name: str
    description: Optional[str] = None
    parent_value_id: Optional[int] = None
    hierarchy_path: Optional[str] = None
    level: int = 1
    extra_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    sort_order: int = 0
    is_active: bool = True
    is_system: bool = False


class ConfigValueResponse(ConfigValueBase):
    id: int
    tenant_id: Optional[int] = None
    config_type_id: int
    source_file: Optional[str] = None
    sync_version: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigSyncRequest(BaseModel):
    file_path: Optional[str] = None  # If not provided, sync all files
    dry_run: bool = False


class ConfigSyncResponse(BaseModel):
    sync_session_id: str
    total_files: int
    successful: int
    failed: int
    files: List[Dict[str, Any]]


class ConfigValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
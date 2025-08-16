from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Configuration Category Schemas
class ConfigurationCategoryBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)


class ConfigurationCategoryCreate(ConfigurationCategoryBase):
    is_system: bool = Field(default=False)


class ConfigurationCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ConfigurationCategory(ConfigurationCategoryBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Configuration Type Schemas
class ConfigurationTypeBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: int = Field(..., gt=0)
    data_type: str = Field(default="string", pattern="^(string|number|boolean|json)$")
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    is_hierarchical: bool = Field(default=False)
    is_translatable: bool = Field(default=False)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, ge=0)


class ConfigurationTypeCreate(ConfigurationTypeBase):
    is_system: bool = Field(default=False)


class ConfigurationTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = Field(None, gt=0)
    data_type: Optional[str] = Field(None, pattern="^(string|number|boolean|json)$")
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    is_hierarchical: Optional[bool] = None
    is_translatable: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ConfigurationType(ConfigurationTypeBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime]
    category: Optional[ConfigurationCategory] = None
    
    class Config:
        from_attributes = True


# Configuration Value Schemas
class ConfigurationValueBase(BaseModel):
    type_id: int = Field(..., gt=0)
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = Field(None, gt=0)
    value_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)


class ConfigurationValueCreate(ConfigurationValueBase):
    is_system: bool = Field(default=False)
    source: Optional[str] = Field(default="manual")
    source_version: Optional[str] = None
    import_id: Optional[int] = None


class ConfigurationValueUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[str] = Field(None, min_length=1)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = Field(None, gt=0)
    value_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ConfigurationValue(ConfigurationValueBase):
    id: int
    level: int
    path: Optional[str]
    is_system: bool
    source: Optional[str] = None
    source_version: Optional[str] = None
    import_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]
    type: Optional[ConfigurationType] = None
    parent: Optional['ConfigurationValue'] = None
    children: Optional[List['ConfigurationValue']] = None
    
    class Config:
        from_attributes = True


# Configuration Translation Schemas
class ConfigurationTranslationBase(BaseModel):
    language_code: str = Field(..., min_length=2, max_length=5)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ConfigurationTranslationCreate(ConfigurationTranslationBase):
    value_id: int = Field(..., gt=0)


class ConfigurationTranslationUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ConfigurationTranslation(ConfigurationTranslationBase):
    id: int
    value_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Advanced Query Schemas
class ConfigurationSearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    type: Optional[str] = None
    active: Optional[bool] = None
    tags: Optional[List[str]] = None
    level: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = Field(None, gt=0)


class ConfigurationFilter(BaseModel):
    category: Optional[str] = None
    type: Optional[str] = None
    active: Optional[bool] = None
    tags: Optional[List[str]] = None
    level: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = Field(None, gt=0)
    search: Optional[str] = None


class ConfigurationHierarchy(BaseModel):
    id: int
    key: str
    display_name: str
    level: int
    parent_id: Optional[int]
    children: List['ConfigurationHierarchy'] = []
    
    class Config:
        from_attributes = True


# Bulk Operation Schemas
class ConfigurationValueBulkCreate(BaseModel):
    values: List[ConfigurationValueCreate] = Field(..., min_items=1, max_items=100)


class ConfigurationValueBulkUpdate(BaseModel):
    updates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)


# Configuration Management Schemas
class ConfigurationSyncStatus(BaseModel):
    is_syncing: bool
    last_sync: Optional[datetime]
    total_items: int
    synced_items: int
    failed_items: int
    errors: List[str] = []


class ConfigurationValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class ConfigurationHealth(BaseModel):
    status: str = Field(..., pattern="^(healthy|warning|error)$")
    total_categories: int
    total_types: int
    total_values: int
    active_values: int
    inactive_values: int
    issues: List[str] = []


# Update forward references for self-referencing models
ConfigurationValue.model_rebuild()
ConfigurationHierarchy.model_rebuild()
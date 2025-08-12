from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# Configuration Category Schemas
class ConfigCategoryBase(BaseModel):
    category_key: str
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True


class ConfigCategoryCreate(ConfigCategoryBase):
    pass


class ConfigCategoryUpdate(ConfigCategoryBase):
    category_key: Optional[str] = None
    name: Optional[str] = None


class ConfigCategoryInDBBase(ConfigCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConfigCategory(ConfigCategoryInDBBase):
    pass


# Configuration Type Schemas
class ConfigTypeBase(BaseModel):
    type_key: str
    name: str
    description: Optional[str] = None
    data_type: str  # 'enum', 'hierarchical', 'key_value'
    max_level: Optional[int] = 1
    allows_custom_values: Optional[bool] = False
    category_id: int
    is_active: Optional[bool] = True


class ConfigTypeCreate(ConfigTypeBase):
    pass


class ConfigTypeUpdate(ConfigTypeBase):
    type_key: Optional[str] = None
    name: Optional[str] = None
    data_type: Optional[str] = None
    category_id: Optional[int] = None


class ConfigTypeInDBBase(ConfigTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConfigType(ConfigTypeInDBBase):
    category: Optional[ConfigCategory] = None
    values: Optional[List["ConfigValue"]] = None


# Configuration Value Schemas
class ConfigValueBase(BaseModel):
    config_type_id: int
    value_key: str
    display_name: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    level: Optional[int] = 1
    parent_value_id: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = True
    is_system: Optional[bool] = False


class ConfigValueCreate(ConfigValueBase):
    pass


class ConfigValueUpdate(ConfigValueBase):
    config_type_id: Optional[int] = None
    value_key: Optional[str] = None
    display_name: Optional[str] = None


class ConfigValueInDBBase(ConfigValueBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConfigValue(ConfigValueInDBBase):
    config_type: Optional[ConfigType] = None
    parent: Optional["ConfigValue"] = None
    children: Optional[List["ConfigValue"]] = None


# Filter and Search Schemas
class ConfigFilter(BaseModel):
    category_key: Optional[str] = None
    is_active: Optional[bool] = None
    level: Optional[int] = None
    parent_value_id: Optional[int] = None
    tags: Optional[List[str]] = None


class ConfigSearchRequest(BaseModel):
    query: str
    category_key: Optional[str] = None
    type_key: Optional[str] = None
    is_active: Optional[bool] = True
    limit: Optional[int] = 50


# Hierarchy Response
class ConfigHierarchyNode(BaseModel):
    id: int
    value_key: str
    display_name: str
    description: Optional[str] = None
    level: int
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    children: Optional[List["ConfigHierarchyNode"]] = None


# Update forward references
ConfigValue.model_rebuild()
ConfigHierarchyNode.model_rebuild()
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime


class OrganizationLocationBase(BaseModel):
    location_name: Optional[str] = None
    location_type: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    employee_count: Optional[int] = None
    is_primary: Optional[bool] = False


class OrganizationLocationCreate(OrganizationLocationBase):
    pass


class OrganizationLocationUpdate(OrganizationLocationBase):
    pass


class OrganizationLocation(OrganizationLocationBase):
    id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationAliasBase(BaseModel):
    alias_name: str
    alias_type: Optional[str] = None


class OrganizationAliasCreate(OrganizationAliasBase):
    pass


class OrganizationAlias(OrganizationAliasBase):
    id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    organization_type: str
    industry: Optional[str] = None
    size_category: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[int] = None
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False

    @validator('organization_type')
    def validate_organization_type(cls, v):
        valid_types = ['school', 'company', 'nonprofit', 'government', 'healthcare', 'religious']
        if v not in valid_types:
            raise ValueError(f'organization_type must be one of: {", ".join(valid_types)}')
        return v

    @validator('size_category')
    def validate_size_category(cls, v):
        if v is None:
            return v
        valid_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
        if v not in valid_sizes:
            raise ValueError(f'size_category must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('address_country_code')
    def validate_country_code(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('address_country_code must be 2 characters')
        return v


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    organization_type: Optional[str] = None
    industry: Optional[str] = None
    size_category: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @validator('organization_type')
    def validate_organization_type(cls, v):
        if v is None:
            return v
        valid_types = ['school', 'company', 'nonprofit', 'government', 'healthcare', 'religious']
        if v not in valid_types:
            raise ValueError(f'organization_type must be one of: {", ".join(valid_types)}')
        return v

    @validator('size_category')
    def validate_size_category(cls, v):
        if v is None:
            return v
        valid_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
        if v not in valid_sizes:
            raise ValueError(f'size_category must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('address_country_code')
    def validate_country_code(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('address_country_code must be 2 characters')
        return v


class OrganizationInDBBase(OrganizationBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Organization(OrganizationInDBBase):
    aliases: List[OrganizationAlias] = []
    locations: List[OrganizationLocation] = []


class OrganizationSimple(OrganizationInDBBase):
    """Simplified organization response without relationships"""
    pass


# For search and listing responses
class OrganizationSearchResult(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None
    organization_type: str
    industry: Optional[str] = None
    size_category: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    employee_count: Optional[int] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country_code: Optional[str] = None
    contact_count: int = 0  # For future use when contacts are implemented

    class Config:
        from_attributes = True


# Pagination response
class OrganizationListResponse(BaseModel):
    data: List[OrganizationSearchResult]
    pagination: dict  # Contains total, page, per_page, total_pages
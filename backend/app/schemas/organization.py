from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    is_active: Optional[bool] = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationInDBBase(OrganizationBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Organization(OrganizationInDBBase):
    pass


class OrganizationInDB(OrganizationInDBBase):
    pass


# Organization Alias schemas
class OrganizationAliasBase(BaseModel):
    name: str
    is_primary: Optional[bool] = False


class OrganizationAliasCreate(OrganizationAliasBase):
    pass


class OrganizationAliasUpdate(BaseModel):
    name: Optional[str] = None
    is_primary: Optional[bool] = None


class OrganizationAliasInDBBase(OrganizationAliasBase):
    id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationAlias(OrganizationAliasInDBBase):
    pass


# Organization Location schemas
class OrganizationLocationBase(BaseModel):
    name: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    is_primary: Optional[bool] = False


class OrganizationLocationCreate(OrganizationLocationBase):
    pass


class OrganizationLocationUpdate(BaseModel):
    name: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    is_primary: Optional[bool] = None


class OrganizationLocationInDBBase(OrganizationLocationBase):
    id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationLocation(OrganizationLocationInDBBase):
    pass


# Search and Response schemas
class OrganizationSearchResult(Organization):
    """Organization search result with additional metadata."""
    pass


class OrganizationListResponse(BaseModel):
    """Response model for organization list with metadata."""
    organizations: List[Organization]
    total: int
    page: int
    page_size: int
    has_next: bool

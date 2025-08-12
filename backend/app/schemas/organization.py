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


class OrganizationAliasCreate(BaseModel):
    alias: str


class OrganizationLocationCreate(BaseModel):
    name: str
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None


class OrganizationLocationUpdate(BaseModel):
    name: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None


class OrganizationSearchResult(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    items: List[Organization]
    total: int
    page: int
    per_page: int
    
    class Config:
        from_attributes = True


class OrganizationAlias(BaseModel):
    id: int
    alias: str
    organization_id: int
    
    class Config:
        from_attributes = True


class OrganizationLocation(BaseModel):
    id: int
    name: str
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    organization_id: int
    
    class Config:
        from_attributes = True

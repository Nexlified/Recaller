from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    organization_type: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    organization_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class Organization(OrganizationBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SocialGroupBase(BaseModel):
    name: str
    group_type: str
    description: Optional[str] = None

class SocialGroupCreate(SocialGroupBase):
    pass

class SocialGroupUpdate(BaseModel):
    name: Optional[str] = None
    group_type: Optional[str] = None
    description: Optional[str] = None

class SocialGroup(SocialGroupBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class ContactVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class ContactBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    organization_id: Optional[int] = None
    notes: Optional[str] = None
    gender: Optional[str] = None  # 'male', 'female', 'non_binary', 'prefer_not_to_say'
    visibility: Optional[ContactVisibility] = ContactVisibility.PRIVATE
    is_active: Optional[bool] = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    organization_id: Optional[int] = None
    notes: Optional[str] = None
    gender: Optional[str] = None
    visibility: Optional[ContactVisibility] = None
    is_active: Optional[bool] = None


class ContactInDBBase(ContactBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Contact(ContactInDBBase):
    pass

class ContactInDB(ContactInDBBase):
    pass

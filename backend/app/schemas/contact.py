from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
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
    # Family Information Tracking
    date_of_birth: Optional[date] = None  # Birthday for reminders and age tracking
    anniversary_date: Optional[date] = None  # Wedding anniversary or other important family date
    maiden_name: Optional[str] = None  # Maiden name for genealogy tracking
    family_nickname: Optional[str] = None  # Informal family name (e.g., "Grandma", "Uncle Bob")
    is_emergency_contact: Optional[bool] = False  # Emergency contact designation
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
    # Family Information Tracking
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    maiden_name: Optional[str] = None
    family_nickname: Optional[str] = None
    is_emergency_contact: Optional[bool] = None
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

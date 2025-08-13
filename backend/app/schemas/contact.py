from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
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
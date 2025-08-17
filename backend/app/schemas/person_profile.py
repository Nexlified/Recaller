"""
Pydantic schemas for Person Profile models.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from enum import Enum


class PersonProfileVisibility(str, Enum):
    PRIVATE = "private"
    TENANT_SHARED = "tenant_shared"


# Base schemas
class PersonProfileBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    notes: Optional[str] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = True
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


class PersonContactInfoBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_type: Optional[str] = "personal"
    is_primary: Optional[bool] = False
    is_emergency_contact: Optional[bool] = False
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


class PersonProfessionalInfoBase(BaseModel):
    job_title: Optional[str] = None
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    salary_range: Optional[str] = None
    work_location: Optional[str] = None
    employment_type: Optional[str] = None
    notes: Optional[str] = None
    is_current: Optional[bool] = True
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


class PersonPersonalInfoBase(BaseModel):
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    maiden_name: Optional[str] = None
    family_nickname: Optional[str] = None
    preferred_name: Optional[str] = None
    favorite_color: Optional[str] = None
    favorite_food: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    personality_notes: Optional[str] = None
    interests_hobbies: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


class PersonLifeEventBase(BaseModel):
    event_type: str
    title: str
    description: Optional[str] = None
    event_date: date
    location: Optional[str] = None
    my_role: Optional[str] = None
    significance: Optional[int] = None
    is_recurring: Optional[bool] = False
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


class PersonBelongingBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    estimated_value: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_method: Optional[str] = None
    relationship_context: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE
    is_active: Optional[bool] = True


class PersonRelationshipBase(BaseModel):
    person_a_id: int
    person_b_id: int
    relationship_type: str
    relationship_category: str
    relationship_strength: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    how_we_met: Optional[str] = None
    context: Optional[str] = None
    notes: Optional[str] = None
    is_mutual: Optional[bool] = True
    is_active: Optional[bool] = True
    visibility: Optional[PersonProfileVisibility] = PersonProfileVisibility.PRIVATE


# Create schemas
class PersonProfileCreate(PersonProfileBase):
    pass


class PersonContactInfoCreate(PersonContactInfoBase):
    person_id: int


class PersonProfessionalInfoCreate(PersonProfessionalInfoBase):
    person_id: int


class PersonPersonalInfoCreate(PersonPersonalInfoBase):
    person_id: int


class PersonLifeEventCreate(PersonLifeEventBase):
    person_id: int


class PersonBelongingCreate(PersonBelongingBase):
    person_id: int


class PersonRelationshipCreate(PersonRelationshipBase):
    pass


# Update schemas  
class PersonProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    notes: Optional[str] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = None
    visibility: Optional[PersonProfileVisibility] = None


class PersonContactInfoUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_type: Optional[str] = None
    is_primary: Optional[bool] = None
    is_emergency_contact: Optional[bool] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = None


class PersonProfessionalInfoUpdate(BaseModel):
    job_title: Optional[str] = None
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    salary_range: Optional[str] = None
    work_location: Optional[str] = None
    employment_type: Optional[str] = None
    notes: Optional[str] = None
    is_current: Optional[bool] = None
    visibility: Optional[PersonProfileVisibility] = None


class PersonPersonalInfoUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    maiden_name: Optional[str] = None
    family_nickname: Optional[str] = None
    preferred_name: Optional[str] = None
    favorite_color: Optional[str] = None
    favorite_food: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    personality_notes: Optional[str] = None
    interests_hobbies: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = None


class PersonLifeEventUpdate(BaseModel):
    event_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    location: Optional[str] = None
    my_role: Optional[str] = None
    significance: Optional[int] = None
    is_recurring: Optional[bool] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = None


class PersonBelongingUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    estimated_value: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_method: Optional[str] = None
    relationship_context: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonProfileVisibility] = None
    is_active: Optional[bool] = None


class PersonRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    relationship_category: Optional[str] = None
    relationship_strength: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    how_we_met: Optional[str] = None
    context: Optional[str] = None
    notes: Optional[str] = None
    is_mutual: Optional[bool] = None
    is_active: Optional[bool] = None
    visibility: Optional[PersonProfileVisibility] = None


# Response schemas (with database fields)
class PersonContactInfoInDBBase(PersonContactInfoBase):
    id: int
    person_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonProfessionalInfoInDBBase(PersonProfessionalInfoBase):
    id: int
    person_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonPersonalInfoInDBBase(PersonPersonalInfoBase):
    id: int
    person_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonLifeEventInDBBase(PersonLifeEventBase):
    id: int
    person_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonBelongingInDBBase(PersonBelongingBase):
    id: int
    person_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonRelationshipInDBBase(PersonRelationshipBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Public API response schemas
class PersonContactInfo(PersonContactInfoInDBBase):
    pass


class PersonProfessionalInfo(PersonProfessionalInfoInDBBase):
    pass


class PersonPersonalInfo(PersonPersonalInfoInDBBase):
    pass


class PersonLifeEvent(PersonLifeEventInDBBase):
    pass


class PersonBelonging(PersonBelongingInDBBase):
    pass


class PersonRelationship(PersonRelationshipInDBBase):
    pass


class PersonProfileInDBBase(PersonProfileBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonProfile(PersonProfileInDBBase):
    # Include related information optionally
    contact_info: Optional[List[PersonContactInfo]] = None
    professional_info: Optional[List[PersonProfessionalInfo]] = None
    personal_info: Optional[List[PersonPersonalInfo]] = None
    life_events: Optional[List[PersonLifeEvent]] = None
    belongings: Optional[List[PersonBelonging]] = None


class PersonProfileInDB(PersonProfileInDBBase):
    pass


# Simplified response for lists
class PersonProfileSummary(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    visibility: PersonProfileVisibility
    created_at: datetime

    class Config:
        from_attributes = True
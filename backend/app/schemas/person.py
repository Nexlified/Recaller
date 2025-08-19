from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class PersonVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class ContactInfoType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SOCIAL_MEDIA = "social_media"
    WEBSITE = "website"


class ContactInfoPrivacy(str, Enum):
    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"


class LifeEventType(str, Enum):
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    GRADUATION = "graduation"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    BIRTH_OF_CHILD = "birth_of_child"
    DEATH = "death"
    PROMOTION = "promotion"
    JOB_CHANGE = "job_change"
    RELOCATION = "relocation"
    RETIREMENT = "retirement"
    OTHER = "other"


class BelongingType(str, Enum):
    GIFT_RECEIVED = "gift_received"
    GIFT_GIVEN = "gift_given"
    ITEM_BORROWED = "item_borrowed"
    ITEM_LENT = "item_lent"
    POSSESSION = "possession"
    RECOMMENDATION = "recommendation"
    OTHER = "other"


# PersonProfile schemas
class PersonProfileBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    gender: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonVisibility] = PersonVisibility.PRIVATE
    is_active: Optional[bool] = True


class PersonProfileCreate(PersonProfileBase):
    pass


class PersonProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[PersonVisibility] = None
    is_active: Optional[bool] = None


class PersonProfileInDBBase(PersonProfileBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonProfile(PersonProfileInDBBase):
    pass


class PersonProfileInDB(PersonProfileInDBBase):
    pass


# PersonContactInfo schemas
class PersonContactInfoBase(BaseModel):
    contact_type: ContactInfoType
    contact_value: str
    contact_label: Optional[str] = None
    privacy_level: Optional[ContactInfoPrivacy] = ContactInfoPrivacy.PRIVATE
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    is_primary: Optional[bool] = False
    is_active: Optional[bool] = True
    sort_order: Optional[int] = 0


class PersonContactInfoCreate(PersonContactInfoBase):
    person_id: int


class PersonContactInfoUpdate(BaseModel):
    contact_type: Optional[ContactInfoType] = None
    contact_value: Optional[str] = None
    contact_label: Optional[str] = None
    privacy_level: Optional[ContactInfoPrivacy] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class PersonContactInfoInDBBase(PersonContactInfoBase):
    id: int
    person_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonContactInfo(PersonContactInfoInDBBase):
    pass


# PersonProfessionalInfo schemas
class PersonProfessionalInfoBase(BaseModel):
    organization_id: Optional[int] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    is_current_position: Optional[bool] = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    work_email: Optional[str] = None
    work_phone: Optional[str] = None
    work_address: Optional[str] = None
    job_description: Optional[str] = None
    responsibilities: Optional[List[str]] = []
    skills_used: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    manager_person_id: Optional[int] = None
    reporting_structure: Optional[str] = None
    can_be_reference: Optional[bool] = False
    reference_notes: Optional[str] = None
    linkedin_profile: Optional[str] = None
    other_profiles: Optional[dict] = {}
    salary_range: Optional[str] = None
    currency: Optional[str] = "USD"
    is_active: Optional[bool] = True


class PersonProfessionalInfoCreate(PersonProfessionalInfoBase):
    person_id: int


class PersonProfessionalInfoUpdate(BaseModel):
    organization_id: Optional[int] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    is_current_position: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    work_email: Optional[str] = None
    work_phone: Optional[str] = None
    work_address: Optional[str] = None
    job_description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    manager_person_id: Optional[int] = None
    reporting_structure: Optional[str] = None
    can_be_reference: Optional[bool] = None
    reference_notes: Optional[str] = None
    linkedin_profile: Optional[str] = None
    other_profiles: Optional[dict] = None
    salary_range: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class PersonProfessionalInfoInDBBase(PersonProfessionalInfoBase):
    id: int
    person_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonProfessionalInfo(PersonProfessionalInfoInDBBase):
    pass


# PersonPersonalInfo schemas
class PersonPersonalInfoBase(BaseModel):
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    maiden_name: Optional[str] = None
    family_nickname: Optional[str] = None
    is_emergency_contact: Optional[bool] = False
    emergency_contact_priority: Optional[int] = 0
    preferred_communication: Optional[List[str]] = []
    communication_notes: Optional[str] = None
    marital_status: Optional[str] = None
    spouse_partner_person_id: Optional[int] = None
    children_count: Optional[int] = 0
    cultural_background: Optional[str] = None
    languages_spoken: Optional[List[str]] = []
    religion: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    hobbies_interests: Optional[List[str]] = []
    favorite_activities: Optional[List[str]] = []
    privacy_level: Optional[ContactInfoPrivacy] = ContactInfoPrivacy.PRIVATE
    is_active: Optional[bool] = True


class PersonPersonalInfoCreate(PersonPersonalInfoBase):
    person_id: int


class PersonPersonalInfoUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    maiden_name: Optional[str] = None
    family_nickname: Optional[str] = None
    is_emergency_contact: Optional[bool] = None
    emergency_contact_priority: Optional[int] = None
    preferred_communication: Optional[List[str]] = None
    communication_notes: Optional[str] = None
    marital_status: Optional[str] = None
    spouse_partner_person_id: Optional[int] = None
    children_count: Optional[int] = None
    cultural_background: Optional[str] = None
    languages_spoken: Optional[List[str]] = None
    religion: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    hobbies_interests: Optional[List[str]] = None
    favorite_activities: Optional[List[str]] = None
    privacy_level: Optional[ContactInfoPrivacy] = None
    is_active: Optional[bool] = None


class PersonPersonalInfoInDBBase(PersonPersonalInfoBase):
    id: int
    person_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonPersonalInfo(PersonPersonalInfoInDBBase):
    pass


# PersonLifeEvent schemas
class PersonLifeEventBase(BaseModel):
    event_type: LifeEventType
    event_date: date
    event_title: str
    description: Optional[str] = None
    importance_level: Optional[int] = 3
    is_recurring: Optional[bool] = False
    recurring_pattern: Optional[str] = None
    should_remind: Optional[bool] = True
    reminder_days_before: Optional[int] = 7
    location: Optional[str] = None
    participants: Optional[List[str]] = []
    related_organization_id: Optional[int] = None
    tags: Optional[List[str]] = []
    privacy_level: Optional[ContactInfoPrivacy] = ContactInfoPrivacy.PRIVATE
    is_active: Optional[bool] = True


class PersonLifeEventCreate(PersonLifeEventBase):
    person_id: int


class PersonLifeEventUpdate(BaseModel):
    event_type: Optional[LifeEventType] = None
    event_date: Optional[date] = None
    event_title: Optional[str] = None
    description: Optional[str] = None
    importance_level: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurring_pattern: Optional[str] = None
    should_remind: Optional[bool] = None
    reminder_days_before: Optional[int] = None
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    related_organization_id: Optional[int] = None
    tags: Optional[List[str]] = None
    privacy_level: Optional[ContactInfoPrivacy] = None
    is_active: Optional[bool] = None


class PersonLifeEventInDBBase(PersonLifeEventBase):
    id: int
    person_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonLifeEvent(PersonLifeEventInDBBase):
    pass


# PersonBelonging schemas
class PersonBelongingBase(BaseModel):
    belonging_type: BelongingType
    item_name: str
    description: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    currency: Optional[str] = "USD"
    sentimental_value: Optional[int] = 3
    date_acquired: Optional[date] = None
    occasion: Optional[str] = None
    related_person_id: Optional[int] = None
    relationship_context: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    current_location: Optional[str] = None
    is_borrowed: Optional[bool] = False
    borrowed_to_person_id: Optional[int] = None
    borrowed_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    photos: Optional[List[str]] = []
    receipts: Optional[List[str]] = []
    documents: Optional[List[str]] = []
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = []
    privacy_level: Optional[ContactInfoPrivacy] = ContactInfoPrivacy.PRIVATE
    is_active: Optional[bool] = True


class PersonBelongingCreate(PersonBelongingBase):
    person_id: int


class PersonBelongingUpdate(BaseModel):
    belonging_type: Optional[BelongingType] = None
    item_name: Optional[str] = None
    description: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    currency: Optional[str] = None
    sentimental_value: Optional[int] = None
    date_acquired: Optional[date] = None
    occasion: Optional[str] = None
    related_person_id: Optional[int] = None
    relationship_context: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    current_location: Optional[str] = None
    is_borrowed: Optional[bool] = None
    borrowed_to_person_id: Optional[int] = None
    borrowed_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    photos: Optional[List[str]] = None
    receipts: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy_level: Optional[ContactInfoPrivacy] = None
    is_active: Optional[bool] = None


class PersonBelongingInDBBase(PersonBelongingBase):
    id: int
    person_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonBelonging(PersonBelongingInDBBase):
    pass


# Complete Person with all related data
class PersonComplete(PersonProfile):
    contact_info: List[PersonContactInfo] = []
    professional_info: List[PersonProfessionalInfo] = []
    personal_info: Optional[PersonPersonalInfo] = None
    life_events: List[PersonLifeEvent] = []
    belongings: List[PersonBelonging] = []
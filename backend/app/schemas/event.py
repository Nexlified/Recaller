from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date, time
from decimal import Decimal


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_type: str
    event_category: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    timezone: Optional[str] = "UTC"
    location: Optional[str] = None
    venue: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    virtual_event_url: Optional[str] = None
    organizer_name: Optional[str] = None
    organizer_contact_id: Optional[int] = None
    host_organization_id: Optional[int] = None
    expected_attendees: Optional[int] = None
    actual_attendees: Optional[int] = 0
    max_capacity: Optional[int] = None
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = None
    is_private: Optional[bool] = False
    requires_invitation: Optional[bool] = False
    cost: Optional[Decimal] = None
    currency: Optional[str] = "USD"
    dress_code: Optional[str] = None
    special_instructions: Optional[str] = None
    event_website: Optional[str] = None
    event_image_url: Optional[str] = None
    photo_album_url: Optional[str] = None
    status: Optional[str] = "planned"


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country_code: Optional[str] = None
    virtual_event_url: Optional[str] = None
    organizer_name: Optional[str] = None
    organizer_contact_id: Optional[int] = None
    host_organization_id: Optional[int] = None
    expected_attendees: Optional[int] = None
    actual_attendees: Optional[int] = None
    max_capacity: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    is_private: Optional[bool] = None
    requires_invitation: Optional[bool] = None
    cost: Optional[Decimal] = None
    currency: Optional[str] = None
    dress_code: Optional[str] = None
    special_instructions: Optional[str] = None
    event_website: Optional[str] = None
    event_image_url: Optional[str] = None
    photo_album_url: Optional[str] = None
    status: Optional[str] = None


class EventInDBBase(EventBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Event(EventInDBBase):
    pass


class EventInDB(EventInDBBase):
    pass


# Contact Event Attendance Schemas
class ContactEventAttendanceBase(BaseModel):
    contact_id: int
    event_id: int
    attendance_status: Optional[str] = "invited"
    role_at_event: Optional[str] = None
    invitation_method: Optional[str] = None
    how_we_met_at_event: Optional[str] = None
    conversation_highlights: Optional[str] = None
    follow_up_needed: Optional[bool] = False
    follow_up_notes: Optional[str] = None
    rsvp_date: Optional[datetime] = None
    rsvp_response: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    plus_one_count: Optional[int] = 0
    relationship_strength_before: Optional[int] = None
    relationship_strength_after: Optional[int] = None
    connection_quality: Optional[str] = None
    personal_notes: Optional[str] = None
    memorable_moments: Optional[str] = None
    photos_with_contact: Optional[List[str]] = None


class ContactEventAttendanceCreate(ContactEventAttendanceBase):
    pass


class ContactEventAttendanceUpdate(BaseModel):
    attendance_status: Optional[str] = None
    role_at_event: Optional[str] = None
    invitation_method: Optional[str] = None
    how_we_met_at_event: Optional[str] = None
    conversation_highlights: Optional[str] = None
    follow_up_needed: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    rsvp_date: Optional[datetime] = None
    rsvp_response: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    plus_one_count: Optional[int] = None
    relationship_strength_before: Optional[int] = None
    relationship_strength_after: Optional[int] = None
    connection_quality: Optional[str] = None
    personal_notes: Optional[str] = None
    memorable_moments: Optional[str] = None
    photos_with_contact: Optional[List[str]] = None


class ContactEventAttendanceInDBBase(ContactEventAttendanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContactEventAttendance(ContactEventAttendanceInDBBase):
    pass


# Event Tag Schemas
class EventTagBase(BaseModel):
    event_id: int
    tag_name: str
    tag_color: Optional[str] = None


class EventTagCreate(EventTagBase):
    pass


class EventTagInDBBase(EventTagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventTag(EventTagInDBBase):
    pass


# Event Follow-up Schemas
class EventFollowUpBase(BaseModel):
    event_id: int
    contact_id: Optional[int] = None
    follow_up_type: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "pending"
    completed_date: Optional[date] = None
    completion_notes: Optional[str] = None


class EventFollowUpCreate(EventFollowUpBase):
    pass


class EventFollowUpUpdate(BaseModel):
    follow_up_type: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    completed_date: Optional[date] = None
    completion_notes: Optional[str] = None


class EventFollowUpInDBBase(EventFollowUpBase):
    id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventFollowUp(EventFollowUpInDBBase):
    pass


# Response schemas for events with related data
class EventWithAttendees(Event):
    attendees: Optional[List[ContactEventAttendance]] = []
    tags: Optional[List[EventTag]] = []
    follow_ups: Optional[List[EventFollowUp]] = []


class EventAnalytics(BaseModel):
    new_connections: int
    strengthened_relationships: int
    follow_ups_created: int
    total_attendees: int
    attendance_rate: Optional[float] = None
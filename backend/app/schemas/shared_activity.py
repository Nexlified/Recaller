from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from decimal import Decimal

class SharedActivityParticipantBase(BaseModel):
    contact_id: int
    participation_level: str = Field(..., pattern="^(organizer|participant|invitee)$")
    attendance_status: str = Field(..., pattern="^(confirmed|maybe|declined|no_show|attended)$")
    participant_notes: Optional[str] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=10)

class SharedActivityParticipantCreate(SharedActivityParticipantBase):
    pass

class SharedActivityParticipantUpdate(BaseModel):
    participation_level: Optional[str] = Field(None, pattern="^(organizer|participant|invitee)$")
    attendance_status: Optional[str] = Field(None, pattern="^(confirmed|maybe|declined|no_show|attended)$")
    participant_notes: Optional[str] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=10)

class SharedActivityParticipant(SharedActivityParticipantBase):
    id: int
    activity_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SharedActivityBase(BaseModel):
    activity_type: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    activity_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    cost_per_person: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    quality_rating: Optional[int] = Field(None, ge=1, le=10)
    photos: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    memorable_moments: Optional[str] = None
    status: str = Field(default="planned", pattern="^(planned|completed|cancelled|postponed)$")
    is_private: bool = False

class SharedActivityCreate(SharedActivityBase):
    participants: List[SharedActivityParticipantCreate] = Field(..., min_items=1)
    
    @validator('participants')
    def validate_participants(cls, v):
        if not v:
            raise ValueError('At least one participant is required')
        
        # Check for at least one organizer
        organizers = [p for p in v if p.participation_level == 'organizer']
        if not organizers:
            raise ValueError('At least one organizer is required')
        
        return v

class SharedActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    activity_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    cost_per_person: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    quality_rating: Optional[int] = Field(None, ge=1, le=10)
    photos: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    memorable_moments: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(planned|completed|cancelled|postponed)$")
    is_private: Optional[bool] = None

class SharedActivity(SharedActivityBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    participants: List[SharedActivityParticipant] = []
    
    class Config:
        from_attributes = True

class ActivityInsights(BaseModel):
    total_activities: int
    activities_this_month: int
    favorite_activity_type: Optional[str]
    average_quality_rating: Optional[float]
    total_spent: Optional[Decimal]
    most_active_contacts: List[Dict[str, Any]]
    activity_frequency: Dict[str, int]
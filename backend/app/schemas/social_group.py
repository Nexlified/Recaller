from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date, time
from decimal import Decimal

# Social Group Schemas
class SocialGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    group_type: str  # 'friends', 'family', 'hobby', 'sports', 'professional', 'neighbors', 'travel', 'study'
    privacy_level: Optional[str] = 'private'  # 'private', 'shared_tenant'
    meets_regularly: Optional[bool] = False
    meeting_frequency: Optional[str] = None  # 'weekly', 'monthly', 'quarterly', 'yearly', 'irregular'
    meeting_day_of_week: Optional[int] = None  # 1-7 for Monday-Sunday
    meeting_time: Optional[time] = None
    meeting_location: Optional[str] = None
    virtual_meeting_url: Optional[str] = None
    founded_date: Optional[date] = None
    max_members: Optional[int] = None
    auto_add_contacts: Optional[bool] = False
    group_image_url: Optional[str] = None
    group_color: Optional[str] = None  # Hex color for UI
    tags: Optional[List[str]] = None

class SocialGroupCreate(SocialGroupBase):
    pass

class SocialGroupUpdate(SocialGroupBase):
    name: Optional[str] = None
    group_type: Optional[str] = None

class SocialGroupInDBBase(SocialGroupBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    member_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SocialGroup(SocialGroupInDBBase):
    pass

class SocialGroupInDB(SocialGroupInDBBase):
    pass

# Membership Schemas
class SocialGroupMembershipBase(BaseModel):
    role: Optional[str] = 'member'  # 'member', 'organizer', 'leader', 'founder', 'admin'
    membership_status: Optional[str] = 'active'  # 'active', 'inactive', 'left', 'removed'
    participation_level: Optional[int] = 5  # 1-10 scale
    membership_notes: Optional[str] = None

class SocialGroupMembershipCreate(SocialGroupMembershipBase):
    contact_id: int
    social_group_id: int

class SocialGroupMembershipUpdate(SocialGroupMembershipBase):
    pass

class SocialGroupMembershipInDBBase(SocialGroupMembershipBase):
    id: int
    contact_id: int
    social_group_id: int
    joined_date: date
    left_date: Optional[date]
    last_participated: Optional[date]
    total_events_attended: int
    invited_by_user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SocialGroupMembership(SocialGroupMembershipInDBBase):
    pass

# Activity Schemas
class SocialGroupActivityBase(BaseModel):
    name: str
    description: Optional[str] = None
    activity_type: Optional[str] = None  # 'meeting', 'outing', 'party', 'trip', 'project', 'volunteer'
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    virtual_meeting_url: Optional[str] = None
    max_attendees: Optional[int] = None
    cost: Optional[Decimal] = None
    organizer_notes: Optional[str] = None

class SocialGroupActivityCreate(SocialGroupActivityBase):
    social_group_id: int

class SocialGroupActivityUpdate(SocialGroupActivityBase):
    name: Optional[str] = None

class SocialGroupActivityInDBBase(SocialGroupActivityBase):
    id: int
    social_group_id: int
    created_by_user_id: int
    status: str  # 'planned', 'confirmed', 'cancelled', 'completed'
    actual_attendees: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SocialGroupActivity(SocialGroupActivityInDBBase):
    pass

# Attendance Schemas
class SocialGroupActivityAttendanceBase(BaseModel):
    attendance_status: Optional[str] = 'invited'  # 'invited', 'confirmed', 'attended', 'declined', 'no_show'
    attendance_notes: Optional[str] = None

class SocialGroupActivityAttendanceCreate(SocialGroupActivityAttendanceBase):
    activity_id: int
    contact_id: int

class SocialGroupActivityAttendanceUpdate(SocialGroupActivityAttendanceBase):
    pass

class SocialGroupActivityAttendanceInDBBase(SocialGroupActivityAttendanceBase):
    id: int
    activity_id: int
    contact_id: int
    rsvp_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class SocialGroupActivityAttendance(SocialGroupActivityAttendanceInDBBase):
    pass

# Bulk operations
class BulkMembershipCreate(BaseModel):
    members: List[SocialGroupMembershipCreate]

# Response with includes
class SocialGroupWithMembers(SocialGroup):
    memberships: Optional[List[SocialGroupMembership]] = None

class SocialGroupWithActivities(SocialGroup):
    activities: Optional[List[SocialGroupActivity]] = None
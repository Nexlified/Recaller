from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Time, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class SocialGroup(Base):
    __tablename__ = "social_groups"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    group_type = Column(String(50), nullable=False, index=True)  # 'friends', 'family', 'hobby', 'sports', 'professional', 'neighbors', 'travel', 'study'
    privacy_level = Column(String(20), default='private')  # 'private', 'shared_tenant'
    
    # Meeting Information
    meets_regularly = Column(Boolean, default=False)
    meeting_frequency = Column(String(50))  # 'weekly', 'monthly', 'quarterly', 'yearly', 'irregular'
    meeting_day_of_week = Column(Integer)  # 1-7 for Monday-Sunday
    meeting_time = Column(Time)
    meeting_location = Column(String(255))
    virtual_meeting_url = Column(String(500))
    
    # Group Details
    founded_date = Column(Date)
    member_count = Column(Integer, default=0)
    max_members = Column(Integer)  # Optional limit
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    auto_add_contacts = Column(Boolean, default=False)  # Auto-add new contacts with matching criteria
    
    # Metadata
    group_image_url = Column(String(500))
    group_color = Column(String(7))  # Hex color for UI
    tags = Column(JSON)  # Changed from ARRAY(String) for SQLite compatibility
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", backref="social_groups")
    created_by = relationship("User", backref="created_social_groups")


class ContactSocialGroupMembership(Base):
    __tablename__ = "contact_social_group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    social_group_id = Column(Integer, ForeignKey("social_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Membership Details
    role = Column(String(100), default='member')  # 'member', 'organizer', 'leader', 'founder', 'admin'
    membership_status = Column(String(50), default='active', index=True)  # 'active', 'inactive', 'left', 'removed'
    
    # Dates
    joined_date = Column(Date, server_default=func.current_date())
    left_date = Column(Date)
    
    # Participation
    participation_level = Column(Integer, default=5)  # 1-10 scale of involvement
    last_participated = Column(Date)
    total_events_attended = Column(Integer, default=0)
    
    # Notes
    membership_notes = Column(Text)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", backref="social_group_memberships")
    social_group = relationship("SocialGroup", backref="memberships")
    invited_by = relationship("User", backref="invited_memberships")


class SocialGroupActivity(Base):
    __tablename__ = "social_group_activities"

    id = Column(Integer, primary_key=True, index=True)
    social_group_id = Column(Integer, ForeignKey("social_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Activity Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    activity_type = Column(String(50))  # 'meeting', 'outing', 'party', 'trip', 'project', 'volunteer'
    
    # Scheduling
    scheduled_date = Column(Date, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String(255))
    virtual_meeting_url = Column(String(500))
    
    # Status
    status = Column(String(50), default='planned')  # 'planned', 'confirmed', 'cancelled', 'completed'
    max_attendees = Column(Integer)
    actual_attendees = Column(Integer, default=0)
    
    # Metadata
    cost = Column(DECIMAL(10, 2))
    organizer_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    social_group = relationship("SocialGroup", backref="activities")
    created_by = relationship("User", backref="created_activities")


class SocialGroupActivityAttendance(Base):
    __tablename__ = "social_group_activity_attendance"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("social_group_activities.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    
    attendance_status = Column(String(50), default='invited')  # 'invited', 'confirmed', 'attended', 'declined', 'no_show'
    rsvp_date = Column(DateTime(timezone=True))
    attendance_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    activity = relationship("SocialGroupActivity", backref="attendance_records")
    contact = relationship("Contact", backref="activity_attendance")
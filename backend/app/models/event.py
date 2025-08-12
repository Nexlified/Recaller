from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, 
    Date, Time, DECIMAL, ARRAY
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(String(50), nullable=False, index=True)  # 'wedding', 'conference', 'party', 'meetup', 'vacation', 'work_event', 'family_gathering'
    event_category = Column(String(50))  # 'personal', 'professional', 'social', 'family', 'educational'
    
    # Date and Time
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    timezone = Column(String(50), default='UTC')
    
    # Location
    location = Column(String(255))
    venue = Column(String(255))
    address_street = Column(Text)
    address_city = Column(String(100))
    address_state = Column(String(100))
    address_postal_code = Column(String(20))
    address_country_code = Column(String(2))
    virtual_event_url = Column(String(500))
    
    # Event Details
    organizer_name = Column(String(255))
    organizer_contact_id = Column(Integer, ForeignKey("contacts.id"), index=True)
    host_organization_id = Column(Integer, ForeignKey("organizations.id"), index=True)
    
    # Capacity and Scale
    expected_attendees = Column(Integer)
    actual_attendees = Column(Integer, default=0)
    max_capacity = Column(Integer)
    
    # Event Properties
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # 'yearly', 'monthly', 'weekly'
    is_private = Column(Boolean, default=False)
    requires_invitation = Column(Boolean, default=False)
    
    # Metadata
    cost = Column(DECIMAL(10, 2))
    currency = Column(String(3), default='USD')
    dress_code = Column(String(100))
    special_instructions = Column(Text)
    event_website = Column(String(500))
    
    # Media
    event_image_url = Column(String(500))
    photo_album_url = Column(String(500))
    
    # Status
    status = Column(String(50), default='planned')  # 'planned', 'confirmed', 'ongoing', 'completed', 'cancelled', 'postponed'
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", backref="events")
    created_by = relationship("User", backref="created_events")
    organizer_contact = relationship("Contact", foreign_keys=[organizer_contact_id], backref="organized_events")
    host_organization = relationship("Organization", foreign_keys=[host_organization_id], backref="hosted_events")


class ContactEventAttendance(Base):
    __tablename__ = "contact_event_attendances"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Attendance Details
    attendance_status = Column(String(50), default='invited', index=True)  # 'invited', 'confirmed', 'attended', 'declined', 'no_show', 'maybe'
    role_at_event = Column(String(100))  # 'guest', 'organizer', 'speaker', 'host', 'vendor', 'performer'
    invitation_method = Column(String(50))  # 'direct', 'through_friend', 'public', 'social_media'
    
    # Interaction Context
    how_we_met_at_event = Column(Text)  # How you specifically interacted at this event
    conversation_highlights = Column(Text)
    follow_up_needed = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # RSVP and Response
    rsvp_date = Column(DateTime(timezone=True))
    rsvp_response = Column(String(50))  # 'yes', 'no', 'maybe', 'pending'
    dietary_restrictions = Column(Text)
    plus_one_count = Column(Integer, default=0)
    
    # Relationship Impact
    relationship_strength_before = Column(Integer)  # 1-10 scale before event
    relationship_strength_after = Column(Integer)  # 1-10 scale after event
    connection_quality = Column(String(50))  # 'first_meeting', 'strengthened', 'maintained', 'weakened'
    
    # Notes and Memories
    personal_notes = Column(Text)
    memorable_moments = Column(Text)
    photos_with_contact = Column(ARRAY(String))  # URLs or paths to photos
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    contact = relationship("Contact", backref="event_attendances")
    event = relationship("Event", backref="attendances")


class EventTag(Base):
    __tablename__ = "event_tags"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_color = Column(String(7))  # Hex color code
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", backref="tags")


class EventFollowUp(Base):
    __tablename__ = "event_follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"))
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    follow_up_type = Column(String(50))  # 'thank_you', 'business_discussion', 'social_meetup', 'collaboration'
    description = Column(Text)
    due_date = Column(Date)
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high'
    status = Column(String(50), default='pending')  # 'pending', 'completed', 'cancelled'
    
    completed_date = Column(Date)
    completion_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    event = relationship("Event", backref="follow_ups")
    contact = relationship("Contact", backref="follow_ups")
    created_by = relationship("User", backref="created_follow_ups")
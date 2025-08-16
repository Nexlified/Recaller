from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Time, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum
import sqlalchemy as sa

class ActivityType(enum.Enum):
    DINNER = "dinner"
    MOVIE = "movie"
    SPORTS = "sports"
    TRAVEL = "travel"
    WORK_MEETING = "work_meeting"
    COFFEE = "coffee"
    PARTY = "party"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    HOBBY = "hobby"
    SHOPPING = "shopping"
    CULTURAL = "cultural"
    OUTDOOR = "outdoor"
    GAME_NIGHT = "game_night"
    OTHER = "other"

class ActivityStatus(enum.Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class ParticipationLevel(enum.Enum):
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"
    INVITEE = "invitee"

class AttendanceStatus(enum.Enum):
    CONFIRMED = "confirmed"
    MAYBE = "maybe"
    DECLINED = "declined"
    NO_SHOW = "no_show"
    ATTENDED = "attended"

class SharedActivity(Base):
    __tablename__ = "shared_activities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(500))
    
    # Timing
    activity_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    duration_minutes = Column(Integer)
    
    # Financial
    cost_per_person = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    
    # Quality & Memory
    quality_rating = Column(Integer)  # 1-10 scale
    photos = Column(JSONB)  # Array of photo metadata
    notes = Column(Text)
    memorable_moments = Column(Text)
    
    # Status
    status = Column(String(20), default=ActivityStatus.PLANNED.value, index=True)
    is_private = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    created_by = relationship("User")
    participants = relationship("SharedActivityParticipant", back_populates="activity", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 10)', name='check_quality_rating_range'),
    )
    
    @property
    def participant_contacts(self):
        """Get all contact participants"""
        return [p.contact for p in self.participants]
    
    @property
    def organizers(self):
        """Get organizer participants"""
        return [p for p in self.participants if p.participation_level == ParticipationLevel.ORGANIZER.value]

class SharedActivityParticipant(Base):
    __tablename__ = "shared_activity_participants"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("shared_activities.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Participation Details
    participation_level = Column(String(20), nullable=False, index=True)
    attendance_status = Column(String(20), nullable=False, index=True)
    
    # Individual Notes
    participant_notes = Column(Text)
    satisfaction_rating = Column(Integer)  # 1-10 scale
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    activity = relationship("SharedActivity", back_populates="participants")
    contact = relationship("Contact")
    tenant = relationship("Tenant")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('activity_id', 'contact_id', name='uq_activity_participant'),
        CheckConstraint('satisfaction_rating IS NULL OR (satisfaction_rating >= 1 AND satisfaction_rating <= 10)', name='check_satisfaction_rating_range'),
    )

# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.contact import Contact
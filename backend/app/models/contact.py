from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Numeric, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

import enum

class ContactVisibility(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic Information - matching database schema
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    
    # Professional Information
    job_title = Column(String(255))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Notes
    notes = Column(Text)
    
    # Gender (optional field for relationship mapping)
    gender = Column(String(20), nullable=True)  # 'male', 'female', 'non_binary', 'prefer_not_to_say'
    
    # Family Information Tracking
    date_of_birth = Column(Date, nullable=True)  # Birthday for reminders and age tracking
    anniversary_date = Column(Date, nullable=True)  # Wedding anniversary or other important family date
    maiden_name = Column(String(255), nullable=True)  # Maiden name for genealogy tracking
    family_nickname = Column(String(100), nullable=True)  # Informal family name (e.g., "Grandma", "Uncle Bob")
    is_emergency_contact = Column(Boolean, default=False, index=True)  # Emergency contact designation
    
    # Visibility scope
    visibility = Column(String(10), nullable=False, default=ContactVisibility.PRIVATE.value, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="contacts")
    created_by = relationship(lambda: User, back_populates="contacts")
    organization = relationship(lambda: Organization, foreign_keys=[organization_id], back_populates="contacts")
    interactions = relationship("ContactInteraction", back_populates="contact", cascade="all, delete-orphan")
    task_contacts = relationship(lambda: TaskContact, back_populates="contact")
    work_experiences = relationship("ContactWorkExperience", foreign_keys="ContactWorkExperience.contact_id", back_populates="contact", cascade="all, delete-orphan")
    personal_reminders = relationship(lambda: PersonalReminder, back_populates="contact")
    gifts_received = relationship(lambda: Gift, back_populates="recipient_contact")
    gift_ideas_for_them = relationship(lambda: GiftIdea, back_populates="target_contact")
    
    # Helper properties for work experience
    @property
    def current_work_experience(self):
        """Get the current work experience"""
        return next((exp for exp in self.work_experiences if exp.is_current), None)

    @property
    def work_history(self):
        """Get all work experiences ordered by start date (most recent first)"""
        return sorted(self.work_experiences, key=lambda x: x.start_date, reverse=True)

# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.organization import Organization
from app.models.social_group import ContactSocialGroupMembership
from app.models.task import TaskContact
from app.models.personal_reminder import PersonalReminder
from app.models.gift import Gift, GiftIdea

class ContactInteraction(Base):
    __tablename__ = "contact_interactions"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    
    # Interaction Details
    interaction_type = Column(String(50), nullable=False)  # meeting, call, email, text, event
    interaction_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer)
    location = Column(String(200))
    
    # Quality and Context
    interaction_quality = Column(Numeric(2,1), default=5.0)  # 1-10 scale
    interaction_mood = Column(String(20))  # positive, neutral, negative
    initiated_by = Column(String(20), nullable=False)  # me, them, mutual
    
    # Content
    title = Column(String(200))
    description = Column(Text)
    topics_discussed = Column(JSON, default=list)  # Changed from ARRAY(String) for SQLite compatibility
    
    # Outcomes
    follow_up_required = Column(Boolean, default=False)
    next_steps = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="interactions")

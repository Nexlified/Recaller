from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    
    # Professional Information
    job_title = Column(String(200))
    current_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    alma_mater_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationship Information
    connection_strength = Column(Numeric(3,2), default=5.0)  # 1-10 scale
    networking_value = Column(String(20), default='medium')  # high, medium, low
    relationship_status = Column(String(50), default='active')  # active, dormant, archived
    
    # Interaction Tracking
    total_interactions = Column(Integer, default=0)
    last_meaningful_interaction = Column(DateTime(timezone=True))
    interaction_frequency = Column(String(20))  # daily, weekly, monthly, quarterly, yearly
    
    # Follow-up Management
    next_suggested_contact_date = Column(DateTime(timezone=True))
    follow_up_urgency = Column(String(20), default='medium')  # high, medium, low
    follow_up_notes = Column(Text)
    
    # Tags and Categories
    tags = Column(ARRAY(String), default=list)
    contact_source = Column(String(50))  # event, referral, social, professional
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="contacts")
    current_organization = relationship("Organization", foreign_keys=[current_organization_id], back_populates="current_employees")
    alma_mater = relationship("Organization", foreign_keys=[alma_mater_id], back_populates="alumni")
    interactions = relationship("ContactInteraction", back_populates="contact", cascade="all, delete-orphan")
    group_memberships = relationship("ContactSocialGroupMembership", back_populates="contact", cascade="all, delete-orphan")

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
    topics_discussed = Column(ARRAY(String), default=list)
    
    # Outcomes
    follow_up_required = Column(Boolean, default=False)
    next_steps = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="interactions")

class ContactSocialGroupMembership(Base):
    __tablename__ = "contact_social_group_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    social_group_id = Column(Integer, ForeignKey("social_groups.id"), nullable=False, index=True)
    
    membership_status = Column(String(20), default='active')  # active, inactive, left
    role = Column(String(50))  # member, organizer, leader
    joined_date = Column(DateTime(timezone=True))
    left_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    contact = relationship("Contact", back_populates="group_memberships")
    social_group = relationship("SocialGroup", back_populates="memberships")
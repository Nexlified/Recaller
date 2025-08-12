from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.tenant import Tenant
from app.models.user import User

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Contact Information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    
    # Education & Career Context
    education_level = Column(String)  # 'high_school', 'bachelor', 'master', 'phd', 'other'
    graduation_year = Column(Integer)
    alma_mater_id = Column(Integer, ForeignKey("organizations.id"))
    current_organization_id = Column(Integer, ForeignKey("organizations.id"))
    current_position = Column(String)
    career_stage = Column(String)  # 'student', 'entry_level', 'mid_level', 'senior', 'executive', 'retired'
    industry_experience = Column(ARRAY(Text))  # Array of industries worked in
    
    # Social & Personal Context
    primary_social_group_id = Column(Integer, ForeignKey("social_groups.id"))
    personality_type = Column(String)  # 'introvert', 'extrovert', 'ambivert'
    communication_preference = Column(String)  # 'text', 'call', 'email', 'in_person', 'video_call'
    preferred_communication_time = Column(String)  # 'morning', 'afternoon', 'evening', 'weekends'
    
    # Life Context
    life_stage = Column(String)  # 'student', 'early_career', 'established', 'parent', 'empty_nester', 'retired'
    relationship_status = Column(String)  # 'single', 'dating', 'married', 'divorced', 'widowed'
    has_children = Column(Boolean, default=False)
    children_count = Column(Integer, default=0)
    children_ages = Column(ARRAY(Integer))  # Array of children's ages
    
    # Interests & Preferences
    hobbies = Column(ARRAY(Text))  # Array of hobbies and interests
    conversation_topics = Column(ARRAY(Text))  # Topics they enjoy discussing
    languages_spoken = Column(String)  # JSON array of languages and proficiency
    dietary_restrictions = Column(ARRAY(Text))  # Food allergies, vegetarian, etc.
    preferred_meeting_type = Column(String)  # 'coffee', 'lunch', 'dinner', 'activity', 'video_call'
    
    # Connection Intelligence
    connection_strength = Column(Integer, default=5)  # 1-10 scale of relationship strength
    connection_source = Column(String)  # How you originally met
    mutual_connections_count = Column(Integer, default=0)
    interaction_frequency_goal = Column(String)  # 'weekly', 'monthly', 'quarterly', 'yearly'
    last_meaningful_interaction = Column(Date)
    interaction_quality_trend = Column(String, default='stable')  # 'improving', 'stable', 'declining'
    
    # Engagement Metrics
    total_interactions = Column(Integer, default=0)
    digital_interactions = Column(Integer, default=0)  # emails, messages, etc.
    in_person_interactions = Column(Integer, default=0)
    events_attended_together = Column(Integer, default=0)
    avg_response_time_hours = Column(Integer)  # Average time to respond to messages
    
    # Follow-up Intelligence
    follow_up_frequency = Column(Integer, default=30)  # Days between check-ins
    last_follow_up_date = Column(Date)
    next_suggested_contact_date = Column(Date)
    follow_up_urgency = Column(String, default='normal')  # 'low', 'normal', 'high', 'overdue'
    
    # Special Dates & Reminders
    important_dates = Column(JSONB)  # Flexible structure for anniversaries, etc.
    reminder_preferences = Column(JSONB)  # When and how to be reminded
    
    # Professional Context
    networking_value = Column(String, default='medium')  # 'low', 'medium', 'high' - professional value
    collaboration_potential = Column(String, default='unknown')  # Potential for working together
    referral_potential = Column(String, default='unknown')  # Potential to provide referrals
    influence_level = Column(String, default='unknown')  # 'low', 'medium', 'high' in their field
    
    # Personal Notes & Context
    relationship_notes = Column(Text)  # Private notes about the relationship
    conversation_history_summary = Column(Text)  # Summary of recent conversations
    shared_experiences = Column(Text)  # Memorable shared experiences
    mutual_interests = Column(ARRAY(Text))  # Things you both enjoy
    
    # AI/ML Enhancement Fields
    contact_score = Column(DECIMAL(5,2), default=5.0)  # Overall relationship health score
    engagement_score = Column(DECIMAL(5,2), default=5.0)  # How engaged they are
    priority_score = Column(DECIMAL(5,2), default=5.0)  # How important to maintain contact
    relationship_trend = Column(String, default='stable')  # 'growing', 'stable', 'declining'
    last_ai_analysis = Column(DateTime(timezone=True))  # When AI last analyzed this contact
    
    # Privacy & Sharing
    sharing_preferences = Column(JSONB)  # Who can see what information
    data_sensitivity = Column(String, default='normal')  # 'low', 'normal', 'high', 'confidential'
    
    # Tenant relationship
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    current_organization = relationship("Organization", foreign_keys=[current_organization_id], back_populates="contacts")
    alma_mater = relationship("Organization", foreign_keys=[alma_mater_id], back_populates="alumni_contacts")
    primary_social_group = relationship("SocialGroup", back_populates="primary_contacts")
    
    # Interaction relationships
    interactions = relationship("ContactInteraction", back_populates="contact", cascade="all, delete-orphan")
    relationship_scores = relationship("ContactRelationshipScore", back_populates="contact", cascade="all, delete-orphan")
    ai_insights = relationship("ContactAIInsight", back_populates="contact", cascade="all, delete-orphan")
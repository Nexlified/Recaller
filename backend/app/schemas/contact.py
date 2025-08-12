from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ContactIntelligence(BaseModel):
    # Education & Career Context
    education_level: Optional[str] = None
    graduation_year: Optional[int] = None
    alma_mater_id: Optional[int] = None
    current_organization_id: Optional[int] = None
    current_position: Optional[str] = None
    career_stage: Optional[str] = None
    industry_experience: Optional[List[str]] = None
    
    # Social & Personal Context
    primary_social_group_id: Optional[int] = None
    personality_type: Optional[str] = None
    communication_preference: Optional[str] = None
    preferred_communication_time: Optional[str] = None
    
    # Life Context
    life_stage: Optional[str] = None
    relationship_status: Optional[str] = None
    has_children: Optional[bool] = False
    children_count: Optional[int] = 0
    children_ages: Optional[List[int]] = None
    
    # Interests & Preferences
    hobbies: Optional[List[str]] = None
    conversation_topics: Optional[List[str]] = None
    languages_spoken: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    preferred_meeting_type: Optional[str] = None
    
    # Connection Intelligence
    connection_strength: Optional[int] = Field(default=5, ge=1, le=10)
    connection_source: Optional[str] = None
    mutual_connections_count: Optional[int] = 0
    interaction_frequency_goal: Optional[str] = None
    last_meaningful_interaction: Optional[date] = None
    interaction_quality_trend: Optional[str] = "stable"
    
    # Professional Context
    networking_value: Optional[str] = "medium"
    collaboration_potential: Optional[str] = "unknown"
    referral_potential: Optional[str] = "unknown"
    influence_level: Optional[str] = "unknown"
    
    # Personal Notes & Context
    relationship_notes: Optional[str] = None
    conversation_history_summary: Optional[str] = None
    shared_experiences: Optional[str] = None
    mutual_interests: Optional[List[str]] = None

class ContactCreate(ContactBase):
    intelligence: Optional[ContactIntelligence] = None

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class ContactIntelligenceUpdate(ContactIntelligence):
    pass

class ContactRelationshipContext(BaseModel):
    personality_type: Optional[str] = None
    communication_preference: Optional[str] = None
    life_stage: Optional[str] = None
    networking_value: Optional[str] = None
    collaboration_potential: Optional[str] = None

class ContactInteractionPreferences(BaseModel):
    communication_preference: Optional[str] = None
    preferred_communication_time: Optional[str] = None
    preferred_meeting_type: Optional[str] = None
    interaction_frequency_goal: Optional[str] = None
    follow_up_frequency: Optional[int] = None

class ContactIntelligenceMetrics(BaseModel):
    connection_strength: int
    engagement_score: Decimal
    priority_score: Decimal
    relationship_trend: str
    total_interactions: int
    last_meaningful_interaction: Optional[date] = None
    next_suggested_contact_date: Optional[date] = None
    follow_up_urgency: str

class ContactInteractionSummary(BaseModel):
    total_interactions: int
    avg_interaction_quality: Optional[float] = None
    preferred_interaction_times: List[str]
    response_rate: Optional[float] = None

class Contact(ContactBase):
    id: int
    tenant_id: int
    
    # Intelligence fields
    education_level: Optional[str] = None
    graduation_year: Optional[int] = None
    current_position: Optional[str] = None
    career_stage: Optional[str] = None
    personality_type: Optional[str] = None
    communication_preference: Optional[str] = None
    life_stage: Optional[str] = None
    connection_strength: int = 5
    connection_source: Optional[str] = None
    networking_value: str = "medium"
    collaboration_potential: str = "unknown"
    
    # Metrics
    contact_score: Decimal = Decimal("5.0")
    engagement_score: Decimal = Decimal("5.0")
    priority_score: Decimal = Decimal("5.0")
    relationship_trend: str = "stable"
    total_interactions: int = 0
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContactFullProfile(Contact):
    intelligence: ContactIntelligenceMetrics
    context: ContactRelationshipContext
    interaction_summary: ContactInteractionSummary
    current_organization: Optional[Dict[str, Any]] = None
    recent_insights: List[Dict[str, Any]] = []
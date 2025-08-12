from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

class ContactInteractionBase(BaseModel):
    interaction_type: str  # 'call', 'text', 'email', 'meeting', 'social_media', 'event'
    interaction_method: Optional[str] = None  # 'phone', 'video', 'in_person', 'whatsapp', 'linkedin'
    interaction_date: datetime
    duration_minutes: Optional[int] = None
    initiated_by: Optional[str] = None  # 'me', 'them', 'mutual'
    interaction_quality: Optional[int] = Field(default=None, ge=1, le=10)
    topics_discussed: Optional[List[str]] = None
    mood_assessment: Optional[str] = None  # 'positive', 'neutral', 'negative'
    summary: Optional[str] = None
    key_takeaways: Optional[str] = None
    follow_up_needed: Optional[bool] = False
    follow_up_notes: Optional[str] = None
    location: Optional[str] = None
    private_notes: Optional[str] = None
    attachments: Optional[List[str]] = None

class ContactInteractionCreate(ContactInteractionBase):
    contact_id: int

class ContactInteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    interaction_method: Optional[str] = None
    interaction_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    initiated_by: Optional[str] = None
    interaction_quality: Optional[int] = Field(default=None, ge=1, le=10)
    topics_discussed: Optional[List[str]] = None
    mood_assessment: Optional[str] = None
    summary: Optional[str] = None
    key_takeaways: Optional[str] = None
    follow_up_needed: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    location: Optional[str] = None
    private_notes: Optional[str] = None
    attachments: Optional[List[str]] = None

class ContactInteraction(ContactInteractionBase):
    id: int
    contact_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ContactRelationshipScoreBase(BaseModel):
    connection_strength: Optional[int] = Field(default=None, ge=1, le=10)
    engagement_score: Optional[Decimal] = None
    priority_score: Optional[Decimal] = None
    relationship_trend: Optional[str] = None
    score_date: date
    calculation_method: str = "manual"  # 'manual', 'automatic', 'ai_calculated'
    factors: Optional[dict] = None
    manual_notes: Optional[str] = None

class ContactRelationshipScoreCreate(ContactRelationshipScoreBase):
    contact_id: int

class ContactRelationshipScoreUpdate(BaseModel):
    connection_strength: Optional[int] = Field(default=None, ge=1, le=10)
    engagement_score: Optional[Decimal] = None
    priority_score: Optional[Decimal] = None
    relationship_trend: Optional[str] = None
    factors: Optional[dict] = None
    manual_notes: Optional[str] = None

class ContactRelationshipScore(ContactRelationshipScoreBase):
    id: int
    contact_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ContactAIInsightBase(BaseModel):
    insight_type: str  # 'follow_up_suggestion', 'relationship_trend', 'engagement_pattern'
    insight_category: Optional[str] = None  # 'networking', 'personal', 'professional', 'social'
    priority: str = "medium"  # 'low', 'medium', 'high'
    title: Optional[str] = None
    description: Optional[str] = None
    actionable_suggestion: Optional[str] = None
    confidence_score: Optional[Decimal] = Field(default=None, ge=0, le=1)
    ai_model_version: Optional[str] = None
    data_sources: Optional[List[str]] = None
    insight_date: date
    expiry_date: Optional[date] = None

class ContactAIInsightCreate(ContactAIInsightBase):
    contact_id: int

class ContactAIInsightUpdate(BaseModel):
    status: Optional[str] = None  # 'active', 'dismissed', 'acted_upon'
    user_feedback: Optional[str] = None  # 'helpful', 'not_helpful', 'wrong'

class ContactAIInsight(ContactAIInsightBase):
    id: int
    contact_id: int
    status: str = "active"
    user_feedback: Optional[str] = None
    dismissed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ContactAIInsight(Base):
    __tablename__ = "contact_ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Insight Details
    insight_type = Column(String, index=True)  # 'follow_up_suggestion', 'relationship_trend', 'engagement_pattern'
    insight_category = Column(String)  # 'networking', 'personal', 'professional', 'social'
    priority = Column(String, default='medium', index=True)  # 'low', 'medium', 'high'
    
    # Content
    title = Column(String)
    description = Column(Text)
    actionable_suggestion = Column(Text)
    
    # AI Metadata
    confidence_score = Column(DECIMAL(3,2))  # 0.00 to 1.00
    ai_model_version = Column(String)
    data_sources = Column(JSON)  # What data was used to generate insight
    
    # Status
    status = Column(String, default='active')  # 'active', 'dismissed', 'acted_upon'
    user_feedback = Column(String)  # 'helpful', 'not_helpful', 'wrong'
    
    # Dates
    insight_date = Column(Date, nullable=False)
    expiry_date = Column(Date)  # When insight becomes irrelevant
    dismissed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="ai_insights")
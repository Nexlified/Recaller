from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ContactRelationshipScore(Base):
    __tablename__ = "contact_relationship_scores"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Score Metrics
    connection_strength = Column(Integer)
    engagement_score = Column(DECIMAL(5,2))
    priority_score = Column(DECIMAL(5,2))
    relationship_trend = Column(String)
    
    # Calculation Context
    score_date = Column(Date, nullable=False, index=True)
    calculation_method = Column(String)  # 'manual', 'automatic', 'ai_calculated'
    factors = Column(JSONB)  # What influenced the score
    
    # Notes
    manual_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="relationship_scores")
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.user import User

class ContactInteraction(Base):
    __tablename__ = "contact_interactions"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Interaction Details
    interaction_type = Column(String, nullable=False)  # 'call', 'text', 'email', 'meeting', 'social_media', 'event'
    interaction_method = Column(String)  # 'phone', 'video', 'in_person', 'whatsapp', 'linkedin'
    interaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer)  # Length of interaction
    
    # Context
    initiated_by = Column(String)  # 'me', 'them', 'mutual'
    interaction_quality = Column(Integer)  # 1-10 rating
    topics_discussed = Column(JSON)
    mood_assessment = Column(String)  # 'positive', 'neutral', 'negative'
    
    # Content
    summary = Column(Text)
    key_takeaways = Column(Text)
    follow_up_needed = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # Location Context
    location = Column(String)
    event_id = Column(Integer)  # Future: ForeignKey to events table
    
    # Metadata
    private_notes = Column(Text)
    attachments = Column(JSON)  # URLs to photos, documents, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="interactions")
    user = relationship("User")
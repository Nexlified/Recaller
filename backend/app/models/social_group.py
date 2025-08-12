from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.tenant import Tenant

class SocialGroup(Base):
    __tablename__ = "social_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group_type = Column(String, nullable=False)  # 'family', 'friends', 'work', 'hobby', 'professional', 'other'
    description = Column(Text)
    
    # Tenant relationship
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    primary_contacts = relationship("Contact", back_populates="primary_social_group")
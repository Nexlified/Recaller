from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    organization_type = Column(String(50), nullable=False)  # company, university, nonprofit, government
    industry = Column(String(100))
    size = Column(String(20))  # startup, small, medium, large, enterprise
    
    # Location
    city = Column(String(100))
    state = Column(String(50))
    country = Column(String(50))
    
    # Contact Information
    website = Column(String(255))
    description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="organizations")
    current_employees = relationship("Contact", foreign_keys="Contact.current_organization_id", back_populates="current_organization")
    alumni = relationship("Contact", foreign_keys="Contact.alma_mater_id", back_populates="alma_mater")
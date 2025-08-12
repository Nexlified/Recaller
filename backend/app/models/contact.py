from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True, server_default="1")
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", backref="contacts")
    created_by = relationship("User", backref="contacts")
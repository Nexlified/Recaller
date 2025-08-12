from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

DEFAULT_TENANT_ID = 1  # Default tenant ID for single-tenant mode

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Tenant relationship - using default tenant for now, but structure is ready for multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True, server_default=str(DEFAULT_TENANT_ID))
    tenant = relationship("Tenant", back_populates="users")
    networking_insights = relationship("NetworkingInsight", back_populates="user")

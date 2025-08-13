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
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="users")
    contacts = relationship(lambda: Contact, back_populates="created_by")
    networking_insights = relationship(lambda: NetworkingInsight, back_populates="user")
    tasks = relationship(lambda: Task, back_populates="user")
    task_categories = relationship(lambda: TaskCategory, back_populates="user")
    financial_accounts = relationship(lambda: FinancialAccount, back_populates="user")

# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.contact import Contact
from app.models.analytics import NetworkingInsight
from app.models.task import Task, TaskCategory
from app.models.financial_account import FinancialAccount

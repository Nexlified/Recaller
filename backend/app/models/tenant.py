from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships - using lambda to defer resolution
    contacts = relationship(lambda: Contact, back_populates="tenant")
    users = relationship(lambda: User, back_populates="tenant")
    organizations = relationship(lambda: Organization, back_populates="tenant")
    networking_insights = relationship(lambda: NetworkingInsight, back_populates="tenant")
    daily_metrics = relationship(lambda: DailyNetworkMetric, back_populates="tenant")
    tasks = relationship(lambda: Task, back_populates="tenant")
    task_categories = relationship(lambda: TaskCategory, back_populates="tenant")

# Import after class definition to avoid circular imports
from app.models.contact import Contact
from app.models.user import User
from app.models.organization import Organization
from app.models.analytics import NetworkingInsight, DailyNetworkMetric
from app.models.task import Task, TaskCategory

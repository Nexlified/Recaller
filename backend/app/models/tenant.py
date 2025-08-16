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
    
    # Relationships 
    contacts = relationship("Contact", back_populates="tenant")
    users = relationship("User", back_populates="tenant")
    organizations = relationship("Organization", back_populates="tenant")
    networking_insights = relationship("NetworkingInsight", back_populates="tenant")
    daily_metrics = relationship("DailyNetworkMetric", back_populates="tenant")
    tasks = relationship("Task", back_populates="tenant")
    task_categories = relationship("TaskCategory", back_populates="tenant")
    journal_entries = relationship("JournalEntry", back_populates="tenant")
    personal_reminders = relationship("PersonalReminder", back_populates="tenant")

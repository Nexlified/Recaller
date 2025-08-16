from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class ReminderType(enum.Enum):
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    DEATH_ANNIVERSARY = "death_anniversary"
    GRADUATION = "graduation"
    PROMOTION = "promotion"
    CUSTOM = "custom"


class ImportanceLevel(enum.IntEnum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class PersonalReminder(Base):
    __tablename__ = "personal_reminders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    reminder_type = Column(String(50), nullable=False, default=ReminderType.CUSTOM.value, index=True)
    
    # Contact association (optional - can be general reminders too)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    
    # Event details
    event_date = Column(Date, nullable=False, index=True)
    is_recurring = Column(Boolean, nullable=False, default=True)  # Most personal dates recur yearly
    
    # Reminder configuration (JSON format for flexibility)
    # Example: {"week_before": true, "day_before": true, "same_day": true, "custom_days": [7, 3, 1]}
    reminder_preferences = Column(JSON, nullable=False, default=dict)
    
    # Notification methods (JSON format)
    # Example: {"email": true, "app_notification": true, "task_creation": true}
    notification_methods = Column(JSON, nullable=False, default=dict)
    
    # Importance and tracking
    importance_level = Column(Integer, nullable=False, default=ImportanceLevel.MEDIUM.value)
    last_celebrated_year = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="personal_reminders")
    user = relationship(lambda: User, back_populates="personal_reminders")
    contact = relationship(lambda: Contact, back_populates="personal_reminders")


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.contact import Contact
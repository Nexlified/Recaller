from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrenceType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Status and Priority
    status = Column(String(20), nullable=False, default=TaskStatus.PENDING.value, index=True)
    priority = Column(String(10), nullable=False, default=TaskPriority.MEDIUM.value, index=True)
    
    # Dates
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    
    # Recurrence
    is_recurring = Column(Boolean, nullable=False, default=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # For tracking recurring task instances
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships 
    tenant = relationship("Tenant", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
    task_contacts = relationship("TaskContact", back_populates="task", cascade="all, delete-orphan")
    task_recurrence = relationship("TaskRecurrence", back_populates="task", cascade="all, delete-orphan", uselist=False)
    task_category_assignments = relationship("TaskCategoryAssignment", back_populates="task", cascade="all, delete-orphan")


class TaskContact(Base):
    __tablename__ = "task_contacts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationship context
    relationship_context = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="task_contacts")
    contact = relationship("Contact", back_populates="task_contacts")
    
    # Unique constraint to prevent duplicate task-contact pairs
    __table_args__ = (
        UniqueConstraint('task_id', 'contact_id', name='uq_task_contacts_task_contact'),
    )


class TaskRecurrence(Base):
    __tablename__ = "task_recurrence"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recurrence Pattern
    recurrence_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly, custom
    recurrence_interval = Column(Integer, nullable=False, default=1)  # every N units
    
    # Weekly recurrence - days of week (e.g., "1,3,5" for Mon, Wed, Fri)
    days_of_week = Column(String(7))
    
    # Monthly recurrence - day of month
    day_of_month = Column(Integer)
    
    # End conditions
    end_date = Column(Date)
    max_occurrences = Column(Integer)
    
    # Lead time for creating next task
    lead_time_days = Column(Integer, nullable=False, default=0)
    
    # Generation tracking fields
    last_generated_at = Column(DateTime(timezone=True))
    next_generation_at = Column(DateTime(timezone=True))
    generation_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="task_recurrence")


class TaskCategory(Base):
    __tablename__ = "task_categories"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(100), nullable=False)
    color = Column(String(7))  # hex color code
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships 
    tenant = relationship("Tenant", back_populates="task_categories")
    user = relationship("User", back_populates="task_categories")
    task_category_assignments = relationship("TaskCategoryAssignment", back_populates="category", cascade="all, delete-orphan")
    
    # Unique constraint to prevent duplicate categories per user
    __table_args__ = (
        UniqueConstraint('tenant_id', 'user_id', 'name', name='uq_task_categories_tenant_user_name'),
    )


class TaskCategoryAssignment(Base):
    __tablename__ = "task_category_assignments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("task_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="task_category_assignments")
    category = relationship("TaskCategory", back_populates="task_category_assignments")
    
    # Unique constraint to prevent duplicate task-category pairs
    __table_args__ = (
        UniqueConstraint('task_id', 'category_id', name='uq_task_category_assignments_task_category'),
    )



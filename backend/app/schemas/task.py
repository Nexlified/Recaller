from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum

# Import the model enums for validation
from app.models.task import TaskStatus, TaskPriority, RecurrenceType


class TaskStatusEnum(str, Enum):
    PENDING = TaskStatus.PENDING.value
    IN_PROGRESS = TaskStatus.IN_PROGRESS.value
    COMPLETED = TaskStatus.COMPLETED.value
    CANCELLED = TaskStatus.CANCELLED.value


class TaskPriorityEnum(str, Enum):
    LOW = TaskPriority.LOW.value
    MEDIUM = TaskPriority.MEDIUM.value
    HIGH = TaskPriority.HIGH.value


class RecurrenceTypeEnum(str, Enum):
    DAILY = RecurrenceType.DAILY.value
    WEEKLY = RecurrenceType.WEEKLY.value
    MONTHLY = RecurrenceType.MONTHLY.value
    YEARLY = RecurrenceType.YEARLY.value
    CUSTOM = RecurrenceType.CUSTOM.value


# Task Recurrence Schemas
class TaskRecurrenceBase(BaseModel):
    recurrence_type: RecurrenceTypeEnum
    recurrence_interval: int = Field(default=1, ge=1)
    days_of_week: Optional[str] = Field(default=None, max_length=7)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[date] = None
    max_occurrences: Optional[int] = Field(default=None, ge=1)
    lead_time_days: int = Field(default=0, ge=0)


class TaskRecurrenceCreate(TaskRecurrenceBase):
    pass


class TaskRecurrenceUpdate(BaseModel):
    recurrence_type: Optional[RecurrenceTypeEnum] = None
    recurrence_interval: Optional[int] = Field(default=None, ge=1)
    days_of_week: Optional[str] = Field(default=None, max_length=7)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[date] = None
    max_occurrences: Optional[int] = Field(default=None, ge=1)
    lead_time_days: Optional[int] = Field(default=None, ge=0)


class TaskRecurrence(TaskRecurrenceBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Task Category Schemas
class TaskCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = None


class TaskCategoryCreate(TaskCategoryBase):
    pass


class TaskCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = None


class TaskCategory(TaskCategoryBase):
    id: int
    tenant_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Forward reference for Contact model - will be resolved after import
class Contact(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    category_ids: Optional[List[int]] = Field(default_factory=list)
    contact_ids: Optional[List[int]] = Field(default_factory=list)
    recurrence: Optional[TaskRecurrenceCreate] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class Task(TaskBase):
    id: int
    tenant_id: int
    user_id: int
    is_recurring: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: List[TaskCategory] = Field(default_factory=list)
    contacts: List[Contact] = Field(default_factory=list)
    recurrence: Optional[TaskRecurrence] = None

    class Config:
        from_attributes = True


# Task Contact Association Schema
class TaskContactCreate(BaseModel):
    contact_id: int
    relationship_context: Optional[str] = None


class TaskContactUpdate(BaseModel):
    relationship_context: Optional[str] = None


# Task Category Assignment Schema
class TaskCategoryAssignmentCreate(BaseModel):
    category_id: int


# Bulk Operation Schemas
class TaskBulkUpdate(BaseModel):
    task_ids: List[int]
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None


# Search and Filter Schemas
class TaskSearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    category_ids: Optional[List[int]] = None
    contact_ids: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TaskFilter(BaseModel):
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    category_ids: Optional[List[int]] = None
    contact_ids: Optional[List[int]] = None
    due_date_start: Optional[date] = None
    due_date_end: Optional[date] = None
    is_recurring: Optional[bool] = None
    is_overdue: Optional[bool] = None
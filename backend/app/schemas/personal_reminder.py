from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum

# Import the model enums for validation
from app.models.personal_reminder import ReminderType, ImportanceLevel


class ReminderTypeEnum(str, Enum):
    BIRTHDAY = ReminderType.BIRTHDAY.value
    ANNIVERSARY = ReminderType.ANNIVERSARY.value
    DEATH_ANNIVERSARY = ReminderType.DEATH_ANNIVERSARY.value
    GRADUATION = ReminderType.GRADUATION.value
    PROMOTION = ReminderType.PROMOTION.value
    CUSTOM = ReminderType.CUSTOM.value


class ImportanceLevelEnum(int, Enum):
    VERY_LOW = ImportanceLevel.VERY_LOW.value
    LOW = ImportanceLevel.LOW.value
    MEDIUM = ImportanceLevel.MEDIUM.value
    HIGH = ImportanceLevel.HIGH.value
    VERY_HIGH = ImportanceLevel.VERY_HIGH.value


# Personal Reminder Schemas
class PersonalReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_type: ReminderTypeEnum = ReminderTypeEnum.CUSTOM
    contact_id: Optional[int] = None
    event_date: date
    is_recurring: bool = True
    reminder_preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_methods: Dict[str, Any] = Field(default_factory=dict)
    importance_level: ImportanceLevelEnum = ImportanceLevelEnum.MEDIUM
    last_celebrated_year: Optional[int] = None
    is_active: bool = True

    @validator('reminder_preferences')
    def validate_reminder_preferences(cls, v):
        """Validate reminder preferences structure."""
        if not isinstance(v, dict):
            raise ValueError('reminder_preferences must be a dict')
        
        # Valid keys for reminder preferences
        valid_keys = {'week_before', 'day_before', 'same_day', 'custom_days'}
        invalid_keys = set(v.keys()) - valid_keys
        if invalid_keys:
            raise ValueError(f'Invalid reminder preference keys: {invalid_keys}')
        
        # Validate custom_days if present
        if 'custom_days' in v and v['custom_days'] is not None:
            if not isinstance(v['custom_days'], list):
                raise ValueError('custom_days must be a list of integers')
            if not all(isinstance(day, int) and day > 0 for day in v['custom_days']):
                raise ValueError('custom_days must contain positive integers')
        
        return v

    @validator('notification_methods')
    def validate_notification_methods(cls, v):
        """Validate notification methods structure."""
        if not isinstance(v, dict):
            raise ValueError('notification_methods must be a dict')
        
        # Valid keys for notification methods
        valid_keys = {'email', 'app_notification', 'task_creation'}
        invalid_keys = set(v.keys()) - valid_keys
        if invalid_keys:
            raise ValueError(f'Invalid notification method keys: {invalid_keys}')
        
        return v

    @validator('last_celebrated_year')
    def validate_last_celebrated_year(cls, v):
        """Validate that last_celebrated_year is reasonable."""
        if v is not None:
            current_year = date.today().year
            if v > current_year:
                raise ValueError('last_celebrated_year cannot be in the future')
            if v < 1900:
                raise ValueError('last_celebrated_year must be after 1900')
        return v


class PersonalReminderCreate(PersonalReminderBase):
    # Set default reminder preferences for new reminders
    reminder_preferences: Dict[str, Any] = Field(
        default_factory=lambda: {
            "week_before": True,
            "day_before": True,
            "same_day": True
        }
    )
    # Set default notification methods for new reminders
    notification_methods: Dict[str, Any] = Field(
        default_factory=lambda: {
            "email": False,
            "app_notification": True,
            "task_creation": True
        }
    )


class PersonalReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_type: Optional[ReminderTypeEnum] = None
    contact_id: Optional[int] = None
    event_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    reminder_preferences: Optional[Dict[str, Any]] = None
    notification_methods: Optional[Dict[str, Any]] = None
    importance_level: Optional[ImportanceLevelEnum] = None
    last_celebrated_year: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('reminder_preferences')
    def validate_reminder_preferences(cls, v):
        """Validate reminder preferences structure."""
        if v is not None:
            return PersonalReminderBase.validate_reminder_preferences(v)
        return v

    @validator('notification_methods')
    def validate_notification_methods(cls, v):
        """Validate notification methods structure."""
        if v is not None:
            return PersonalReminderBase.validate_notification_methods(v)
        return v

    @validator('last_celebrated_year')
    def validate_last_celebrated_year(cls, v):
        """Validate that last_celebrated_year is reasonable."""
        if v is not None:
            return PersonalReminderBase.validate_last_celebrated_year(v)
        return v


class PersonalReminder(PersonalReminderBase):
    id: int
    tenant_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Contact information for reminder display
class ReminderContact(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    family_nickname: Optional[str] = None

    class Config:
        from_attributes = True


# Personal reminder with contact information
class PersonalReminderWithContact(PersonalReminder):
    contact: Optional[ReminderContact] = None


# Upcoming reminder information for dashboard
class UpcomingReminder(BaseModel):
    reminder_id: int
    title: str
    description: Optional[str] = None
    reminder_type: ReminderTypeEnum
    event_date: date
    days_until: int
    importance_level: ImportanceLevelEnum
    contact: Optional[ReminderContact] = None
    years_since: Optional[int] = None  # For anniversaries/birthdays


# Bulk operations
class PersonalReminderBulkUpdate(BaseModel):
    reminder_ids: List[int]
    is_active: Optional[bool] = None
    importance_level: Optional[ImportanceLevelEnum] = None


# Filter and search schemas
class PersonalReminderFilter(BaseModel):
    reminder_type: Optional[ReminderTypeEnum] = None
    importance_level: Optional[ImportanceLevelEnum] = None
    contact_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_recurring: Optional[bool] = None
    event_date_start: Optional[date] = None
    event_date_end: Optional[date] = None
    days_ahead: Optional[int] = Field(None, ge=1, le=365)


class PersonalReminderSearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    reminder_type: Optional[ReminderTypeEnum] = None
    importance_level: Optional[ImportanceLevelEnum] = None
    is_active: Optional[bool] = None
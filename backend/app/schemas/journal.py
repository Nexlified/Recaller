from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum

# Import the model enums for validation
from app.models.journal import JournalEntryMood
from app.core.validation import (
    create_journal_content_validator,
    create_journal_title_validator,
    create_journal_location_validator,
    create_journal_weather_validator,
    create_entry_date_validator,
    create_tag_name_validator,
    create_tag_color_validator,
)


class JournalEntryMoodEnum(str, Enum):
    """Mood/sentiment options for journal entries."""
    VERY_HAPPY = JournalEntryMood.VERY_HAPPY.value
    HAPPY = JournalEntryMood.HAPPY.value
    CONTENT = JournalEntryMood.CONTENT.value
    NEUTRAL = JournalEntryMood.NEUTRAL.value
    ANXIOUS = JournalEntryMood.ANXIOUS.value
    SAD = JournalEntryMood.SAD.value
    VERY_SAD = JournalEntryMood.VERY_SAD.value
    ANGRY = JournalEntryMood.ANGRY.value
    EXCITED = JournalEntryMood.EXCITED.value
    GRATEFUL = JournalEntryMood.GRATEFUL.value


# Journal Tag Schemas
class JournalTagBase(BaseModel):
    """Base schema for journal tags."""
    tag_name: str = Field(..., min_length=1, max_length=50)
    tag_color: Optional[str] = Field(default=None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    # Validators
    _validate_tag_name = validator('tag_name', allow_reuse=True)(create_tag_name_validator())
    _validate_tag_color = validator('tag_color', allow_reuse=True)(create_tag_color_validator())


class JournalTagCreate(JournalTagBase):
    """Schema for creating a journal tag."""
    pass


class JournalTagUpdate(BaseModel):
    """Schema for updating a journal tag."""
    tag_name: Optional[str] = Field(None, min_length=1, max_length=50)
    tag_color: Optional[str] = Field(default=None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    # Validators
    _validate_tag_name = validator('tag_name', allow_reuse=True)(create_tag_name_validator())
    _validate_tag_color = validator('tag_color', allow_reuse=True)(create_tag_color_validator())


class JournalTag(JournalTagBase):
    """Schema for journal tag responses."""
    id: int
    journal_entry_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Journal Attachment Schemas
class JournalAttachmentBase(BaseModel):
    """Base schema for journal attachments."""
    original_filename: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class JournalAttachmentCreate(JournalAttachmentBase):
    """Schema for creating a journal attachment (file upload will set other fields)."""
    pass


class JournalAttachmentUpdate(BaseModel):
    """Schema for updating a journal attachment."""
    description: Optional[str] = None


class JournalAttachment(JournalAttachmentBase):
    """Schema for journal attachment responses."""
    id: int
    journal_entry_id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    is_encrypted: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    """Base schema for journal entries."""
    title: Optional[str] = Field(default=None, max_length=255)
    content: str = Field(..., min_length=1)
    entry_date: date
    mood: Optional[JournalEntryMoodEnum] = None
    location: Optional[str] = Field(default=None, max_length=255)
    weather: Optional[str] = Field(default=None, max_length=100)
    is_private: bool = Field(default=True)
    
    # Validators for security and data integrity
    _validate_title = validator('title', allow_reuse=True)(create_journal_title_validator())
    _validate_content = validator('content', allow_reuse=True)(create_journal_content_validator())
    _validate_entry_date = validator('entry_date', allow_reuse=True)(create_entry_date_validator())
    _validate_location = validator('location', allow_reuse=True)(create_journal_location_validator())
    _validate_weather = validator('weather', allow_reuse=True)(create_journal_weather_validator())


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry."""
    tags: Optional[List[JournalTagCreate]] = Field(default_factory=list)


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    entry_date: Optional[date] = None
    mood: Optional[JournalEntryMoodEnum] = None
    location: Optional[str] = Field(default=None, max_length=255)
    weather: Optional[str] = Field(default=None, max_length=100)
    is_private: Optional[bool] = None
    is_archived: Optional[bool] = None
    
    # Validators for security and data integrity
    _validate_title = validator('title', allow_reuse=True)(create_journal_title_validator())
    _validate_content = validator('content', allow_reuse=True)(create_journal_content_validator())
    _validate_entry_date = validator('entry_date', allow_reuse=True)(create_entry_date_validator())
    _validate_location = validator('location', allow_reuse=True)(create_journal_location_validator())
    _validate_weather = validator('weather', allow_reuse=True)(create_journal_weather_validator())


class JournalEntryInDBBase(JournalEntryBase):
    """Base schema for journal entries with database fields."""
    id: int
    tenant_id: int
    user_id: int
    is_archived: bool
    entry_version: int
    parent_entry_id: Optional[int]
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class JournalEntry(JournalEntryInDBBase):
    """Schema for journal entry responses."""
    tags: List[JournalTag] = Field(default_factory=list)
    attachments: List[JournalAttachment] = Field(default_factory=list)


class JournalEntryInDB(JournalEntryInDBBase):
    """Schema for journal entries in database operations."""
    pass


# Journal Entry with minimal data for lists
class JournalEntrySummary(BaseModel):
    """Minimal journal entry schema for listing."""
    id: int
    title: Optional[str]
    entry_date: date
    mood: Optional[JournalEntryMoodEnum]
    is_private: bool
    is_archived: bool
    created_at: datetime
    tag_count: int = 0
    attachment_count: int = 0

    class Config:
        from_attributes = True


# Search and Filter Schemas
class JournalEntryFilter(BaseModel):
    """Schema for filtering journal entries."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    mood: Optional[JournalEntryMoodEnum] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    has_attachments: Optional[bool] = None
    is_archived: Optional[bool] = None
    search_content: Optional[str] = Field(default=None, min_length=1)


class JournalEntrySearchQuery(BaseModel):
    """Schema for searching journal entries."""
    query: str = Field(..., min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    mood: Optional[JournalEntryMoodEnum] = None
    tags: Optional[List[str]] = Field(default_factory=list)


# Bulk Operations
class JournalEntryBulkUpdate(BaseModel):
    """Schema for bulk updating journal entries."""
    entry_ids: List[int] = Field(..., min_items=1)
    is_archived: Optional[bool] = None
    is_private: Optional[bool] = None


class JournalEntryBulkTag(BaseModel):
    """Schema for bulk tagging journal entries."""
    entry_ids: List[int] = Field(..., min_items=1)
    tags_to_add: Optional[List[JournalTagCreate]] = Field(default_factory=list)
    tags_to_remove: Optional[List[str]] = Field(default_factory=list)


# Analytics and Statistics
class JournalEntryStats(BaseModel):
    """Schema for journal entry statistics."""
    total_entries: int
    entries_this_month: int
    entries_this_week: int
    average_words_per_entry: float
    most_common_mood: Optional[JournalEntryMoodEnum]
    most_used_tags: List[str] = Field(default_factory=list)
    longest_streak_days: int
    current_streak_days: int
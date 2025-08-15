from typing import Optional, List, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum

# Import the model enums for validation
from app.models.journal import JournalEntryMood, WeatherImpact
from app.core.validation import (
    create_journal_content_validator,
    create_journal_title_validator,
    create_journal_location_validator,
    create_journal_weather_validator,
    create_entry_date_validator,
    create_tag_name_validator,
    create_tag_color_validator,
    create_rating_validator,
    create_positive_integer_validator,
    create_weather_impact_validator,
    create_significant_events_validator,
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


class WeatherImpactEnum(str, Enum):
    """Weather impact options for journal entries."""
    POSITIVE = WeatherImpact.POSITIVE.value
    NEUTRAL = WeatherImpact.NEUTRAL.value
    NEGATIVE = WeatherImpact.NEGATIVE.value


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
    
    # Day quality and life metrics (all optional)
    day_quality_rating: Optional[int] = Field(default=None, ge=1, le=10)
    energy_level: Optional[int] = Field(default=None, ge=1, le=10)
    stress_level: Optional[int] = Field(default=None, ge=1, le=10)
    productivity_level: Optional[int] = Field(default=None, ge=1, le=10)
    social_interactions_count: Optional[int] = Field(default=None, ge=0)
    exercise_minutes: Optional[int] = Field(default=None, ge=0)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=10)
    weather_impact: Optional[WeatherImpactEnum] = None
    significant_events: Optional[List[Any]] = Field(default=None)
    
    # Validators for security and data integrity
    _validate_title = validator('title', allow_reuse=True)(create_journal_title_validator())
    _validate_content = validator('content', allow_reuse=True)(create_journal_content_validator())
    _validate_entry_date = validator('entry_date', allow_reuse=True)(create_entry_date_validator())
    _validate_location = validator('location', allow_reuse=True)(create_journal_location_validator())
    _validate_weather = validator('weather', allow_reuse=True)(create_journal_weather_validator())
    
    # Validators for new life metrics fields
    _validate_day_quality_rating = validator('day_quality_rating', allow_reuse=True)(create_rating_validator('Day quality rating'))
    _validate_energy_level = validator('energy_level', allow_reuse=True)(create_rating_validator('Energy level'))
    _validate_stress_level = validator('stress_level', allow_reuse=True)(create_rating_validator('Stress level'))
    _validate_productivity_level = validator('productivity_level', allow_reuse=True)(create_rating_validator('Productivity level'))
    _validate_sleep_quality = validator('sleep_quality', allow_reuse=True)(create_rating_validator('Sleep quality'))
    _validate_social_interactions_count = validator('social_interactions_count', allow_reuse=True)(create_positive_integer_validator('Social interactions count'))
    _validate_exercise_minutes = validator('exercise_minutes', allow_reuse=True)(create_positive_integer_validator('Exercise minutes'))
    _validate_significant_events = validator('significant_events', allow_reuse=True)(create_significant_events_validator())


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
    
    # Day quality and life metrics (all optional for updates)
    day_quality_rating: Optional[int] = Field(default=None, ge=1, le=10)
    energy_level: Optional[int] = Field(default=None, ge=1, le=10)
    stress_level: Optional[int] = Field(default=None, ge=1, le=10)
    productivity_level: Optional[int] = Field(default=None, ge=1, le=10)
    social_interactions_count: Optional[int] = Field(default=None, ge=0)
    exercise_minutes: Optional[int] = Field(default=None, ge=0)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=10)
    weather_impact: Optional[WeatherImpactEnum] = None
    significant_events: Optional[List[Any]] = Field(default=None)
    
    # Validators for security and data integrity
    _validate_title = validator('title', allow_reuse=True)(create_journal_title_validator())
    _validate_content = validator('content', allow_reuse=True)(create_journal_content_validator())
    _validate_entry_date = validator('entry_date', allow_reuse=True)(create_entry_date_validator())
    _validate_location = validator('location', allow_reuse=True)(create_journal_location_validator())
    _validate_weather = validator('weather', allow_reuse=True)(create_journal_weather_validator())
    
    # Validators for new life metrics fields
    _validate_day_quality_rating = validator('day_quality_rating', allow_reuse=True)(create_rating_validator('Day quality rating'))
    _validate_energy_level = validator('energy_level', allow_reuse=True)(create_rating_validator('Energy level'))
    _validate_stress_level = validator('stress_level', allow_reuse=True)(create_rating_validator('Stress level'))
    _validate_productivity_level = validator('productivity_level', allow_reuse=True)(create_rating_validator('Productivity level'))
    _validate_sleep_quality = validator('sleep_quality', allow_reuse=True)(create_rating_validator('Sleep quality'))
    _validate_social_interactions_count = validator('social_interactions_count', allow_reuse=True)(create_positive_integer_validator('Social interactions count'))
    _validate_exercise_minutes = validator('exercise_minutes', allow_reuse=True)(create_positive_integer_validator('Exercise minutes'))
    _validate_significant_events = validator('significant_events', allow_reuse=True)(create_significant_events_validator())


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


# Pagination Schemas
class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class JournalEntryListResponse(BaseModel):
    """Schema for paginated journal entry responses."""
    items: List[JournalEntrySummary]
    pagination: PaginationMeta


class JournalEntryBulkResponse(BaseModel):
    """Schema for bulk operation responses."""
    success_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)


# Version Management Schemas

class JournalEntryVersion(BaseModel):
    """Schema for journal entry version information."""
    id: int
    entry_version: int
    title: Optional[str]
    content: str
    entry_date: date
    mood: Optional[JournalEntryMoodEnum]
    location: Optional[str]
    weather: Optional[str]
    is_private: bool
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime]
    parent_entry_id: Optional[int]
    
    class Config:
        from_attributes = True


class JournalEntryVersionSummary(BaseModel):
    """Summary schema for journal entry versions."""
    id: int
    entry_version: int
    title: Optional[str]
    created_at: datetime
    changes_summary: Optional[str] = None  # Brief description of changes
    
    class Config:
        from_attributes = True


class JournalEntryVersionHistory(BaseModel):
    """Schema for journal entry version history."""
    current_version: JournalEntryVersion
    versions: List[JournalEntryVersionSummary]
    total_versions: int


class JournalEntryRevertRequest(BaseModel):
    """Schema for reverting to a specific version."""
    version: int = Field(..., ge=1, description="Version number to revert to")


class JournalEntryVersionResponse(BaseModel):
    """Schema for version operation responses."""
    success: bool
    message: str
    version: Optional[JournalEntryVersion] = None
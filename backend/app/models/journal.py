from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class JournalEntryMood(enum.Enum):
    """Mood/sentiment options for journal entries."""
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    CONTENT = "content"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    SAD = "sad"
    VERY_SAD = "very_sad"
    ANGRY = "angry"
    EXCITED = "excited"
    GRATEFUL = "grateful"


class WeatherImpact(enum.Enum):
    """Weather impact on day quality."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class JournalEntry(Base):
    """Main journal entry model."""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Core content
    title = Column(String(255))  # Optional title for the entry
    content = Column(Text, nullable=False)  # Main journal content
    
    # Entry metadata
    entry_date = Column(Date, nullable=False, index=True)  # Date this entry represents
    mood = Column(String(20), index=True)  # Optional mood/sentiment
    location = Column(String(255))  # Optional location
    weather = Column(String(100))  # Optional weather context
    
    # Day quality and life metrics
    day_quality_rating = Column(Integer)  # 1-10 scale for overall day assessment
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    productivity_level = Column(Integer)  # 1-10 scale
    social_interactions_count = Column(Integer)  # Number of social interactions
    exercise_minutes = Column(Integer)  # Minutes of exercise
    sleep_quality = Column(Integer)  # 1-10 scale for previous night
    weather_impact = Column(String(20))  # positive, neutral, negative
    significant_events = Column(JSON)  # JSON array of key events
    
    # Privacy and visibility
    is_private = Column(Boolean, nullable=False, default=True)
    is_archived = Column(Boolean, nullable=False, default=False, index=True)
    
    # Future features support
    entry_version = Column(Integer, nullable=False, default=1)
    parent_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)  # For versioning
    is_encrypted = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="journal_entries")
    user = relationship(lambda: User, back_populates="journal_entries")
    tags = relationship("JournalTag", back_populates="journal_entry", cascade="all, delete-orphan")
    attachments = relationship("JournalAttachment", back_populates="journal_entry", cascade="all, delete-orphan")
    
    # Self-referential relationship for versioning
    parent_entry = relationship("JournalEntry", remote_side=[id], backref="child_versions")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('ix_journal_entries_tenant_user_date', 'tenant_id', 'user_id', 'entry_date'),
        Index('ix_journal_entries_user_archived', 'user_id', 'is_archived'),
        Index('ix_journal_entries_day_quality_rating', 'day_quality_rating'),
        Index('ix_journal_entries_energy_level', 'energy_level'),
        Index('ix_journal_entries_weather_impact', 'weather_impact'),
    )


class JournalTag(Base):
    """Tags for categorizing journal entries."""
    __tablename__ = "journal_tags"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tag information
    tag_name = Column(String(50), nullable=False, index=True)
    tag_color = Column(String(7))  # Hex color code like #FF5733
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="tags")
    
    # Unique constraint to prevent duplicate tags per entry
    __table_args__ = (
        UniqueConstraint('journal_entry_id', 'tag_name', name='uq_journal_tags_entry_name'),
    )


class JournalAttachment(Base):
    """File attachments for journal entries (photos, documents, etc.)."""
    __tablename__ = "journal_attachments"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path from storage root
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    
    # Attachment metadata
    description = Column(Text)  # Optional description
    is_encrypted = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="attachments")


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
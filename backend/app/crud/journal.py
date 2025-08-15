from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from app.models.journal import JournalEntry, JournalTag, JournalAttachment
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalTagCreate,
    JournalEntryMoodEnum, JournalEntryFilter
)


def get_journal_entry(db: Session, entry_id: int, user_id: int, tenant_id: int) -> Optional[JournalEntry]:
    """Get a single journal entry by ID with user and tenant filtering."""
    return db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id
    ).first()


def get_journal_entry_with_relations(db: Session, entry_id: int, user_id: int, tenant_id: int) -> Optional[JournalEntry]:
    """Get a journal entry with all its relationships loaded."""
    return db.query(JournalEntry).options(
        joinedload(JournalEntry.tags),
        joinedload(JournalEntry.attachments)
    ).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id
    ).first()


def get_by_user(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int, 
    skip: int = 0, 
    limit: int = 100,
    include_archived: bool = False
) -> List[JournalEntry]:
    """Get all journal entries for a specific user."""
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id
    )
    
    if not include_archived:
        query = query.filter(JournalEntry.is_archived == False)
    
    return query.order_by(desc(JournalEntry.entry_date), desc(JournalEntry.created_at)).offset(skip).limit(limit).all()


def get_by_date_range(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    start_date: date,
    end_date: date,
    include_archived: bool = False
) -> List[JournalEntry]:
    """Get journal entries within a date range."""
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.entry_date >= start_date,
        JournalEntry.entry_date <= end_date
    )
    
    if not include_archived:
        query = query.filter(JournalEntry.is_archived == False)
    
    return query.order_by(desc(JournalEntry.entry_date)).all()


def get_by_mood(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    mood: JournalEntryMoodEnum,
    skip: int = 0,
    limit: int = 100
) -> List[JournalEntry]:
    """Get journal entries by mood."""
    return db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.mood == mood.value,
        JournalEntry.is_archived == False
    ).order_by(desc(JournalEntry.entry_date)).offset(skip).limit(limit).all()


def search_entries(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    search_text: str,
    skip: int = 0,
    limit: int = 100
) -> List[JournalEntry]:
    """Search journal entries by content."""
    return db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        or_(
            JournalEntry.content.ilike(f"%{search_text}%"),
            JournalEntry.title.ilike(f"%{search_text}%")
        ),
        JournalEntry.is_archived == False
    ).order_by(desc(JournalEntry.entry_date)).offset(skip).limit(limit).all()


def get_entries_with_tags(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    tag_names: List[str],
    skip: int = 0,
    limit: int = 100
) -> List[JournalEntry]:
    """Get journal entries that have any of the specified tags."""
    return db.query(JournalEntry).join(JournalTag).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalTag.tag_name.in_(tag_names),
        JournalEntry.is_archived == False
    ).order_by(desc(JournalEntry.entry_date)).offset(skip).limit(limit).all()


def create_journal_entry(
    db: Session,
    *,
    journal_entry: JournalEntryCreate,
    user_id: int,
    tenant_id: int
) -> JournalEntry:
    """Create a new journal entry."""
    db_entry = JournalEntry(
        tenant_id=tenant_id,
        user_id=user_id,
        title=journal_entry.title,
        content=journal_entry.content,
        entry_date=journal_entry.entry_date,
        mood=journal_entry.mood.value if journal_entry.mood else None,
        location=journal_entry.location,
        weather=journal_entry.weather,
        is_private=journal_entry.is_private
    )
    
    db.add(db_entry)
    db.flush()  # Get the ID without committing
    
    # Add tags if provided
    if journal_entry.tags:
        for tag_data in journal_entry.tags:
            tag = JournalTag(
                journal_entry_id=db_entry.id,
                tag_name=tag_data.tag_name,
                tag_color=tag_data.tag_color
            )
            db.add(tag)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry


def update_journal_entry(
    db: Session,
    *,
    entry_id: int,
    user_id: int,
    tenant_id: int,
    journal_entry: JournalEntryUpdate
) -> Optional[JournalEntry]:
    """Update a journal entry."""
    db_entry = get_journal_entry(db, entry_id=entry_id, user_id=user_id, tenant_id=tenant_id)
    if not db_entry:
        return None
    
    update_data = journal_entry.dict(exclude_unset=True)
    if "mood" in update_data and update_data["mood"]:
        update_data["mood"] = update_data["mood"].value
    
    for field, value in update_data.items():
        setattr(db_entry, field, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_journal_entry(
    db: Session,
    *,
    entry_id: int,
    user_id: int,
    tenant_id: int
) -> bool:
    """Delete a journal entry (hard delete)."""
    db_entry = get_journal_entry(db, entry_id=entry_id, user_id=user_id, tenant_id=tenant_id)
    if not db_entry:
        return False
    
    db.delete(db_entry)
    db.commit()
    return True


def archive_journal_entry(
    db: Session,
    *,
    entry_id: int,
    user_id: int,
    tenant_id: int,
    archive: bool = True
) -> Optional[JournalEntry]:
    """Archive or unarchive a journal entry (soft delete)."""
    db_entry = get_journal_entry(db, entry_id=entry_id, user_id=user_id, tenant_id=tenant_id)
    if not db_entry:
        return None
    
    db_entry.is_archived = archive
    db.commit()
    db.refresh(db_entry)
    return db_entry


def add_tag_to_entry(
    db: Session,
    *,
    entry_id: int,
    user_id: int,
    tenant_id: int,
    tag: JournalTagCreate
) -> Optional[JournalTag]:
    """Add a tag to a journal entry."""
    # Verify the entry exists and belongs to the user
    db_entry = get_journal_entry(db, entry_id=entry_id, user_id=user_id, tenant_id=tenant_id)
    if not db_entry:
        return None
    
    # Check if tag already exists
    existing_tag = db.query(JournalTag).filter(
        JournalTag.journal_entry_id == entry_id,
        JournalTag.tag_name == tag.tag_name
    ).first()
    
    if existing_tag:
        return existing_tag
    
    # Create new tag
    db_tag = JournalTag(
        journal_entry_id=entry_id,
        tag_name=tag.tag_name,
        tag_color=tag.tag_color
    )
    
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def remove_tag_from_entry(
    db: Session,
    *,
    entry_id: int,
    user_id: int,
    tenant_id: int,
    tag_name: str
) -> bool:
    """Remove a tag from a journal entry."""
    # Verify the entry exists and belongs to the user
    db_entry = get_journal_entry(db, entry_id=entry_id, user_id=user_id, tenant_id=tenant_id)
    if not db_entry:
        return False
    
    # Find and delete the tag
    db_tag = db.query(JournalTag).filter(
        JournalTag.journal_entry_id == entry_id,
        JournalTag.tag_name == tag_name
    ).first()
    
    if not db_tag:
        return False
    
    db.delete(db_tag)
    db.commit()
    return True


def get_user_stats(db: Session, *, user_id: int, tenant_id: int) -> Dict[str, Any]:
    """Get journal statistics for a user."""
    total_entries = db.query(func.count(JournalEntry.id)).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.is_archived == False
    ).scalar() or 0
    
    # Get mood distribution
    mood_stats = db.query(
        JournalEntry.mood,
        func.count(JournalEntry.id)
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.is_archived == False,
        JournalEntry.mood.is_not(None)
    ).group_by(JournalEntry.mood).all()
    
    # Get most used tags
    tag_stats = db.query(
        JournalTag.tag_name,
        func.count(JournalTag.id)
    ).join(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.is_archived == False
    ).group_by(JournalTag.tag_name).order_by(desc(func.count(JournalTag.id))).limit(10).all()
    
    return {
        "total_entries": total_entries,
        "mood_distribution": {mood: count for mood, count in mood_stats},
        "most_used_tags": [{"tag": tag, "count": count} for tag, count in tag_stats]
    }
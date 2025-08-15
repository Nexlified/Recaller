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


# New optimized functions for performance

def get_entry_count(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int, 
    include_archived: bool = False,
    search_text: Optional[str] = None,
    mood: Optional[JournalEntryMoodEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """Get count of journal entries matching the given filters."""
    query = db.query(func.count(JournalEntry.id)).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id
    )
    
    if not include_archived:
        query = query.filter(JournalEntry.is_archived == False)
    
    if search_text:
        query = query.filter(
            or_(
                JournalEntry.content.ilike(f"%{search_text}%"),
                JournalEntry.title.ilike(f"%{search_text}%")
            )
        )
    
    if mood:
        query = query.filter(JournalEntry.mood == mood.value)
    
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    
    return query.scalar() or 0


def get_entries_with_pagination(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    page: int = 1,
    per_page: int = 20,
    include_archived: bool = False,
    search_text: Optional[str] = None,
    mood: Optional[JournalEntryMoodEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> tuple[List[JournalEntry], int]:
    """Get journal entries with pagination metadata."""
    # Build the base query
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id
    )
    
    if not include_archived:
        query = query.filter(JournalEntry.is_archived == False)
    
    if search_text:
        query = query.filter(
            or_(
                JournalEntry.content.ilike(f"%{search_text}%"),
                JournalEntry.title.ilike(f"%{search_text}%")
            )
        )
    
    if mood:
        query = query.filter(JournalEntry.mood == mood.value)
    
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    
    # Get total count before applying pagination
    total_count = query.count()
    
    # Apply ordering and pagination
    skip = (page - 1) * per_page
    entries = query.order_by(
        desc(JournalEntry.entry_date), 
        desc(JournalEntry.created_at)
    ).offset(skip).limit(per_page).all()
    
    return entries, total_count


def search_entries_optimized(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    search_text: str,
    page: int = 1,
    per_page: int = 20,
    include_archived: bool = False
) -> tuple[List[JournalEntry], int]:
    """Optimized search for journal entries with pagination."""
    # For PostgreSQL, we could use full-text search here
    # For now, using optimized ILIKE with proper indexing
    
    base_query = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        or_(
            JournalEntry.content.ilike(f"%{search_text}%"),
            JournalEntry.title.ilike(f"%{search_text}%")
        )
    )
    
    if not include_archived:
        base_query = base_query.filter(JournalEntry.is_archived == False)
    
    # Get total count
    total_count = base_query.count()
    
    # Apply pagination
    skip = (page - 1) * per_page
    entries = base_query.order_by(
        desc(JournalEntry.entry_date),
        desc(JournalEntry.created_at)
    ).offset(skip).limit(per_page).all()
    
    return entries, total_count


def bulk_update_entries(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    entry_ids: List[int],
    updates: Dict[str, Any]
) -> tuple[int, List[str]]:
    """Bulk update multiple journal entries."""
    errors = []
    success_count = 0
    
    try:
        # Verify all entries belong to the user
        entries = db.query(JournalEntry).filter(
            JournalEntry.id.in_(entry_ids),
            JournalEntry.user_id == user_id,
            JournalEntry.tenant_id == tenant_id
        ).all()
        
        if len(entries) != len(entry_ids):
            found_ids = {entry.id for entry in entries}
            missing_ids = set(entry_ids) - found_ids
            errors.append(f"Entries not found or not accessible: {missing_ids}")
        
        # Apply updates to found entries
        for entry in entries:
            for field, value in updates.items():
                if hasattr(entry, field):
                    setattr(entry, field, value)
                    success_count += 1
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        errors.append(f"Database error: {str(e)}")
    
    return success_count, errors


def bulk_add_tags(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    entry_ids: List[int],
    tags: List[JournalTagCreate]
) -> tuple[int, List[str]]:
    """Bulk add tags to multiple journal entries."""
    errors = []
    success_count = 0
    
    try:
        # Verify all entries belong to the user
        entries = db.query(JournalEntry).filter(
            JournalEntry.id.in_(entry_ids),
            JournalEntry.user_id == user_id,
            JournalEntry.tenant_id == tenant_id
        ).all()
        
        if len(entries) != len(entry_ids):
            found_ids = {entry.id for entry in entries}
            missing_ids = set(entry_ids) - found_ids
            errors.append(f"Entries not found or not accessible: {missing_ids}")
        
        # Add tags to each entry
        for entry in entries:
            for tag_data in tags:
                # Check if tag already exists
                existing = db.query(JournalTag).filter(
                    JournalTag.journal_entry_id == entry.id,
                    JournalTag.tag_name == tag_data.tag_name
                ).first()
                
                if not existing:
                    new_tag = JournalTag(
                        journal_entry_id=entry.id,
                        tag_name=tag_data.tag_name,
                        tag_color=tag_data.tag_color
                    )
                    db.add(new_tag)
                    success_count += 1
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        errors.append(f"Database error: {str(e)}")
    
    return success_count, errors


def get_popular_tags(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get most popular tags for a user."""
    tag_stats = db.query(
        JournalTag.tag_name,
        JournalTag.tag_color,
        func.count(JournalTag.id).label('usage_count')
    ).join(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.tenant_id == tenant_id,
        JournalEntry.is_archived == False
    ).group_by(
        JournalTag.tag_name,
        JournalTag.tag_color
    ).order_by(
        desc(func.count(JournalTag.id))
    ).limit(limit).all()
    
    return [
        {
            "tag_name": tag_name,
            "tag_color": tag_color,
            "usage_count": usage_count
        }
        for tag_name, tag_color, usage_count in tag_stats
    ]
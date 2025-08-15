from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import date

from app.api import deps
from app.crud import journal as journal_crud
from app.models.user import User
from app.schemas.journal import (
    JournalEntry, JournalEntryCreate, JournalEntryUpdate, JournalEntrySummary,
    JournalEntryMoodEnum, JournalTag, JournalTagCreate, JournalEntryListResponse,
    PaginationMeta, JournalEntryBulkUpdate, JournalEntryBulkTag, JournalEntryBulkResponse
)

router = APIRouter()


def build_pagination_meta(page: int, per_page: int, total: int) -> PaginationMeta:
    """Build pagination metadata."""
    total_pages = (total + per_page - 1) // per_page
    return PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )


@router.get("/", response_model=JournalEntryListResponse)
def list_journal_entries(
    request: Request,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Number of entries per page"),
    include_archived: bool = Query(False, description="Include archived entries"),
    mood: Optional[JournalEntryMoodEnum] = Query(None, description="Filter by mood"),
    start_date: Optional[date] = Query(None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(None, description="Filter entries until this date"),
    search: Optional[str] = Query(None, min_length=1, description="Search in title and content"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List user's journal entries with pagination and filtering.
    
    **Filtering Options:**
    - **include_archived**: Include archived entries (default: false)
    - **mood**: Filter by specific mood
    - **start_date**: Show entries from this date onwards
    - **end_date**: Show entries up to this date
    - **search**: Search in title and content
    
    **Pagination:**
    - Use `page` and `per_page` parameters for pagination
    - Returns pagination metadata including total count and page info
    - Maximum per_page is 100 entries per request
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own journal entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    if search:
        # Use optimized search with pagination
        entries, total_count = journal_crud.search_entries_optimized(
            db,
            user_id=current_user.id,
            tenant_id=tenant_id,
            search_text=search,
            page=page,
            per_page=per_page,
            include_archived=include_archived
        )
    else:
        # Use optimized general query with pagination
        entries, total_count = journal_crud.get_entries_with_pagination(
            db,
            user_id=current_user.id,
            tenant_id=tenant_id,
            page=page,
            per_page=per_page,
            include_archived=include_archived,
            mood=mood,
            start_date=start_date,
            end_date=end_date
        )
    
    # Convert to summary format (with tag and attachment counts)
    summaries = []
    for entry in entries:
        summary = JournalEntrySummary(
            id=entry.id,
            title=entry.title,
            entry_date=entry.entry_date,
            mood=JournalEntryMoodEnum(entry.mood) if entry.mood else None,
            is_private=entry.is_private,
            is_archived=entry.is_archived,
            created_at=entry.created_at,
            tag_count=len(entry.tags) if entry.tags else 0,
            attachment_count=len(entry.attachments) if entry.attachments else 0
        )
        summaries.append(summary)
    
    # Build pagination metadata
    pagination = build_pagination_meta(page, per_page, total_count)
    
    return JournalEntryListResponse(
        items=summaries,
        pagination=pagination
    )


@router.post("/", response_model=JournalEntry)
def create_journal_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    journal_entry_in: JournalEntryCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new journal entry.
    
    **Entry Data:**
    - **content**: Required - main journal content
    - **title**: Optional - entry title
    - **entry_date**: Required - date this entry represents
    - **mood**: Optional - mood/sentiment for the entry
    - **location**: Optional - location context
    - **weather**: Optional - weather context
    - **is_private**: Optional - privacy setting (default: true)
    - **tags**: Optional - list of tags to add to the entry
    
    **Authentication:**
    - Requires valid authentication token
    - Entry is associated with the authenticated user and their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    journal_entry = journal_crud.create_journal_entry(
        db=db,
        journal_entry=journal_entry_in,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return journal_entry


@router.get("/{entry_id}", response_model=JournalEntry)
def get_journal_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific journal entry by ID.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    journal_entry = journal_crud.get_journal_entry_with_relations(
        db, entry_id=entry_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal_entry


@router.put("/{entry_id}", response_model=JournalEntry)
def update_journal_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    journal_entry_in: JournalEntryUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a journal entry.
    
    **Updatable Fields:**
    - **title**: Entry title
    - **content**: Main journal content
    - **entry_date**: Date this entry represents
    - **mood**: Mood/sentiment for the entry
    - **location**: Location context
    - **weather**: Weather context
    - **is_private**: Privacy setting
    - **is_archived**: Archive status
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only update their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    journal_entry = journal_crud.update_journal_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        journal_entry=journal_entry_in
    )
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal_entry


@router.delete("/{entry_id}")
def delete_journal_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a journal entry (hard delete).
    
    **Warning:**
    - This permanently deletes the entry and cannot be undone
    - Consider using the archive endpoint for soft deletion
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only delete their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    success = journal_crud.delete_journal_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"detail": "Journal entry deleted successfully"}


@router.post("/{entry_id}/archive", response_model=JournalEntry)
def archive_journal_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    archive: bool = Query(True, description="Archive (true) or unarchive (false) the entry"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Archive or unarchive a journal entry (soft delete/restore).
    
    **Parameters:**
    - **archive**: true to archive, false to unarchive (default: true)
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only archive their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    journal_entry = journal_crud.archive_journal_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        archive=archive
    )
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal_entry


@router.post("/{entry_id}/tags", response_model=JournalTag)
def add_tag_to_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    tag_in: JournalTagCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a tag to a journal entry.
    
    **Tag Data:**
    - **tag_name**: Required - name of the tag (1-50 characters)
    - **tag_color**: Optional - hex color code (e.g., #FF5733)
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only add tags to their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    tag = journal_crud.add_tag_to_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        tag=tag_in
    )
    if not tag:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return tag


@router.delete("/{entry_id}/tags/{tag_name}")
def remove_tag_from_entry(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    entry_id: int,
    tag_name: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove a tag from a journal entry.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only remove tags from their own entries within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    success = journal_crud.remove_tag_from_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        tag_name=tag_name
    )
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry or tag not found")
    return {"detail": "Tag removed successfully"}


@router.get("/stats/", response_model=dict)
def get_journal_stats(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get journal statistics for the current user.
    
    **Returns:**
    - **total_entries**: Total number of non-archived entries
    - **mood_distribution**: Count of entries by mood
    - **most_used_tags**: Top 10 most used tags with counts
    
    **Authentication:**
    - Requires valid authentication token
    - Returns statistics only for the authenticated user's entries
    """
    tenant_id = deps.get_tenant_context(request)
    
    stats = journal_crud.get_user_stats(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return stats


@router.post("/bulk-update", response_model=JournalEntryBulkResponse)
def bulk_update_journal_entries(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    bulk_update: JournalEntryBulkUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Bulk update multiple journal entries.
    
    **Supported Updates:**
    - **is_archived**: Archive or unarchive entries
    - **is_private**: Change privacy setting
    
    **Authentication:**
    - Requires valid authentication token
    - Can only update entries belonging to the authenticated user
    """
    tenant_id = deps.get_tenant_context(request)
    
    # Prepare updates dictionary
    updates = {}
    if bulk_update.is_archived is not None:
        updates['is_archived'] = bulk_update.is_archived
    if bulk_update.is_private is not None:
        updates['is_private'] = bulk_update.is_private
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid updates provided")
    
    success_count, errors = journal_crud.bulk_update_entries(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        entry_ids=bulk_update.entry_ids,
        updates=updates
    )
    
    return JournalEntryBulkResponse(
        success_count=success_count,
        failed_count=len(bulk_update.entry_ids) - success_count,
        errors=errors
    )


@router.post("/bulk-tag", response_model=JournalEntryBulkResponse)
def bulk_tag_journal_entries(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    bulk_tag: JournalEntryBulkTag,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Bulk add or remove tags from multiple journal entries.
    
    **Operations:**
    - **tags_to_add**: List of tags to add to all specified entries
    - **tags_to_remove**: List of tag names to remove from all specified entries
    
    **Authentication:**
    - Requires valid authentication token
    - Can only modify entries belonging to the authenticated user
    """
    tenant_id = deps.get_tenant_context(request)
    
    success_count = 0
    errors = []
    
    # Add tags if specified
    if bulk_tag.tags_to_add:
        add_count, add_errors = journal_crud.bulk_add_tags(
            db=db,
            user_id=current_user.id,
            tenant_id=tenant_id,
            entry_ids=bulk_tag.entry_ids,
            tags=bulk_tag.tags_to_add
        )
        success_count += add_count
        errors.extend(add_errors)
    
    # Remove tags if specified
    if bulk_tag.tags_to_remove:
        for entry_id in bulk_tag.entry_ids:
            for tag_name in bulk_tag.tags_to_remove:
                removed = journal_crud.remove_tag_from_entry(
                    db=db,
                    entry_id=entry_id,
                    user_id=current_user.id,
                    tenant_id=tenant_id,
                    tag_name=tag_name
                )
                if removed:
                    success_count += 1
    
    return JournalEntryBulkResponse(
        success_count=success_count,
        failed_count=0,  # Error handling could be improved here
        errors=errors
    )


@router.get("/tags/popular", response_model=List[dict])
def get_popular_tags(
    request: Request,
    db: Session = Depends(deps.get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of tags to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the most popular tags for the current user.
    
    **Returns:**
    - List of tags with usage counts, sorted by popularity
    - Each tag includes: name, color, and usage count
    
    **Authentication:**
    - Requires valid authentication token
    - Returns only tags from the authenticated user's entries
    """
    tenant_id = deps.get_tenant_context(request)
    
    popular_tags = journal_crud.get_popular_tags(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        limit=limit
    )
    
    return popular_tags
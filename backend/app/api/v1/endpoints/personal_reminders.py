from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import personal_reminder
from app.models.user import User
from app.schemas.personal_reminder import (
    PersonalReminder,
    PersonalReminderCreate,
    PersonalReminderUpdate,
    PersonalReminderWithContact,
    UpcomingReminder,
    PersonalReminderFilter,
    PersonalReminderSearchQuery,
    ReminderTypeEnum,
    ImportanceLevelEnum
)

router = APIRouter()


@router.post("/", response_model=PersonalReminder)
def create_personal_reminder(
    request: Request,
    reminder_in: PersonalReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new personal reminder.
    """
    tenant_id = request.state.tenant.id
    
    # Validate contact_id exists if provided
    if reminder_in.contact_id:
        from app.crud import contact
        contact_obj = contact.get_contact(
            db=db, 
            contact_id=reminder_in.contact_id, 
            tenant_id=tenant_id
        )
        if not contact_obj or contact_obj.created_by_user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Contact not found or not accessible"
            )
    
    return personal_reminder.create_reminder(
        db=db,
        obj_in=reminder_in,
        user_id=current_user.id,
        tenant_id=tenant_id
    )


@router.get("/", response_model=List[PersonalReminderWithContact])
def get_personal_reminders(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of reminders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of reminders to retrieve"),
    reminder_type: Optional[ReminderTypeEnum] = Query(None, description="Filter by reminder type"),
    importance_level: Optional[ImportanceLevelEnum] = Query(None, description="Filter by importance level"),
    contact_id: Optional[int] = Query(None, description="Filter by contact ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_recurring: Optional[bool] = Query(None, description="Filter by recurring status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personal reminders for the current user with optional filtering.
    """
    tenant_id = request.state.tenant.id
    
    filter_params = PersonalReminderFilter(
        reminder_type=reminder_type,
        importance_level=importance_level,
        contact_id=contact_id,
        is_active=is_active,
        is_recurring=is_recurring
    )
    
    return personal_reminder.get_reminders_by_user(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        filter_params=filter_params,
        skip=skip,
        limit=limit
    )


@router.get("/upcoming", response_model=List[UpcomingReminder])
def get_upcoming_reminders(
    request: Request,
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days ahead to look for reminders"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming reminders within the specified number of days.
    """
    tenant_id = request.state.tenant.id
    
    return personal_reminder.get_upcoming_reminders(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=days_ahead
    )


@router.get("/today", response_model=List[UpcomingReminder])
def get_todays_reminders(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get reminders happening today.
    """
    tenant_id = request.state.tenant.id
    
    return personal_reminder.get_upcoming_reminders(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=0
    )


@router.get("/this-week", response_model=List[UpcomingReminder])
def get_this_weeks_reminders(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get reminders happening this week (next 7 days).
    """
    tenant_id = request.state.tenant.id
    
    return personal_reminder.get_upcoming_reminders(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=7
    )


@router.get("/search", response_model=List[PersonalReminderWithContact])
def search_personal_reminders(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    reminder_type: Optional[ReminderTypeEnum] = Query(None, description="Filter by reminder type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search personal reminders by title and description.
    """
    tenant_id = request.state.tenant.id
    
    return personal_reminder.search_reminders(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        query=q,
        reminder_type=reminder_type.value if reminder_type else None,
        is_active=is_active
    )


@router.get("/{reminder_id}", response_model=PersonalReminderWithContact)
def get_personal_reminder(
    request: Request,
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific personal reminder by ID.
    """
    tenant_id = request.state.tenant.id
    
    reminder = personal_reminder.get_reminder_with_contact(
        db=db,
        reminder_id=reminder_id,
        tenant_id=tenant_id
    )
    
    if not reminder or reminder.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Personal reminder not found"
        )
    
    return reminder


@router.put("/{reminder_id}", response_model=PersonalReminder)
def update_personal_reminder(
    request: Request,
    reminder_id: int,
    reminder_in: PersonalReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a personal reminder.
    """
    tenant_id = request.state.tenant.id
    
    # Get the existing reminder
    db_reminder = personal_reminder.get_reminder(
        db=db,
        reminder_id=reminder_id,
        tenant_id=tenant_id
    )
    
    if not db_reminder or db_reminder.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Personal reminder not found"
        )
    
    # Validate contact_id if being updated
    if reminder_in.contact_id:
        from app.crud import contact
        contact_obj = contact.get_contact(
            db=db,
            contact_id=reminder_in.contact_id,
            tenant_id=tenant_id
        )
        if not contact_obj or contact_obj.created_by_user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Contact not found or not accessible"
            )
    
    return personal_reminder.update_reminder(
        db=db,
        db_obj=db_reminder,
        obj_in=reminder_in
    )


@router.delete("/{reminder_id}")
def delete_personal_reminder(
    request: Request,
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a personal reminder.
    """
    tenant_id = request.state.tenant.id
    
    # Verify the reminder exists and belongs to the user
    db_reminder = personal_reminder.get_reminder(
        db=db,
        reminder_id=reminder_id,
        tenant_id=tenant_id
    )
    
    if not db_reminder or db_reminder.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Personal reminder not found"
        )
    
    success = personal_reminder.delete_reminder(
        db=db,
        reminder_id=reminder_id,
        tenant_id=tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete personal reminder"
        )
    
    return {"message": "Personal reminder deleted successfully"}


@router.post("/{reminder_id}/celebrate")
def mark_reminder_celebrated(
    request: Request,
    reminder_id: int,
    year: Optional[int] = Query(None, description="Year to mark as celebrated (defaults to current year)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a reminder as celebrated for a specific year.
    """
    tenant_id = request.state.tenant.id
    
    # Verify the reminder exists and belongs to the user
    db_reminder = personal_reminder.get_reminder(
        db=db,
        reminder_id=reminder_id,
        tenant_id=tenant_id
    )
    
    if not db_reminder or db_reminder.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Personal reminder not found"
        )
    
    # Use current year if not specified
    from datetime import date
    if year is None:
        year = date.today().year
    
    updated_reminder = personal_reminder.update_last_celebrated_year(
        db=db,
        reminder_id=reminder_id,
        year=year
    )
    
    return {
        "message": f"Reminder marked as celebrated for {year}",
        "last_celebrated_year": updated_reminder.last_celebrated_year
    }
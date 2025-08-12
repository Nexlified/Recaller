from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.api import deps
from app.crud import event as event_crud, contact as contact_crud
from app.models.user import User
from app.schemas.event import (
    Event, EventCreate, EventUpdate, EventWithAttendees,
    ContactEventAttendance, ContactEventAttendanceCreate, ContactEventAttendanceUpdate,
    EventTag, EventTagCreate, EventFollowUp, EventFollowUpCreate, EventFollowUpUpdate,
    EventAnalytics
)

router = APIRouter()


# Core Event Operations
@router.get("/", response_model=List[Event])
def list_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve events with optional filtering.
    """
    events = event_crud.get_events(
        db, 
        skip=skip, 
        limit=limit, 
        tenant_id=current_user.tenant_id,
        event_type=event_type,
        status=status,
        start_date_from=start_date_from,
        start_date_to=start_date_to
    )
    return events


@router.get("/{event_id}", response_model=EventWithAttendees)
def get_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    include: Optional[str] = Query(None, description="Comma-separated list: attendees,tags,follow_ups"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event details with optional related data.
    """
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Build response with optional includes
    result = EventWithAttendees.model_validate(event)
    
    if include:
        includes = [inc.strip() for inc in include.split(",")]
        
        if "attendees" in includes:
            result.attendees = event_crud.get_event_attendees(db, event_id)
        
        if "tags" in includes:
            result.tags = event_crud.get_event_tags(db, event_id)
        
        if "follow_ups" in includes:
            result.follow_ups = event_crud.get_event_follow_ups(db, event_id)
    
    return result


@router.post("/", response_model=Event)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: EventCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new event.
    """
    event = event_crud.create_event(
        db, 
        obj_in=event_in, 
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id
    )
    return event


@router.put("/{event_id}", response_model=Event)
def update_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update event.
    """
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = event_crud.update_event(db, db_obj=event, obj_in=event_in)
    return event


@router.delete("/{event_id}")
def delete_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete event.
    """
    event = event_crud.delete_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}


# Event Discovery
@router.get("/search/", response_model=List[Event])
def search_events(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search events by name, location, type, description.
    """
    events = event_crud.search_events(
        db, 
        query=q, 
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return events


@router.get("/types/{event_type}", response_model=List[Event])
def get_events_by_type(
    *,
    db: Session = Depends(deps.get_db),
    event_type: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get events by specific type.
    """
    events = event_crud.get_events(
        db, 
        skip=skip, 
        limit=limit, 
        tenant_id=current_user.tenant_id,
        event_type=event_type
    )
    return events


@router.get("/upcoming/", response_model=List[Event])
def get_upcoming_events(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get upcoming events.
    """
    events = event_crud.get_upcoming_events(
        db, 
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return events


@router.get("/past/", response_model=List[Event])
def get_past_events(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get past events.
    """
    events = event_crud.get_past_events(
        db, 
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return events


@router.get("/by-date/{event_date}", response_model=List[Event])
def get_events_by_date(
    *,
    db: Session = Depends(deps.get_db),
    event_date: date,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get events by specific date.
    """
    events = event_crud.get_events_by_date(
        db, 
        event_date=event_date, 
        tenant_id=current_user.tenant_id
    )
    return events


@router.get("/calendar/{year}/{month}", response_model=List[Event])
def get_events_for_calendar(
    *,
    db: Session = Depends(deps.get_db),
    year: int,
    month: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get events for calendar view.
    """
    events = event_crud.get_events_for_calendar(
        db, 
        year=year, 
        month=month, 
        tenant_id=current_user.tenant_id
    )
    return events


# Attendance Management
@router.get("/{event_id}/attendees", response_model=List[ContactEventAttendance])
def get_event_attendees(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event attendees.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendees = event_crud.get_event_attendees(db, event_id)
    return attendees


@router.post("/{event_id}/attendees", response_model=ContactEventAttendance)
def add_event_attendee(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    attendance_in: ContactEventAttendanceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add attendee to event.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Verify contact belongs to user's tenant
    contact = contact_crud.get_contact(db, contact_id=attendance_in.contact_id, tenant_id=current_user.tenant_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Check if attendance already exists
    existing = event_crud.get_attendance(db, contact_id=attendance_in.contact_id, event_id=event_id)
    if existing:
        raise HTTPException(status_code=400, detail="Contact already added to event")
    
    # Ensure event_id matches URL parameter
    attendance_in.event_id = event_id
    
    attendance = event_crud.create_attendance(db, obj_in=attendance_in)
    return attendance


@router.put("/{event_id}/attendees/{contact_id}", response_model=ContactEventAttendance)
def update_event_attendee(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    contact_id: int,
    attendance_in: ContactEventAttendanceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update attendee details.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendance = event_crud.get_attendance(db, contact_id=contact_id, event_id=event_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    attendance = event_crud.update_attendance(db, db_obj=attendance, obj_in=attendance_in)
    return attendance


@router.delete("/{event_id}/attendees/{contact_id}")
def remove_event_attendee(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove attendee from event.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attendance = event_crud.delete_attendance(db, contact_id=contact_id, event_id=event_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    return {"message": "Attendee removed successfully"}


# Event Context and Relationships
@router.get("/{event_id}/new-connections", response_model=List[ContactEventAttendance])
def get_new_connections_at_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get new relationships formed at event.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    connections = event_crud.get_new_connections_at_event(db, event_id)
    return connections


@router.get("/{event_id}/relationship-changes", response_model=List[ContactEventAttendance])
def get_relationship_changes_at_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get relationship strength changes at event.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    changes = event_crud.get_relationship_changes_at_event(db, event_id)
    return changes


@router.post("/{event_id}/follow-ups", response_model=EventFollowUp)
def create_event_follow_up(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    follow_up_in: EventFollowUpCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create follow-up action for event.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Ensure event_id matches URL parameter
    follow_up_in.event_id = event_id
    
    follow_up = event_crud.create_event_follow_up(
        db, 
        obj_in=follow_up_in, 
        created_by_user_id=current_user.id
    )
    return follow_up


@router.get("/{event_id}/follow-ups", response_model=List[EventFollowUp])
def get_event_follow_ups(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event follow-ups.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    follow_ups = event_crud.get_event_follow_ups(db, event_id)
    return follow_ups


# Event Analytics
@router.get("/{event_id}/analytics", response_model=EventAnalytics)
def get_event_analytics(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event networking analytics.
    """
    # Verify event belongs to user's tenant
    event = event_crud.get_event(db, event_id=event_id, tenant_id=current_user.tenant_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    analytics = event_crud.get_event_analytics(db, event_id)
    return analytics
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import date, datetime

from app.models.event import Event, ContactEventAttendance, EventTag, EventFollowUp
from app.schemas.event import (
    EventCreate, EventUpdate, 
    ContactEventAttendanceCreate, ContactEventAttendanceUpdate,
    EventTagCreate, EventFollowUpCreate, EventFollowUpUpdate,
    EventAnalytics
)


# Event CRUD Operations
def get_event(db: Session, event_id: int, tenant_id: int) -> Optional[Event]:
    return db.query(Event).filter(
        Event.id == event_id,
        Event.tenant_id == tenant_id
    ).first()


def get_events(
    db: Session, 
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100, 
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None
) -> List[Event]:
    query = db.query(Event).filter(Event.tenant_id == tenant_id)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if status:
        query = query.filter(Event.status == status)
    
    if start_date_from:
        query = query.filter(Event.start_date >= start_date_from)
    
    if start_date_to:
        query = query.filter(Event.start_date <= start_date_to)
    
    return query.offset(skip).limit(limit).all()


def get_upcoming_events(
    db: Session, 
    tenant_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Event]:
    today = date.today()
    return db.query(Event).filter(
        Event.tenant_id == tenant_id,
        Event.start_date >= today,
        Event.status.in_(['planned', 'confirmed'])
    ).order_by(Event.start_date).offset(skip).limit(limit).all()


def get_past_events(
    db: Session, 
    tenant_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Event]:
    today = date.today()
    return db.query(Event).filter(
        Event.tenant_id == tenant_id,
        Event.start_date < today
    ).order_by(Event.start_date.desc()).offset(skip).limit(limit).all()


def get_events_by_date(
    db: Session, 
    event_date: date, 
    tenant_id: int
) -> List[Event]:
    return db.query(Event).filter(
        Event.tenant_id == tenant_id,
        Event.start_date == event_date
    ).all()


def get_events_for_calendar(
    db: Session, 
    year: int, 
    month: int, 
    tenant_id: int
) -> List[Event]:
    from datetime import date
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    return db.query(Event).filter(
        Event.tenant_id == tenant_id,
        Event.start_date >= start_date,
        Event.start_date < end_date
    ).order_by(Event.start_date).all()


def create_event(
    db: Session, 
    obj_in: EventCreate, 
    tenant_id: int, 
    created_by_user_id: int
) -> Event:
    db_obj = Event(
        **obj_in.model_dump(),
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_event(
    db: Session, 
    db_obj: Event, 
    obj_in: Union[EventUpdate, Dict[str, Any]]
) -> Event:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_event(db: Session, event_id: int, tenant_id: int) -> Optional[Event]:
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.tenant_id == tenant_id
    ).first()
    if event:
        db.delete(event)
        db.commit()
    return event


def search_events(
    db: Session,
    query: str,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Event]:
    return db.query(Event).filter(
        Event.tenant_id == tenant_id,
        or_(
            Event.name.ilike(f"%{query}%"),
            Event.description.ilike(f"%{query}%"),
            Event.location.ilike(f"%{query}%"),
            Event.venue.ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit).all()


# Contact Event Attendance CRUD Operations
def get_event_attendees(db: Session, event_id: int) -> List[ContactEventAttendance]:
    return db.query(ContactEventAttendance).filter(
        ContactEventAttendance.event_id == event_id
    ).all()


def get_contact_events(db: Session, contact_id: int) -> List[ContactEventAttendance]:
    return db.query(ContactEventAttendance).filter(
        ContactEventAttendance.contact_id == contact_id
    ).all()


def get_attendance(
    db: Session, 
    contact_id: int, 
    event_id: int
) -> Optional[ContactEventAttendance]:
    return db.query(ContactEventAttendance).filter(
        ContactEventAttendance.contact_id == contact_id,
        ContactEventAttendance.event_id == event_id
    ).first()


def create_attendance(
    db: Session, 
    obj_in: ContactEventAttendanceCreate
) -> ContactEventAttendance:
    db_obj = ContactEventAttendance(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_attendance(
    db: Session,
    db_obj: ContactEventAttendance,
    obj_in: Union[ContactEventAttendanceUpdate, Dict[str, Any]]
) -> ContactEventAttendance:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_attendance(
    db: Session, 
    contact_id: int, 
    event_id: int
) -> Optional[ContactEventAttendance]:
    attendance = db.query(ContactEventAttendance).filter(
        ContactEventAttendance.contact_id == contact_id,
        ContactEventAttendance.event_id == event_id
    ).first()
    if attendance:
        db.delete(attendance)
        db.commit()
    return attendance


# Event Tags CRUD Operations
def get_event_tags(db: Session, event_id: int) -> List[EventTag]:
    return db.query(EventTag).filter(EventTag.event_id == event_id).all()


def create_event_tag(db: Session, obj_in: EventTagCreate) -> EventTag:
    db_obj = EventTag(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_event_tag(db: Session, tag_id: int) -> Optional[EventTag]:
    tag = db.query(EventTag).filter(EventTag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


# Event Follow-ups CRUD Operations
def get_event_follow_ups(db: Session, event_id: int) -> List[EventFollowUp]:
    return db.query(EventFollowUp).filter(EventFollowUp.event_id == event_id).all()


def create_event_follow_up(
    db: Session, 
    obj_in: EventFollowUpCreate, 
    created_by_user_id: int
) -> EventFollowUp:
    db_obj = EventFollowUp(
        **obj_in.model_dump(),
        created_by_user_id=created_by_user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_event_follow_up(
    db: Session,
    db_obj: EventFollowUp,
    obj_in: Union[EventFollowUpUpdate, Dict[str, Any]]
) -> EventFollowUp:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_event_follow_up(db: Session, follow_up_id: int) -> Optional[EventFollowUp]:
    follow_up = db.query(EventFollowUp).filter(EventFollowUp.id == follow_up_id).first()
    if follow_up:
        db.delete(follow_up)
        db.commit()
    return follow_up


# Analytics Functions
def get_event_analytics(db: Session, event_id: int) -> EventAnalytics:
    attendances = db.query(ContactEventAttendance).filter(
        ContactEventAttendance.event_id == event_id
    ).all()
    
    new_connections = len([a for a in attendances if a.connection_quality == "first_meeting"])
    strengthened_relationships = len([a for a in attendances if a.connection_quality == "strengthened"])
    follow_ups_created = len([a for a in attendances if a.follow_up_needed])
    total_attendees = len([a for a in attendances if a.attendance_status == "attended"])
    
    # Get expected attendees from event
    event = db.query(Event).filter(Event.id == event_id).first()
    attendance_rate = None
    if event and event.expected_attendees:
        attendance_rate = total_attendees / event.expected_attendees
    
    return EventAnalytics(
        new_connections=new_connections,
        strengthened_relationships=strengthened_relationships,
        follow_ups_created=follow_ups_created,
        total_attendees=total_attendees,
        attendance_rate=attendance_rate
    )


def get_shared_events(db: Session, contact1_id: int, contact2_id: int) -> List[Event]:
    """Get events where both contacts attended"""
    return db.query(Event).join(ContactEventAttendance).filter(
        ContactEventAttendance.contact_id == contact1_id
    ).intersect(
        db.query(Event).join(ContactEventAttendance).filter(
            ContactEventAttendance.contact_id == contact2_id
        )
    ).all()


def get_new_connections_at_event(db: Session, event_id: int) -> List[ContactEventAttendance]:
    """Get attendances where new connections were made"""
    return db.query(ContactEventAttendance).filter(
        ContactEventAttendance.event_id == event_id,
        ContactEventAttendance.connection_quality == "first_meeting"
    ).all()


def get_relationship_changes_at_event(db: Session, event_id: int) -> List[ContactEventAttendance]:
    """Get attendances where relationship strength changed"""
    return db.query(ContactEventAttendance).filter(
        ContactEventAttendance.event_id == event_id,
        ContactEventAttendance.relationship_strength_before.is_not(None),
        ContactEventAttendance.relationship_strength_after.is_not(None),
        ContactEventAttendance.relationship_strength_before != ContactEventAttendance.relationship_strength_after
    ).all()
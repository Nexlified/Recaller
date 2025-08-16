from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, extract, func
from datetime import date, datetime, timedelta

from app.models.personal_reminder import PersonalReminder
from app.models.contact import Contact
from app.schemas.personal_reminder import (
    PersonalReminderCreate, PersonalReminderUpdate, PersonalReminderFilter,
    UpcomingReminder, ReminderContact
)


def create_reminder(
    db: Session, 
    *, 
    obj_in: PersonalReminderCreate, 
    user_id: int, 
    tenant_id: int
) -> PersonalReminder:
    """Create a new personal reminder."""
    db_obj = PersonalReminder(
        tenant_id=tenant_id,
        user_id=user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_reminder(db: Session, reminder_id: int, tenant_id: int) -> Optional[PersonalReminder]:
    """Get a single reminder by ID with tenant filtering."""
    return db.query(PersonalReminder).filter(
        PersonalReminder.id == reminder_id,
        PersonalReminder.tenant_id == tenant_id
    ).first()


def get_reminder_with_contact(db: Session, reminder_id: int, tenant_id: int) -> Optional[PersonalReminder]:
    """Get a reminder with contact information loaded."""
    return db.query(PersonalReminder).options(
        joinedload(PersonalReminder.contact)
    ).filter(
        PersonalReminder.id == reminder_id,
        PersonalReminder.tenant_id == tenant_id
    ).first()


def get_reminders_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    filter_params: Optional[PersonalReminderFilter] = None,
    skip: int = 0,
    limit: int = 100
) -> List[PersonalReminder]:
    """Get reminders for a specific user with optional filtering."""
    query = db.query(PersonalReminder).options(
        joinedload(PersonalReminder.contact)
    ).filter(
        PersonalReminder.user_id == user_id,
        PersonalReminder.tenant_id == tenant_id
    )

    if filter_params:
        query = _apply_filters(query, filter_params)

    return query.offset(skip).limit(limit).all()


def get_upcoming_reminders(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    days_ahead: int = 30
) -> List[UpcomingReminder]:
    """Get upcoming reminders within the specified number of days."""
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    
    # For recurring reminders, we need to calculate the next occurrence
    reminders = db.query(PersonalReminder).options(
        joinedload(PersonalReminder.contact)
    ).filter(
        PersonalReminder.user_id == user_id,
        PersonalReminder.tenant_id == tenant_id,
        PersonalReminder.is_active == True
    ).all()

    upcoming = []
    for reminder in reminders:
        next_occurrence = _calculate_next_occurrence(reminder, today)
        if next_occurrence and next_occurrence <= end_date:
            days_until = (next_occurrence - today).days
            
            # Calculate years since for anniversaries/birthdays
            years_since = None
            if reminder.reminder_type in ['birthday', 'anniversary', 'death_anniversary']:
                years_since = next_occurrence.year - reminder.event_date.year

            contact_info = None
            if reminder.contact:
                contact_info = ReminderContact(
                    id=reminder.contact.id,
                    first_name=reminder.contact.first_name,
                    last_name=reminder.contact.last_name,
                    family_nickname=reminder.contact.family_nickname
                )

            upcoming_reminder = UpcomingReminder(
                reminder_id=reminder.id,
                title=reminder.title,
                description=reminder.description,
                reminder_type=reminder.reminder_type,
                event_date=next_occurrence,
                days_until=days_until,
                importance_level=reminder.importance_level,
                contact=contact_info,
                years_since=years_since
            )
            upcoming.append(upcoming_reminder)

    # Sort by days until
    upcoming.sort(key=lambda x: x.days_until)
    return upcoming


def get_reminders_for_date(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    target_date: date
) -> List[PersonalReminder]:
    """Get reminders that should trigger on a specific date."""
    reminders = db.query(PersonalReminder).filter(
        PersonalReminder.user_id == user_id,
        PersonalReminder.tenant_id == tenant_id,
        PersonalReminder.is_active == True
    ).all()

    triggered_reminders = []
    for reminder in reminders:
        if _should_trigger_reminder(reminder, target_date):
            triggered_reminders.append(reminder)

    return triggered_reminders


def search_reminders(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    query: str,
    reminder_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[PersonalReminder]:
    """Search reminders by title and description."""
    search_query = db.query(PersonalReminder).options(
        joinedload(PersonalReminder.contact)
    ).filter(
        PersonalReminder.user_id == user_id,
        PersonalReminder.tenant_id == tenant_id
    )

    # Text search
    search_query = search_query.filter(
        or_(
            PersonalReminder.title.ilike(f"%{query}%"),
            PersonalReminder.description.ilike(f"%{query}%")
        )
    )

    # Additional filters
    if reminder_type:
        search_query = search_query.filter(PersonalReminder.reminder_type == reminder_type)
    if is_active is not None:
        search_query = search_query.filter(PersonalReminder.is_active == is_active)

    return search_query.all()


def update_reminder(
    db: Session,
    *,
    db_obj: PersonalReminder,
    obj_in: PersonalReminderUpdate
) -> PersonalReminder:
    """Update a personal reminder."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_reminder(db: Session, *, reminder_id: int, tenant_id: int) -> bool:
    """Delete a personal reminder."""
    reminder = db.query(PersonalReminder).filter(
        PersonalReminder.id == reminder_id,
        PersonalReminder.tenant_id == tenant_id
    ).first()
    
    if reminder:
        db.delete(reminder)
        db.commit()
        return True
    return False


def update_last_celebrated_year(
    db: Session,
    *,
    reminder_id: int,
    year: int
) -> Optional[PersonalReminder]:
    """Update the last celebrated year for a reminder."""
    reminder = db.query(PersonalReminder).filter(PersonalReminder.id == reminder_id).first()
    if reminder:
        reminder.last_celebrated_year = year
        db.commit()
        db.refresh(reminder)
    return reminder


def _calculate_next_occurrence(reminder: PersonalReminder, from_date: date) -> Optional[date]:
    """Calculate the next occurrence of a reminder."""
    if not reminder.is_recurring:
        # For non-recurring reminders, return the event date if it's in the future
        return reminder.event_date if reminder.event_date >= from_date else None

    # For recurring reminders, calculate next occurrence
    event_date = reminder.event_date
    current_year = from_date.year

    # Try to create the date in the current year
    try:
        next_occurrence = event_date.replace(year=current_year)
    except ValueError:
        # Handle leap year edge case (Feb 29)
        next_occurrence = date(current_year, event_date.month, 28)

    # If the date has already passed this year, move to next year
    if next_occurrence < from_date:
        try:
            next_occurrence = event_date.replace(year=current_year + 1)
        except ValueError:
            # Handle leap year edge case
            next_occurrence = date(current_year + 1, event_date.month, 28)

    return next_occurrence


def _should_trigger_reminder(reminder: PersonalReminder, target_date: date) -> bool:
    """Check if a reminder should trigger on a specific date."""
    next_occurrence = _calculate_next_occurrence(reminder, target_date)
    if not next_occurrence:
        return False

    days_until = (next_occurrence - target_date).days
    preferences = reminder.reminder_preferences or {}

    # Check if any of the preference conditions are met
    if preferences.get('same_day') and days_until == 0:
        return True
    if preferences.get('day_before') and days_until == 1:
        return True
    if preferences.get('week_before') and days_until == 7:
        return True
    if preferences.get('custom_days') and days_until in preferences['custom_days']:
        return True

    return False


def _apply_filters(query, filter_params: PersonalReminderFilter):
    """Apply filters to the query."""
    if filter_params.reminder_type:
        query = query.filter(PersonalReminder.reminder_type == filter_params.reminder_type)
    if filter_params.importance_level is not None:
        query = query.filter(PersonalReminder.importance_level == filter_params.importance_level)
    if filter_params.contact_id:
        query = query.filter(PersonalReminder.contact_id == filter_params.contact_id)
    if filter_params.is_active is not None:
        query = query.filter(PersonalReminder.is_active == filter_params.is_active)
    if filter_params.is_recurring is not None:
        query = query.filter(PersonalReminder.is_recurring == filter_params.is_recurring)
    if filter_params.event_date_start:
        query = query.filter(PersonalReminder.event_date >= filter_params.event_date_start)
    if filter_params.event_date_end:
        query = query.filter(PersonalReminder.event_date <= filter_params.event_date_end)

    return query
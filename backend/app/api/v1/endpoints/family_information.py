"""
API endpoints for family information tracking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.family_information import (
    FamilyMemberInfo,
    BirthdayReminder,
    EmergencyContact,
    FamilySummary,
    FamilyInformationFilter
)
from app.crud.family_information import FamilyInformationService

router = APIRouter()


@router.get("/members", response_model=List[FamilyMemberInfo])
def get_family_members(
    request: Request,
    include_extended: bool = Query(True, description="Include extended family members"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all family members with relationship information.
    
    Args:
        include_extended: Whether to include extended family (cousins, aunts, etc.)
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    return family_service.get_family_members(
        user_id=current_user.id,
        tenant_id=tenant_id,
        include_extended=include_extended
    )


@router.get("/birthdays", response_model=List[BirthdayReminder])
def get_upcoming_birthdays(
    request: Request,
    days_ahead: int = Query(30, description="Number of days ahead to look for birthdays"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming birthdays within the specified number of days.
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    return family_service.get_upcoming_birthdays(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=days_ahead
    )


@router.get("/anniversaries", response_model=List[BirthdayReminder])
def get_upcoming_anniversaries(
    request: Request,
    days_ahead: int = Query(30, description="Number of days ahead to look for anniversaries"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming anniversaries within the specified number of days.
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    return family_service.get_upcoming_anniversaries(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=days_ahead
    )


@router.get("/emergency-contacts", response_model=List[EmergencyContact])
def get_emergency_contacts(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all contacts marked as emergency contacts.
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    return family_service.get_emergency_contacts(
        user_id=current_user.id,
        tenant_id=tenant_id
    )


@router.get("/summary", response_model=FamilySummary)
def get_family_summary(
    request: Request,
    include_extended_family: bool = Query(True, description="Include extended family in summary"),
    include_in_laws: bool = Query(True, description="Include in-laws in summary"),
    days_ahead_for_reminders: int = Query(30, description="Days ahead for birthday/anniversary reminders"),
    generation_depth: int = Query(3, description="How many generations to include in family tree"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive family information summary including:
    - Total family members count
    - Family tree structure
    - Upcoming birthdays and anniversaries  
    - Emergency contacts list
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    filter_params = FamilyInformationFilter(
        include_extended_family=include_extended_family,
        include_in_laws=include_in_laws,
        days_ahead_for_reminders=days_ahead_for_reminders,
        generation_depth=generation_depth
    )
    
    return family_service.get_family_summary(
        user_id=current_user.id,
        tenant_id=tenant_id,
        filter_params=filter_params
    )


@router.get("/reminders/today", response_model=List[BirthdayReminder])
def get_todays_reminders(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get birthdays and anniversaries happening today.
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    # Get events happening today (0 days ahead)
    birthdays_today = family_service.get_upcoming_birthdays(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=0
    )
    
    anniversaries_today = family_service.get_upcoming_anniversaries(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=0
    )
    
    # Combine and return
    return birthdays_today + anniversaries_today


@router.get("/reminders/this-week", response_model=List[BirthdayReminder])
def get_this_weeks_reminders(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get birthdays and anniversaries happening this week (next 7 days).
    """
    tenant_id = request.state.tenant.id
    family_service = FamilyInformationService(db)
    
    # Get events happening in the next 7 days
    birthdays_this_week = family_service.get_upcoming_birthdays(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=7
    )
    
    anniversaries_this_week = family_service.get_upcoming_anniversaries(
        user_id=current_user.id,
        tenant_id=tenant_id,
        days_ahead=7
    )
    
    # Combine and return
    all_reminders = birthdays_this_week + anniversaries_this_week
    # Sort by days until event
    all_reminders.sort(key=lambda x: x.days_until)
    
    return all_reminders
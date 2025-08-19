from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import person as person_crud
from app.models.user import User
from app.schemas.person import (
    PersonProfile, PersonProfileCreate, PersonProfileUpdate, PersonComplete,
    PersonContactInfo, PersonContactInfoCreate, PersonContactInfoUpdate,
    PersonProfessionalInfo, PersonProfessionalInfoCreate, PersonProfessionalInfoUpdate,
    PersonPersonalInfo, PersonPersonalInfoCreate, PersonPersonalInfoUpdate,
    PersonLifeEvent, PersonLifeEventCreate, PersonLifeEventUpdate,
    PersonBelonging, PersonBelongingCreate, PersonBelongingUpdate
)

router = APIRouter()


# Person Profile endpoints
@router.get("/", response_model=List[PersonProfile])
def list_persons(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve persons visible to current user (their own persons + public persons in tenant).
    """
    persons = person_crud.get_user_persons(
        db, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return persons


@router.get("/search/", response_model=List[PersonProfile])
def search_persons(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search persons visible to current user (their own persons + public persons).
    """
    persons = person_crud.search_persons(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        query=q,
        skip=skip, 
        limit=limit
    )
    return persons


@router.post("/", response_model=PersonProfile)
def create_person(
    *,
    db: Session = Depends(deps.get_db),
    person_in: PersonProfileCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new person profile.
    """
    person = person_crud.create_person_profile(
        db, 
        obj_in=person_in, 
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id
    )
    return person


@router.get("/{person_id}", response_model=PersonComplete)
def get_person(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get person by ID with all related data.
    """
    person = person_crud.get_complete_person(
        db,
        person_id=person_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonProfile)
def update_person(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    person_in: PersonProfileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update person profile.
    """
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Check permissions (user must own the person or it must be public)
    if person.created_by_user_id != current_user.id and person.visibility != "public":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only owner can update
    if person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the person owner can update")
    
    person = person_crud.update_person_profile(db, db_obj=person, obj_in=person_in)
    return person


@router.delete("/{person_id}", response_model=PersonProfile)
def delete_person(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete person profile (soft delete).
    """
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Only owner can delete
    if person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the person owner can delete")
    
    person = person_crud.delete_person_profile(db, person_id=person_id)
    return person


# Contact Info endpoints
@router.get("/{person_id}/contact-info", response_model=List[PersonContactInfo])
def get_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contact information for a person.
    """
    # Verify person exists and user has access
    person = person_crud.get_person_profile_with_user_access(
        db, person_id=person_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    contact_info = person_crud.get_person_contact_info_by_person(db, person_id=person_id)
    return contact_info


@router.post("/{person_id}/contact-info", response_model=PersonContactInfo)
def create_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    contact_info_in: PersonContactInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create contact information for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    contact_info_in.person_id = person_id
    contact_info = person_crud.create_person_contact_info(db, obj_in=contact_info_in)
    return contact_info


@router.put("/{person_id}/contact-info/{contact_info_id}", response_model=PersonContactInfo)
def update_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    contact_info_id: int,
    contact_info_in: PersonContactInfoUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update contact information for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    from app.models.person import PersonContactInfo
    contact_info = db.query(PersonContactInfo).filter(PersonContactInfo.id == contact_info_id).first()
    if not contact_info or contact_info.person_id != person_id:
        raise HTTPException(status_code=404, detail="Contact info not found")
    
    contact_info = person_crud.update_person_contact_info(db, db_obj=contact_info, obj_in=contact_info_in)
    return contact_info


@router.delete("/{person_id}/contact-info/{contact_info_id}", response_model=PersonContactInfo)
def delete_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    contact_info_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete contact information for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    from app.models.person import PersonContactInfo
    contact_info = db.query(PersonContactInfo).filter(PersonContactInfo.id == contact_info_id).first()
    if not contact_info or contact_info.person_id != person_id:
        raise HTTPException(status_code=404, detail="Contact info not found")
    
    contact_info = person_crud.delete_person_contact_info(db, contact_info_id=contact_info_id)
    return contact_info


# Professional Info endpoints
@router.get("/{person_id}/professional-info", response_model=List[PersonProfessionalInfo])
def get_person_professional_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get professional information for a person.
    """
    # Verify person exists and user has access
    person = person_crud.get_person_profile_with_user_access(
        db, person_id=person_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    professional_info = person_crud.get_person_professional_info_by_person(db, person_id=person_id)
    return professional_info


@router.post("/{person_id}/professional-info", response_model=PersonProfessionalInfo)
def create_person_professional_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    professional_info_in: PersonProfessionalInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create professional information for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    professional_info_in.person_id = person_id
    professional_info = person_crud.create_person_professional_info(db, obj_in=professional_info_in)
    
    # If this is marked as current position, unset others
    if professional_info_in.is_current_position:
        person_crud.set_current_position(
            db, person_id=person_id, professional_info_id=professional_info.id
        )
    
    return professional_info


# Personal Info endpoints
@router.get("/{person_id}/personal-info", response_model=Optional[PersonPersonalInfo])
def get_person_personal_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get personal information for a person.
    """
    # Verify person exists and user has access
    person = person_crud.get_person_profile_with_user_access(
        db, person_id=person_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    personal_info = person_crud.get_person_personal_info_by_person(db, person_id=person_id)
    return personal_info


@router.post("/{person_id}/personal-info", response_model=PersonPersonalInfo)
def create_person_personal_info(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    personal_info_in: PersonPersonalInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create personal information for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    # Check if personal info already exists
    existing = person_crud.get_person_personal_info_by_person(db, person_id=person_id)
    if existing:
        raise HTTPException(status_code=400, detail="Personal info already exists for this person")
    
    personal_info_in.person_id = person_id
    personal_info = person_crud.create_person_personal_info(db, obj_in=personal_info_in)
    return personal_info


# Life Events endpoints
@router.get("/{person_id}/life-events", response_model=List[PersonLifeEvent])
def get_person_life_events(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get life events for a person.
    """
    # Verify person exists and user has access
    person = person_crud.get_person_profile_with_user_access(
        db, person_id=person_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    life_events = person_crud.get_person_life_events_by_person(db, person_id=person_id)
    return life_events


@router.post("/{person_id}/life-events", response_model=PersonLifeEvent)
def create_person_life_event(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    life_event_in: PersonLifeEventCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create life event for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    life_event_in.person_id = person_id
    life_event = person_crud.create_person_life_event(db, obj_in=life_event_in)
    return life_event


# Belongings endpoints
@router.get("/{person_id}/belongings", response_model=List[PersonBelonging])
def get_person_belongings(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get belongings for a person.
    """
    # Verify person exists and user has access
    person = person_crud.get_person_profile_with_user_access(
        db, person_id=person_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    belongings = person_crud.get_person_belongings_by_person(db, person_id=person_id)
    return belongings


@router.post("/{person_id}/belongings", response_model=PersonBelonging)
def create_person_belonging(
    *,
    db: Session = Depends(deps.get_db),
    person_id: int,
    belonging_in: PersonBelongingCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create belonging for a person.
    """
    # Verify person exists and user owns it
    person = person_crud.get_person_profile(db, person_id=person_id, tenant_id=current_user.tenant_id)
    if not person or person.created_by_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    
    belonging_in.person_id = person_id
    belonging = person_crud.create_person_belonging(db, obj_in=belonging_in)
    return belonging


# Utility endpoints
@router.get("/upcoming-events/", response_model=List[PersonLifeEvent])
def get_upcoming_events(
    *,
    db: Session = Depends(deps.get_db),
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get upcoming life events for the current user's tenant.
    """
    events = person_crud.get_upcoming_events(
        db, tenant_id=current_user.tenant_id, days_ahead=days_ahead
    )
    return events


@router.get("/emergency-contacts/", response_model=List[PersonPersonalInfo])
def get_emergency_contacts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get emergency contacts for the current user's tenant.
    """
    emergency_contacts = person_crud.get_emergency_contacts(
        db, tenant_id=current_user.tenant_id
    )
    return emergency_contacts


@router.get("/borrowed-items/", response_model=List[PersonBelonging])
def get_borrowed_items(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get borrowed items for the current user's tenant.
    """
    borrowed_items = person_crud.get_borrowed_items(
        db, tenant_id=current_user.tenant_id
    )
    return borrowed_items
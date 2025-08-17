"""
API endpoints for Relationship Management - Person Profiles.
This is the new normalized approach to managing person information.
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import person_profile as person_crud
from app.models.user import User
from app.schemas.person_profile import (
    PersonProfile, PersonProfileCreate, PersonProfileUpdate, PersonProfileSummary,
    PersonContactInfo, PersonContactInfoCreate, PersonContactInfoUpdate,
    PersonProfessionalInfo, PersonProfessionalInfoCreate, PersonProfessionalInfoUpdate,
    PersonPersonalInfo, PersonPersonalInfoCreate, PersonPersonalInfoUpdate,
    PersonLifeEvent, PersonLifeEventCreate, PersonLifeEventUpdate,
    PersonBelonging, PersonBelongingCreate, PersonBelongingUpdate,
    PersonRelationship, PersonRelationshipCreate, PersonRelationshipUpdate
)

router = APIRouter()


# Person Profile endpoints
@router.get("/profiles/", response_model=List[PersonProfileSummary])
def list_person_profiles(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List person profiles visible to current user (their own + tenant-shared).
    """
    profiles = person_crud.get_user_person_profiles(
        db, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return profiles


@router.get("/profiles/search/", response_model=List[PersonProfileSummary])
def search_person_profiles(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search person profiles by name.
    """
    profiles = person_crud.search_person_profiles(
        db,
        query=q,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return profiles


@router.post("/profiles/", response_model=PersonProfile)
def create_person_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: PersonProfileCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new person profile. Only requires a name to start.
    """
    # Check for duplicate name
    existing_profile = person_crud.get_person_profile_by_name(
        db, 
        first_name=profile_in.first_name, 
        last_name=profile_in.last_name,
        tenant_id=current_user.tenant_id
    )
    if existing_profile:
        raise HTTPException(
            status_code=400, 
            detail="Person profile with this name already exists"
        )
    
    profile = person_crud.create_person_profile(
        db, 
        obj_in=profile_in, 
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id
    )
    return profile


@router.get("/profiles/{profile_id}", response_model=PersonProfile)
def get_person_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get person profile by ID.
    """
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    # Check access rights
    if profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    return profile


@router.put("/profiles/{profile_id}", response_model=PersonProfile)
def update_person_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    profile_in: PersonProfileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update person profile. Only the creator can update it.
    """
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    # Check ownership
    if profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can update this profile")
    
    profile = person_crud.update_person_profile(db, db_obj=profile, obj_in=profile_in)
    return profile


@router.delete("/profiles/{profile_id}")
def delete_person_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete person profile. Only the creator can delete it.
    """
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    # Check ownership
    if profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can delete this profile")
    
    person_crud.delete_person_profile(db, profile_id=profile_id)
    return {"detail": "Person profile deleted successfully"}


# Contact Information endpoints
@router.get("/profiles/{profile_id}/contact-info/", response_model=List[PersonContactInfo])
def get_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contact information for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    contact_info = person_crud.get_person_contact_info_by_person(
        db, person_id=profile_id, tenant_id=current_user.tenant_id
    )
    return contact_info


@router.post("/profiles/{profile_id}/contact-info/", response_model=PersonContactInfo)
def create_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    contact_info_in: PersonContactInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add contact information to a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can add contact info")
    
    contact_info_in.person_id = profile_id
    contact_info = person_crud.create_person_contact_info(
        db, obj_in=contact_info_in, tenant_id=current_user.tenant_id
    )
    return contact_info


@router.put("/profiles/{profile_id}/contact-info/{contact_info_id}", response_model=PersonContactInfo)
def update_person_contact_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    contact_info_id: int,
    contact_info_in: PersonContactInfoUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update contact information for a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can update contact info")
    
    contact_info = person_crud.get_person_contact_info(db, id=contact_info_id)
    if not contact_info or contact_info.person_id != profile_id:
        raise HTTPException(status_code=404, detail="Contact info not found")
    
    contact_info = person_crud.update_person_contact_info(db, db_obj=contact_info, obj_in=contact_info_in)
    return contact_info


# Professional Information endpoints
@router.get("/profiles/{profile_id}/professional-info/", response_model=List[PersonProfessionalInfo])
def get_person_professional_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get professional information for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    professional_info = person_crud.get_person_professional_info_by_person(
        db, person_id=profile_id, tenant_id=current_user.tenant_id
    )
    return professional_info


@router.post("/profiles/{profile_id}/professional-info/", response_model=PersonProfessionalInfo)
def create_person_professional_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    professional_info_in: PersonProfessionalInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add professional information to a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can add professional info")
    
    professional_info_in.person_id = profile_id
    professional_info = person_crud.create_person_professional_info(
        db, obj_in=professional_info_in, tenant_id=current_user.tenant_id
    )
    return professional_info


# Personal Information endpoints
@router.get("/profiles/{profile_id}/personal-info/", response_model=List[PersonPersonalInfo])
def get_person_personal_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get personal information for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    personal_info = person_crud.get_person_personal_info_by_person(
        db, person_id=profile_id, tenant_id=current_user.tenant_id
    )
    return personal_info


@router.post("/profiles/{profile_id}/personal-info/", response_model=PersonPersonalInfo)
def create_person_personal_info(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    personal_info_in: PersonPersonalInfoCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add personal information to a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can add personal info")
    
    personal_info_in.person_id = profile_id
    personal_info = person_crud.create_person_personal_info(
        db, obj_in=personal_info_in, tenant_id=current_user.tenant_id
    )
    return personal_info


# Life Events endpoints
@router.get("/profiles/{profile_id}/life-events/", response_model=List[PersonLifeEvent])
def get_person_life_events(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get life events for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    life_events = person_crud.get_person_life_events_by_person(
        db, person_id=profile_id, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return life_events


@router.post("/profiles/{profile_id}/life-events/", response_model=PersonLifeEvent)
def create_person_life_event(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    life_event_in: PersonLifeEventCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a life event to a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can add life events")
    
    life_event_in.person_id = profile_id
    life_event = person_crud.create_person_life_event(
        db, obj_in=life_event_in, tenant_id=current_user.tenant_id
    )
    return life_event


# Belongings endpoints
@router.get("/profiles/{profile_id}/belongings/", response_model=List[PersonBelonging])
def get_person_belongings(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True, description="Only return active belongings"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get belongings for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    belongings = person_crud.get_person_belongings_by_person(
        db, person_id=profile_id, tenant_id=current_user.tenant_id, 
        skip=skip, limit=limit, active_only=active_only
    )
    return belongings


@router.post("/profiles/{profile_id}/belongings/", response_model=PersonBelonging)
def create_person_belonging(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    belonging_in: PersonBelongingCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a belonging to a person profile.
    """
    # Check profile ownership
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id or profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can add belongings")
    
    belonging_in.person_id = profile_id
    belonging = person_crud.create_person_belonging(
        db, obj_in=belonging_in, tenant_id=current_user.tenant_id
    )
    return belonging


# Relationships endpoints
@router.get("/profiles/{profile_id}/relationships/", response_model=List[PersonRelationship])
def get_person_relationships(
    *,
    db: Session = Depends(deps.get_db),
    profile_id: int,
    include_inactive: bool = Query(False, description="Include inactive relationships"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get relationships for a person profile.
    """
    # Check profile access first
    profile = person_crud.get_person_profile(db, profile_id=profile_id, tenant_id=current_user.tenant_id)
    if not profile or profile.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    if profile.visibility == "private" and profile.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private profile")
    
    relationships = person_crud.get_person_relationships(
        db, person_id=profile_id, tenant_id=current_user.tenant_id, include_inactive=include_inactive
    )
    return relationships


@router.post("/relationships/", response_model=PersonRelationship)
def create_person_relationship(
    *,
    db: Session = Depends(deps.get_db),
    relationship_in: PersonRelationshipCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a relationship between two person profiles.
    """
    # Check both profiles exist and are accessible
    profile_a = person_crud.get_person_profile(db, profile_id=relationship_in.person_a_id, tenant_id=current_user.tenant_id)
    profile_b = person_crud.get_person_profile(db, profile_id=relationship_in.person_b_id, tenant_id=current_user.tenant_id)
    
    if not profile_a or not profile_b:
        raise HTTPException(status_code=404, detail="One or both person profiles not found")
    
    if profile_a.tenant_id != current_user.tenant_id or profile_b.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Cannot create relationships between different tenants")
    
    # Check if relationship already exists
    existing = person_crud.get_person_relationship_between(
        db, person_a_id=relationship_in.person_a_id, person_b_id=relationship_in.person_b_id,
        tenant_id=current_user.tenant_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists between these profiles")
    
    relationship = person_crud.create_person_relationship(
        db, obj_in=relationship_in, tenant_id=current_user.tenant_id, created_by_user_id=current_user.id
    )
    return relationship
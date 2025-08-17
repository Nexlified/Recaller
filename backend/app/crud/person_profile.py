"""
CRUD operations for Person Profile models.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.person_profile import (
    PersonProfile, PersonContactInfo, PersonProfessionalInfo,
    PersonPersonalInfo, PersonLifeEvent, PersonBelonging, PersonRelationship
)
from app.schemas.person_profile import (
    PersonProfileCreate, PersonProfileUpdate,
    PersonContactInfoCreate, PersonContactInfoUpdate,
    PersonProfessionalInfoCreate, PersonProfessionalInfoUpdate,
    PersonPersonalInfoCreate, PersonPersonalInfoUpdate,
    PersonLifeEventCreate, PersonLifeEventUpdate,
    PersonBelongingCreate, PersonBelongingUpdate,
    PersonRelationshipCreate, PersonRelationshipUpdate
)


# PersonProfile CRUD functions
def create_person_profile(
    db: Session, *, obj_in: PersonProfileCreate, tenant_id: int, created_by_user_id: int
) -> PersonProfile:
    """Create a new person profile."""
    db_obj = PersonProfile(
        **obj_in.dict(),
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_profile(db: Session, profile_id: int, tenant_id: int) -> Optional[PersonProfile]:
    """Get person profile by ID and tenant."""
    return db.query(PersonProfile).filter(
        PersonProfile.id == profile_id,
        PersonProfile.tenant_id == tenant_id
    ).first()


def update_person_profile(
    db: Session, *, db_obj: PersonProfile, obj_in: PersonProfileUpdate
) -> PersonProfile:
    """Update a person profile."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_person_profile(db: Session, profile_id: int) -> None:
    """Delete a person profile."""
    db.query(PersonProfile).filter(PersonProfile.id == profile_id).delete()
    db.commit()


def get_user_person_profiles(
    db: Session, *, user_id: int, tenant_id: int, skip: int = 0, limit: int = 100
) -> List[PersonProfile]:
    """Get person profiles visible to the user (their own + tenant-shared)."""
    return db.query(PersonProfile).filter(
        and_(
            PersonProfile.tenant_id == tenant_id,
            # User can see their own profiles + tenant-shared profiles
            or_(
                PersonProfile.created_by_user_id == user_id,
                PersonProfile.visibility == "tenant_shared"
            )
        )
    ).offset(skip).limit(limit).all()


def get_person_profile_by_name(
    db: Session, *, first_name: str, last_name: Optional[str], tenant_id: int
) -> Optional[PersonProfile]:
    """Find person profile by name within tenant."""
    query = db.query(PersonProfile).filter(
        and_(
            PersonProfile.tenant_id == tenant_id,
            PersonProfile.first_name == first_name
        )
    )
    if last_name:
        query = query.filter(PersonProfile.last_name == last_name)
    else:
        query = query.filter(PersonProfile.last_name.is_(None))
    return query.first()


def search_person_profiles(
    db: Session, *, query: str, user_id: int, tenant_id: int, skip: int = 0, limit: int = 100
) -> List[PersonProfile]:
    """Search person profiles by name."""
    search_filter = or_(
        PersonProfile.first_name.ilike(f"%{query}%"),
        PersonProfile.last_name.ilike(f"%{query}%"),
        PersonProfile.display_name.ilike(f"%{query}%")
    )
    
    return db.query(PersonProfile).filter(
        and_(
            PersonProfile.tenant_id == tenant_id,
            search_filter,
            # User can see their own profiles + tenant-shared profiles
            or_(
                PersonProfile.created_by_user_id == user_id,
                PersonProfile.visibility == "tenant_shared"
            )
        )
    ).offset(skip).limit(limit).all()


# PersonContactInfo CRUD functions
def create_person_contact_info(
    db: Session, *, obj_in: PersonContactInfoCreate, tenant_id: int
) -> PersonContactInfo:
    """Create contact information for a person."""
    db_obj = PersonContactInfo(
        **obj_in.dict(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_contact_info_by_person(
    db: Session, *, person_id: int, tenant_id: int
) -> List[PersonContactInfo]:
    """Get all contact info for a person."""
    return db.query(PersonContactInfo).filter(
        and_(
            PersonContactInfo.person_id == person_id,
            PersonContactInfo.tenant_id == tenant_id
        )
    ).all()


def get_primary_person_contact_info(
    db: Session, *, person_id: int, tenant_id: int
) -> Optional[PersonContactInfo]:
    """Get primary contact info for a person."""
    return db.query(PersonContactInfo).filter(
        and_(
            PersonContactInfo.person_id == person_id,
            PersonContactInfo.tenant_id == tenant_id,
            PersonContactInfo.is_primary == True
        )
    ).first()


def update_person_contact_info(
    db: Session, *, db_obj: PersonContactInfo, obj_in: PersonContactInfoUpdate
) -> PersonContactInfo:
    """Update person contact info."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_contact_info(db: Session, contact_info_id: int) -> Optional[PersonContactInfo]:
    """Get person contact info by ID."""
    return db.query(PersonContactInfo).filter(PersonContactInfo.id == contact_info_id).first()


# PersonProfessionalInfo CRUD functions
def create_person_professional_info(
    db: Session, *, obj_in: PersonProfessionalInfoCreate, tenant_id: int
) -> PersonProfessionalInfo:
    """Create professional information for a person."""
    db_obj = PersonProfessionalInfo(
        **obj_in.dict(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_professional_info_by_person(
    db: Session, *, person_id: int, tenant_id: int
) -> List[PersonProfessionalInfo]:
    """Get all professional info for a person."""
    return db.query(PersonProfessionalInfo).filter(
        and_(
            PersonProfessionalInfo.person_id == person_id,
            PersonProfessionalInfo.tenant_id == tenant_id
        )
    ).order_by(PersonProfessionalInfo.start_date.desc()).all()


def get_current_person_professional_info(
    db: Session, *, person_id: int, tenant_id: int
) -> Optional[PersonProfessionalInfo]:
    """Get current professional info for a person."""
    return db.query(PersonProfessionalInfo).filter(
        and_(
            PersonProfessionalInfo.person_id == person_id,
            PersonProfessionalInfo.tenant_id == tenant_id,
            PersonProfessionalInfo.is_current == True
        )
    ).first()


# PersonPersonalInfo CRUD functions
def create_person_personal_info(
    db: Session, *, obj_in: PersonPersonalInfoCreate, tenant_id: int
) -> PersonPersonalInfo:
    """Create personal information for a person."""
    db_obj = PersonPersonalInfo(
        **obj_in.dict(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_personal_info_by_person(
    db: Session, *, person_id: int, tenant_id: int
) -> List[PersonPersonalInfo]:
    """Get all personal info for a person."""
    return db.query(PersonPersonalInfo).filter(
        and_(
            PersonPersonalInfo.person_id == person_id,
            PersonPersonalInfo.tenant_id == tenant_id
        )
    ).all()


# PersonLifeEvent CRUD functions
def create_person_life_event(
    db: Session, *, obj_in: PersonLifeEventCreate, tenant_id: int
) -> PersonLifeEvent:
    """Create a life event for a person."""
    db_obj = PersonLifeEvent(
        **obj_in.dict(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_life_events_by_person(
    db: Session, *, person_id: int, tenant_id: int, skip: int = 0, limit: int = 100
) -> List[PersonLifeEvent]:
    """Get life events for a person."""
    return db.query(PersonLifeEvent).filter(
        and_(
            PersonLifeEvent.person_id == person_id,
            PersonLifeEvent.tenant_id == tenant_id
        )
    ).order_by(PersonLifeEvent.event_date.desc()).offset(skip).limit(limit).all()


# PersonBelonging CRUD functions
def create_person_belonging(
    db: Session, *, obj_in: PersonBelongingCreate, tenant_id: int
) -> PersonBelonging:
    """Create a belonging for a person."""
    db_obj = PersonBelonging(
        **obj_in.dict(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_belongings_by_person(
    db: Session, *, person_id: int, tenant_id: int, skip: int = 0, limit: int = 100, 
    active_only: bool = True
) -> List[PersonBelonging]:
    """Get belongings for a person."""
    query = db.query(PersonBelonging).filter(
        and_(
            PersonBelonging.person_id == person_id,
            PersonBelonging.tenant_id == tenant_id
        )
    )
    if active_only:
        query = query.filter(PersonBelonging.is_active == True)
    
    return query.order_by(PersonBelonging.created_at.desc()).offset(skip).limit(limit).all()


# PersonRelationship CRUD functions
def create_person_relationship(
    db: Session, *, obj_in: PersonRelationshipCreate, tenant_id: int, created_by_user_id: int
) -> PersonRelationship:
    """Create a relationship between two persons."""
    db_obj = PersonRelationship(
        **obj_in.dict(),
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_person_relationships(
    db: Session, *, person_id: int, tenant_id: int, include_inactive: bool = False
) -> List[PersonRelationship]:
    """Get all relationships for a person."""
    query = db.query(PersonRelationship).filter(
        and_(
            PersonRelationship.tenant_id == tenant_id,
            or_(
                PersonRelationship.person_a_id == person_id,
                PersonRelationship.person_b_id == person_id
            )
        )
    )
    
    if not include_inactive:
        query = query.filter(PersonRelationship.is_active == True)
    
    return query.all()


def get_person_relationship_between(
    db: Session, *, person_a_id: int, person_b_id: int, tenant_id: int
) -> Optional[PersonRelationship]:
    """Get relationship between two specific persons."""
    return db.query(PersonRelationship).filter(
        and_(
            PersonRelationship.tenant_id == tenant_id,
            or_(
                and_(
                    PersonRelationship.person_a_id == person_a_id,
                    PersonRelationship.person_b_id == person_b_id
                ),
                and_(
                    PersonRelationship.person_a_id == person_b_id,
                    PersonRelationship.person_b_id == person_a_id
                )
            )
        )
    ).first()
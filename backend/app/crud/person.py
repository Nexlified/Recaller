from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.models.person import (
    PersonProfile, PersonContactInfo, PersonProfessionalInfo, 
    PersonPersonalInfo, PersonLifeEvent, PersonBelonging
)
from app.schemas.person import (
    PersonProfileCreate, PersonProfileUpdate,
    PersonContactInfoCreate, PersonContactInfoUpdate,
    PersonProfessionalInfoCreate, PersonProfessionalInfoUpdate,
    PersonPersonalInfoCreate, PersonPersonalInfoUpdate,
    PersonLifeEventCreate, PersonLifeEventUpdate,
    PersonBelongingCreate, PersonBelongingUpdate
)


# PersonProfile CRUD functions
def get_person_profile(db: Session, person_id: int, tenant_id: int) -> Optional[PersonProfile]:
    """Get person profile by ID within tenant"""
    return db.query(PersonProfile).filter(
        PersonProfile.id == person_id,
        PersonProfile.tenant_id == tenant_id
    ).first()


def get_person_profile_with_user_access(
    db: Session, 
    person_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[PersonProfile]:
    """Get person profile if user has access (owns it or it's public)"""
    return db.query(PersonProfile).filter(
        PersonProfile.id == person_id,
        PersonProfile.tenant_id == tenant_id,
        PersonProfile.is_active == True,
        or_(
            PersonProfile.created_by_user_id == user_id,
            PersonProfile.visibility == "public"
        )
    ).first()


def get_persons_by_tenant(
    db: Session,
    *,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[PersonProfile]:
    """Get all person profiles for a tenant"""
    return (
        db.query(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonProfile.is_active == True
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_persons(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[PersonProfile]:
    """Get persons visible to user (their own + public ones in tenant)"""
    return (
        db.query(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonProfile.is_active == True,
                or_(
                    PersonProfile.created_by_user_id == user_id,
                    PersonProfile.visibility == "public"
                )
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_persons(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[PersonProfile]:
    """Search persons by name"""
    search_term = f"%{query}%"
    return (
        db.query(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonProfile.is_active == True,
                or_(
                    PersonProfile.created_by_user_id == user_id,
                    PersonProfile.visibility == "public"
                ),
                or_(
                    PersonProfile.first_name.ilike(search_term),
                    PersonProfile.last_name.ilike(search_term)
                )
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_complete_person(
    db: Session,
    *,
    person_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[PersonProfile]:
    """Get complete person with all related data"""
    person = (
        db.query(PersonProfile)
        .options(
            joinedload(PersonProfile.contact_info),
            joinedload(PersonProfile.professional_info),
            joinedload(PersonProfile.personal_info),
            joinedload(PersonProfile.life_events),
            joinedload(PersonProfile.belongings)
        )
        .filter(
            and_(
                PersonProfile.id == person_id,
                PersonProfile.tenant_id == tenant_id,
                PersonProfile.is_active == True,
                or_(
                    PersonProfile.created_by_user_id == user_id,
                    PersonProfile.visibility == "public"
                )
            )
        )
        .first()
    )
    return person


def create_person_profile(
    db: Session,
    *,
    obj_in: PersonProfileCreate,
    tenant_id: int,
    created_by_user_id: int
) -> PersonProfile:
    """Create person profile with tenant and user info"""
    obj_in_data = obj_in.dict()
    obj_in_data.update({
        "tenant_id": tenant_id,
        "created_by_user_id": created_by_user_id
    })
    db_obj = PersonProfile(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_person_profile(
    db: Session,
    *,
    db_obj: PersonProfile,
    obj_in: Union[PersonProfileUpdate, Dict[str, Any]]
) -> PersonProfile:
    """Update person profile"""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_person_profile(db: Session, *, person_id: int) -> PersonProfile:
    """Soft delete person profile"""
    db_obj = db.query(PersonProfile).filter(PersonProfile.id == person_id).first()
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


# PersonContactInfo CRUD functions
def get_person_contact_info_by_person(
    db: Session,
    *,
    person_id: int
) -> List[PersonContactInfo]:
    """Get all contact info for a person"""
    return (
        db.query(PersonContactInfo)
        .filter(
            and_(
                PersonContactInfo.person_id == person_id,
                PersonContactInfo.is_active == True
            )
        )
        .order_by(PersonContactInfo.sort_order, PersonContactInfo.id)
        .all()
    )


def get_primary_email(
    db: Session,
    *,
    person_id: int
) -> Optional[PersonContactInfo]:
    """Get primary email for a person"""
    return (
        db.query(PersonContactInfo)
        .filter(
            and_(
                PersonContactInfo.person_id == person_id,
                PersonContactInfo.contact_type == "email",
                PersonContactInfo.is_primary == True,
                PersonContactInfo.is_active == True
            )
        )
        .first()
    )


def get_primary_phone(
    db: Session,
    *,
    person_id: int
) -> Optional[PersonContactInfo]:
    """Get primary phone for a person"""
    return (
        db.query(PersonContactInfo)
        .filter(
            and_(
                PersonContactInfo.person_id == person_id,
                PersonContactInfo.contact_type == "phone",
                PersonContactInfo.is_primary == True,
                PersonContactInfo.is_active == True
            )
        )
        .first()
    )


def create_person_contact_info(
    db: Session,
    *,
    obj_in: PersonContactInfoCreate
) -> PersonContactInfo:
    """Create person contact info"""
    obj_in_data = obj_in.dict()
    db_obj = PersonContactInfo(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_person_contact_info(
    db: Session,
    *,
    db_obj: PersonContactInfo,
    obj_in: Union[PersonContactInfoUpdate, Dict[str, Any]]
) -> PersonContactInfo:
    """Update person contact info"""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_person_contact_info(db: Session, *, contact_info_id: int) -> PersonContactInfo:
    """Soft delete person contact info"""
    db_obj = db.query(PersonContactInfo).filter(PersonContactInfo.id == contact_info_id).first()
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


# PersonProfessionalInfo CRUD functions
def get_person_professional_info_by_person(
    db: Session,
    *,
    person_id: int
) -> List[PersonProfessionalInfo]:
    """Get all professional info for a person"""
    return (
        db.query(PersonProfessionalInfo)
        .filter(
            and_(
                PersonProfessionalInfo.person_id == person_id,
                PersonProfessionalInfo.is_active == True
            )
        )
        .order_by(PersonProfessionalInfo.is_current_position.desc(), PersonProfessionalInfo.start_date.desc())
        .all()
    )


def get_current_position(
    db: Session,
    *,
    person_id: int
) -> Optional[PersonProfessionalInfo]:
    """Get current position for a person"""
    return (
        db.query(PersonProfessionalInfo)
        .filter(
            and_(
                PersonProfessionalInfo.person_id == person_id,
                PersonProfessionalInfo.is_current_position == True,
                PersonProfessionalInfo.is_active == True
            )
        )
        .first()
    )


def set_current_position(
    db: Session,
    *,
    person_id: int,
    professional_info_id: int
) -> None:
    """Set a professional info record as the current position"""
    # First, unset all current positions for this person
    db.query(PersonProfessionalInfo).filter(
        and_(
            PersonProfessionalInfo.person_id == person_id,
            PersonProfessionalInfo.is_current_position == True
        )
    ).update({"is_current_position": False})
    
    # Then set the specified one as current
    db.query(PersonProfessionalInfo).filter(
        PersonProfessionalInfo.id == professional_info_id
    ).update({"is_current_position": True})
    
    db.commit()


def create_person_professional_info(
    db: Session,
    *,
    obj_in: PersonProfessionalInfoCreate
) -> PersonProfessionalInfo:
    """Create person professional info"""
    obj_in_data = obj_in.dict()
    db_obj = PersonProfessionalInfo(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# PersonPersonalInfo CRUD functions
def get_person_personal_info_by_person(
    db: Session,
    *,
    person_id: int
) -> Optional[PersonPersonalInfo]:
    """Get personal info for a person (should be unique)"""
    return (
        db.query(PersonPersonalInfo)
        .filter(
            and_(
                PersonPersonalInfo.person_id == person_id,
                PersonPersonalInfo.is_active == True
            )
        )
        .first()
    )


def get_emergency_contacts(
    db: Session,
    *,
    tenant_id: int
) -> List[PersonPersonalInfo]:
    """Get all emergency contacts for a tenant"""
    return (
        db.query(PersonPersonalInfo)
        .join(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonPersonalInfo.is_emergency_contact == True,
                PersonPersonalInfo.is_active == True,
                PersonProfile.is_active == True
            )
        )
        .order_by(PersonPersonalInfo.emergency_contact_priority)
        .all()
    )


def create_person_personal_info(
    db: Session,
    *,
    obj_in: PersonPersonalInfoCreate
) -> PersonPersonalInfo:
    """Create person personal info"""
    obj_in_data = obj_in.dict()
    db_obj = PersonPersonalInfo(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# PersonLifeEvent CRUD functions
def get_person_life_events_by_person(
    db: Session,
    *,
    person_id: int
) -> List[PersonLifeEvent]:
    """Get all life events for a person"""
    return (
        db.query(PersonLifeEvent)
        .filter(
            and_(
                PersonLifeEvent.person_id == person_id,
                PersonLifeEvent.is_active == True
            )
        )
        .order_by(PersonLifeEvent.event_date.desc())
        .all()
    )


def get_upcoming_events(
    db: Session,
    *,
    tenant_id: int,
    days_ahead: int = 30
) -> List[PersonLifeEvent]:
    """Get upcoming life events for a tenant"""
    from datetime import date, timedelta
    end_date = date.today() + timedelta(days=days_ahead)
    
    return (
        db.query(PersonLifeEvent)
        .join(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonLifeEvent.should_remind == True,
                PersonLifeEvent.event_date <= end_date,
                PersonLifeEvent.is_active == True,
                PersonProfile.is_active == True
            )
        )
        .order_by(PersonLifeEvent.event_date)
        .all()
    )


def create_person_life_event(
    db: Session,
    *,
    obj_in: PersonLifeEventCreate
) -> PersonLifeEvent:
    """Create person life event"""
    obj_in_data = obj_in.dict()
    db_obj = PersonLifeEvent(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# PersonBelonging CRUD functions
def get_person_belongings_by_person(
    db: Session,
    *,
    person_id: int
) -> List[PersonBelonging]:
    """Get all belongings for a person"""
    return (
        db.query(PersonBelonging)
        .filter(
            and_(
                PersonBelonging.person_id == person_id,
                PersonBelonging.is_active == True
            )
        )
        .order_by(PersonBelonging.date_acquired.desc())
        .all()
    )


def get_borrowed_items(
    db: Session,
    *,
    tenant_id: int
) -> List[PersonBelonging]:
    """Get all borrowed items for a tenant"""
    return (
        db.query(PersonBelonging)
        .join(PersonProfile)
        .filter(
            and_(
                PersonProfile.tenant_id == tenant_id,
                PersonBelonging.is_borrowed == True,
                PersonBelonging.is_active == True,
                PersonProfile.is_active == True
            )
        )
        .order_by(PersonBelonging.expected_return_date)
        .all()
    )


def get_gifts_received(
    db: Session,
    *,
    person_id: int
) -> List[PersonBelonging]:
    """Get gifts received by a person"""
    return (
        db.query(PersonBelonging)
        .filter(
            and_(
                PersonBelonging.person_id == person_id,
                PersonBelonging.belonging_type == "gift_received",
                PersonBelonging.is_active == True
            )
        )
        .order_by(PersonBelonging.date_acquired.desc())
        .all()
    )


def create_person_belonging(
    db: Session,
    *,
    obj_in: PersonBelongingCreate
) -> PersonBelonging:
    """Create person belonging"""
    obj_in_data = obj_in.dict()
    db_obj = PersonBelonging(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
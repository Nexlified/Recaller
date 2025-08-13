from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.contact import Contact, ContactVisibility
from app.schemas.contact import ContactCreate, ContactUpdate

def get_contact(db: Session, contact_id: int, tenant_id: int = 1) -> Optional[Contact]:
    return db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.tenant_id == tenant_id
    ).first()


def get_contact_with_user_access(
    db: Session, 
    contact_id: int, 
    user_id: int, 
    tenant_id: int = 1
) -> Optional[Contact]:
    """Get contact if user has access (owns it or it's public)"""
    return db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.tenant_id == tenant_id,
            or_(
                Contact.created_by_user_id == user_id,  # User owns the contact
                Contact.visibility == ContactVisibility.PUBLIC.value  # Contact is public
            )
        )
    ).first()


def can_user_edit_contact(contact: Contact, user_id: int) -> bool:
    """Check if user can edit the contact (only owner can edit)"""
    return contact.created_by_user_id == user_id

def get_contact_by_email(db: Session, email: str, tenant_id: int = 1) -> Optional[Contact]:
    return db.query(Contact).filter(
        Contact.email == email,
        Contact.tenant_id == tenant_id
    ).first()

def get_contacts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: int = 1
) -> List[Contact]:
    """Get all contacts in tenant (admin function - returns all contacts)"""
    return db.query(Contact).filter(
        Contact.tenant_id == tenant_id
    ).offset(skip).limit(limit).all()


def get_user_contacts(
    db: Session, 
    user_id: int,
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: int = 1
) -> List[Contact]:
    """Get contacts visible to a specific user (their own + public contacts in tenant)"""
    return db.query(Contact).filter(
        and_(
            Contact.tenant_id == tenant_id,
            or_(
                Contact.created_by_user_id == user_id,  # User's own contacts
                Contact.visibility == ContactVisibility.PUBLIC.value  # Public contacts
            )
        )
    ).offset(skip).limit(limit).all()


def get_public_contacts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: int = 1
) -> List[Contact]:
    """Get only public contacts in tenant"""
    return db.query(Contact).filter(
        and_(
            Contact.tenant_id == tenant_id,
            Contact.visibility == ContactVisibility.PUBLIC.value
        )
    ).offset(skip).limit(limit).all()


def get_contacts_by_email(
    db: Session, 
    email: str, 
    tenant_id: int
) -> List[Contact]:
    return db.query(Contact).filter(
        Contact.email == email,
        Contact.tenant_id == tenant_id
    ).all()


def get_contact_by_phone(db: Session, phone: str, tenant_id: int = 1) -> Optional[Contact]:
    return db.query(Contact).filter(
        Contact.phone == phone,
        Contact.tenant_id == tenant_id
    ).first()


def get_contacts_by_phone(
    db: Session, 
    phone: str, 
    tenant_id: int
) -> List[Contact]:
    return db.query(Contact).filter(
        Contact.phone == phone,
        Contact.tenant_id == tenant_id
    ).all()


def create_contact(
    db: Session, 
    obj_in: ContactCreate, 
    created_by_user_id: int,
    tenant_id: int = 1
) -> Contact:
    db_obj = Contact(
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_contact(
    db: Session, 
    db_obj: Contact, 
    obj_in: Union[ContactUpdate, Dict[str, Any]]
) -> Contact:
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


def delete_contact(db: Session, contact_id: int, tenant_id: int) -> Optional[Contact]:
    contact = get_contact(db, contact_id=contact_id, tenant_id=tenant_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def search_contacts(
    db: Session,
    query: str,
    user_id: int,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Contact]:
    """Search contacts visible to user (their own + public contacts)"""
    return db.query(Contact).filter(
        and_(
            Contact.tenant_id == tenant_id,
            or_(
                Contact.created_by_user_id == user_id,  # User's own contacts
                Contact.visibility == ContactVisibility.PUBLIC.value  # Public contacts
            ),
            (Contact.first_name.ilike(f"%{query}%") |
             Contact.last_name.ilike(f"%{query}%") |
             Contact.email.ilike(f"%{query}%") |
             Contact.job_title.ilike(f"%{query}%"))
        )
    ).offset(skip).limit(limit).all()

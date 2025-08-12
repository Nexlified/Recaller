from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate

def get_contact(db: Session, contact_id: int, tenant_id: int = 1) -> Optional[Contact]:
    return db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.tenant_id == tenant_id
    ).first()

def get_contact_by_email(db: Session, email: str, tenant_id: int = 1) -> Optional[Contact]:
    return db.query(Contact).filter(
        Contact.email == email,
        Contact.tenant_id == tenant_id
    ).first()

def get_contacts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: int = 1,
    is_active: Optional[bool] = None
) -> List[Contact]:
    query = db.query(Contact).filter(Contact.tenant_id == tenant_id)
    
    if is_active is not None:
        query = query.filter(Contact.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

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

def delete_contact(db: Session, contact_id: int, tenant_id: int = 1) -> Optional[Contact]:
    contact = get_contact(db, contact_id=contact_id, tenant_id=tenant_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact
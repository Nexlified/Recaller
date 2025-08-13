from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import contact as contact_crud, event as event_crud
from app.models.user import User
from app.schemas.contact import Contact, ContactCreate, ContactUpdate
from app.schemas.event import ContactEventAttendance, Event

router = APIRouter()


@router.get("/", response_model=List[Contact])
def list_contacts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve contacts.
    """
    contacts = contact_crud.get_contacts(
        db, 
        skip=skip, 
        limit=limit, 
        tenant_id=current_user.tenant_id
    )
    return contacts


@router.get("/search/", response_model=List[Contact])
def search_contacts(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search contacts by name, email, company.
    """
    contacts = contact_crud.search_contacts(
        db, 
        query=q, 
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return contacts


@router.get("/{contact_id}", response_model=Contact)
def get_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contact by ID.
    """
    contact = contact_crud.get_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/validate/email/{email}")
def validate_email(
    *,
    db: Session = Depends(deps.get_db),
    email: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check if contact with email already exists.
    """
    contact = contact_crud.get_contact_by_email(
        db, 
        email=email, 
        tenant_id=current_user.tenant_id
    )
    return {"exists": contact is not None, "email": email}


@router.get("/validate/phone/{phone}")
def validate_phone(
    *,
    db: Session = Depends(deps.get_db),
    phone: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check if contact with phone already exists.
    """
    contact = contact_crud.get_contact_by_phone(
        db, 
        phone=phone, 
        tenant_id=current_user.tenant_id
    )
    return {"exists": contact is not None, "phone": phone}


@router.post("/", response_model=Contact)
def create_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_in: ContactCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new contact.
    """
    # Check for duplicate email
    if contact_in.email:
        existing_email = contact_crud.get_contact_by_email(
            db, 
            email=contact_in.email, 
            tenant_id=current_user.tenant_id
        )
        if existing_email:
            raise HTTPException(
                status_code=400, 
                detail="Contact with this email already exists"
            )
    
    # Check for duplicate phone
    if contact_in.phone:
        existing_phone = contact_crud.get_contact_by_phone(
            db, 
            phone=contact_in.phone, 
            tenant_id=current_user.tenant_id
        )
        if existing_phone:
            raise HTTPException(
                status_code=400, 
                detail="Contact with this phone number already exists"
            )
    
    contact = contact_crud.create_contact(
        db, 
        obj_in=contact_in, 
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id
    )
    return contact


@router.put("/{contact_id}", response_model=Contact)
def update_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    contact_in: ContactUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update contact.
    """
    contact = contact_crud.get_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact = contact_crud.update_contact(db, db_obj=contact, obj_in=contact_in)
    return contact


@router.delete("/{contact_id}")
def delete_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete contact.
    """
    contact = contact_crud.delete_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"message": "Contact deleted successfully"}


# Contact-Event Integration
@router.get("/{contact_id}/events", response_model=List[ContactEventAttendance])
def get_contact_events(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get events attended by contact.
    """
    # Verify contact belongs to user's tenant
    contact = contact_crud.get_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    events = event_crud.get_contact_events(db, contact_id)
    return events


@router.get("/{contact_id}/shared-events/{other_contact_id}", response_model=List[Event])
def get_shared_events(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    other_contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get shared events between two contacts.
    """
    # Verify both contacts belong to user's tenant
    contact1 = contact_crud.get_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    contact2 = contact_crud.get_contact(
        db, 
        contact_id=other_contact_id, 
        tenant_id=current_user.tenant_id
    )
    
    if not contact1:
        raise HTTPException(status_code=404, detail="First contact not found")
    if not contact2:
        raise HTTPException(status_code=404, detail="Second contact not found")
    
    events = event_crud.get_shared_events(db, contact_id, other_contact_id)
    return events
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.models.organization import Organization
from app.schemas.contact import ContactCreate, ContactUpdate, ContactIntelligenceUpdate

class CRUDContact(CRUDBase[Contact, ContactCreate, ContactUpdate]):
    def get_by_email(self, db: Session, *, email: str, tenant_id: int) -> Optional[Contact]:
        return db.query(Contact).filter(
            Contact.email == email,
            Contact.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        return db.query(Contact).filter(
            Contact.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: ContactCreate, tenant_id: int
    ) -> Contact:
        obj_in_data = obj_in.dict()
        
        # Extract intelligence data if provided
        intelligence_data = obj_in_data.pop("intelligence", {}) or {}
        
        # Merge intelligence fields into the main contact data
        db_obj = Contact(**obj_in_data, **intelligence_data, tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_intelligence(
        self, db: Session, *, db_obj: Contact, obj_in: ContactIntelligenceUpdate
    ) -> Contact:
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_full_profile(self, db: Session, *, contact_id: int, tenant_id: int) -> Optional[Contact]:
        return db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.tenant_id == tenant_id
        ).first()

    def search_contacts(
        self, 
        db: Session, 
        *, 
        tenant_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contact]:
        search_query = f"%{query}%"
        return db.query(Contact).filter(
            Contact.tenant_id == tenant_id,
            (Contact.first_name.ilike(search_query) |
             Contact.last_name.ilike(search_query) |
             Contact.email.ilike(search_query))
        ).offset(skip).limit(limit).all()

    def get_follow_up_needed(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        """Get contacts that need follow-up based on urgency"""
        return db.query(Contact).filter(
            Contact.tenant_id == tenant_id,
            Contact.follow_up_urgency.in_(["high", "overdue"])
        ).order_by(desc(Contact.follow_up_urgency)).offset(skip).limit(limit).all()

    def get_by_relationship_strength(
        self, 
        db: Session, 
        *, 
        tenant_id: int,
        min_strength: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contact]:
        """Get contacts with high relationship strength"""
        return db.query(Contact).filter(
            Contact.tenant_id == tenant_id,
            Contact.connection_strength >= min_strength
        ).order_by(desc(Contact.connection_strength)).offset(skip).limit(limit).all()

    def get_by_networking_value(
        self, 
        db: Session, 
        *, 
        tenant_id: int,
        networking_value: str = "high",
        skip: int = 0,
        limit: int = 100
    ) -> List[Contact]:
        """Get contacts with specific networking value"""
        return db.query(Contact).filter(
            Contact.tenant_id == tenant_id,
            Contact.networking_value == networking_value
        ).order_by(desc(Contact.priority_score)).offset(skip).limit(limit).all()

contact = CRUDContact(Contact)
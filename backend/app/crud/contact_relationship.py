from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.contact_relationship import ContactRelationship
from app.models.contact import Contact
from app.schemas.contact_relationship import (
    ContactRelationshipCreate, 
    ContactRelationshipUpdate,
    ContactRelationshipPair
)
from app.services.relationship_mapping import relationship_mapping_service


def get_contact_relationship(
    db: Session, 
    relationship_id: int, 
    tenant_id: int
) -> Optional[ContactRelationship]:
    """Get a specific contact relationship by ID."""
    return db.query(ContactRelationship).filter(
        ContactRelationship.id == relationship_id,
        ContactRelationship.tenant_id == tenant_id
    ).first()


def get_contact_relationships(
    db: Session,
    contact_id: int,
    tenant_id: int,
    include_inactive: bool = False
) -> List[ContactRelationship]:
    """Get all relationships for a specific contact."""
    query = db.query(ContactRelationship).filter(
        ContactRelationship.tenant_id == tenant_id,
        or_(
            ContactRelationship.contact_a_id == contact_id,
            ContactRelationship.contact_b_id == contact_id
        )
    )
    
    if not include_inactive:
        query = query.filter(ContactRelationship.is_active == True)
    
    return query.all()


def get_bidirectional_relationship(
    db: Session,
    contact_a_id: int,
    contact_b_id: int,
    tenant_id: int
) -> List[ContactRelationship]:
    """Get both sides of a bidirectional relationship."""
    return db.query(ContactRelationship).filter(
        ContactRelationship.tenant_id == tenant_id,
        or_(
            and_(
                ContactRelationship.contact_a_id == contact_a_id,
                ContactRelationship.contact_b_id == contact_b_id
            ),
            and_(
                ContactRelationship.contact_a_id == contact_b_id,
                ContactRelationship.contact_b_id == contact_a_id
            )
        )
    ).all()


def create_contact_relationship(
    db: Session,
    obj_in: ContactRelationshipCreate,
    created_by_user_id: int,
    tenant_id: int
) -> ContactRelationshipPair:
    """
    Create a bidirectional contact relationship with automatic gender resolution.
    
    This function:
    1. Gets the contacts and their genders
    2. Resolves the relationship type based on gender if applicable
    3. Creates both sides of the bidirectional relationship
    4. Returns the resolved relationship pair
    """
    
    # Get the contacts to determine their genders
    contact_a = db.query(Contact).filter(
        Contact.id == obj_in.contact_a_id,
        Contact.tenant_id == tenant_id
    ).first()
    
    contact_b = db.query(Contact).filter(
        Contact.id == obj_in.contact_b_id,
        Contact.tenant_id == tenant_id
    ).first()
    
    if not contact_a or not contact_b:
        raise ValueError("One or both contacts not found")
    
    if contact_a.id == contact_b.id:
        raise ValueError("Cannot create relationship with self")
    
    # Check if relationship already exists
    existing = get_bidirectional_relationship(
        db, obj_in.contact_a_id, obj_in.contact_b_id, tenant_id
    )
    if existing:
        raise ValueError("Relationship already exists between these contacts")
    
    # Resolve the relationship based on genders (unless override is specified)
    if not obj_in.override_gender_resolution:
        mapping_result = relationship_mapping_service.determine_gender_specific_relationship(
            obj_in.relationship_type,
            contact_a.gender,
            contact_b.gender
        )
    else:
        # Manual override - validate the provided relationship
        mapping_result = relationship_mapping_service.validate_gender_relationship(
            obj_in.relationship_type,
            contact_a.gender,
            contact_b.gender
        )
    
    if not mapping_result.success:
        raise ValueError(f"Relationship mapping failed: {mapping_result.error_message}")
    
    # Create the A -> B relationship
    relationship_a_to_b = ContactRelationship(
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id,
        contact_a_id=obj_in.contact_a_id,
        contact_b_id=obj_in.contact_b_id,
        relationship_type=mapping_result.relationship_a_to_b,
        relationship_category=mapping_result.relationship_category,
        notes=obj_in.notes,
        is_gender_resolved=mapping_result.is_gender_resolved,
        original_relationship_type=mapping_result.original_relationship_type
    )
    
    # Create the B -> A relationship
    relationship_b_to_a = ContactRelationship(
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id,
        contact_a_id=obj_in.contact_b_id,
        contact_b_id=obj_in.contact_a_id,
        relationship_type=mapping_result.relationship_b_to_a,
        relationship_category=mapping_result.relationship_category,
        notes=obj_in.notes,
        is_gender_resolved=mapping_result.is_gender_resolved,
        original_relationship_type=mapping_result.original_relationship_type
    )
    
    db.add(relationship_a_to_b)
    db.add(relationship_b_to_a)
    db.commit()
    db.refresh(relationship_a_to_b)
    db.refresh(relationship_b_to_a)
    
    return ContactRelationshipPair(
        contact_a_id=obj_in.contact_a_id,
        contact_b_id=obj_in.contact_b_id,
        relationship_a_to_b=mapping_result.relationship_a_to_b,
        relationship_b_to_a=mapping_result.relationship_b_to_a,
        relationship_category=mapping_result.relationship_category,
        is_gender_resolved=mapping_result.is_gender_resolved,
        original_relationship_type=mapping_result.original_relationship_type
    )


def update_contact_relationship(
    db: Session,
    relationship_id: int,
    obj_in: ContactRelationshipUpdate,
    tenant_id: int
) -> Optional[ContactRelationship]:
    """Update a contact relationship (this updates only one side)."""
    relationship = get_contact_relationship(db, relationship_id, tenant_id)
    if not relationship:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(relationship, field, update_data[field])
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


def update_bidirectional_relationship(
    db: Session,
    contact_a_id: int,
    contact_b_id: int,
    new_relationship_type: str,
    tenant_id: int,
    notes: Optional[str] = None,
    override_gender_resolution: bool = False
) -> ContactRelationshipPair:
    """Update both sides of a bidirectional relationship."""
    
    # Get existing relationships
    existing = get_bidirectional_relationship(db, contact_a_id, contact_b_id, tenant_id)
    if not existing:
        raise ValueError("Relationship not found")
    
    # Get contacts for gender resolution
    contact_a = db.query(Contact).filter(
        Contact.id == contact_a_id,
        Contact.tenant_id == tenant_id
    ).first()
    
    contact_b = db.query(Contact).filter(
        Contact.id == contact_b_id,
        Contact.tenant_id == tenant_id
    ).first()
    
    if not contact_a or not contact_b:
        raise ValueError("One or both contacts not found")
    
    # Resolve the new relationship
    if not override_gender_resolution:
        mapping_result = relationship_mapping_service.determine_gender_specific_relationship(
            new_relationship_type,
            contact_a.gender,
            contact_b.gender
        )
    else:
        mapping_result = relationship_mapping_service.validate_gender_relationship(
            new_relationship_type,
            contact_a.gender,
            contact_b.gender
        )
    
    if not mapping_result.success:
        raise ValueError(f"Relationship mapping failed: {mapping_result.error_message}")
    
    # Update both relationships
    for rel in existing:
        if rel.contact_a_id == contact_a_id and rel.contact_b_id == contact_b_id:
            # A -> B relationship
            rel.relationship_type = mapping_result.relationship_a_to_b
        elif rel.contact_a_id == contact_b_id and rel.contact_b_id == contact_a_id:
            # B -> A relationship
            rel.relationship_type = mapping_result.relationship_b_to_a
        
        # Update common fields
        rel.relationship_category = mapping_result.relationship_category
        rel.is_gender_resolved = mapping_result.is_gender_resolved
        rel.original_relationship_type = mapping_result.original_relationship_type
        if notes is not None:
            rel.notes = notes
        
        db.add(rel)
    
    db.commit()
    
    return ContactRelationshipPair(
        contact_a_id=contact_a_id,
        contact_b_id=contact_b_id,
        relationship_a_to_b=mapping_result.relationship_a_to_b,
        relationship_b_to_a=mapping_result.relationship_b_to_a,
        relationship_category=mapping_result.relationship_category,
        is_gender_resolved=mapping_result.is_gender_resolved,
        original_relationship_type=mapping_result.original_relationship_type
    )


def delete_contact_relationship(
    db: Session,
    contact_a_id: int,
    contact_b_id: int,
    tenant_id: int
) -> bool:
    """Delete a bidirectional relationship (both sides)."""
    existing = get_bidirectional_relationship(db, contact_a_id, contact_b_id, tenant_id)
    
    if not existing:
        return False
    
    for rel in existing:
        db.delete(rel)
    
    db.commit()
    return True


def get_relationship_summary(
    db: Session,
    contact_id: int,
    tenant_id: int
) -> Dict[str, List[Dict[str, Any]]]:
    """Get a summary of relationships grouped by category."""
    relationships = get_contact_relationships(db, contact_id, tenant_id)
    
    summary = {}
    
    for rel in relationships:
        category = rel.relationship_category
        if category not in summary:
            summary[category] = []
        
        # Determine the other contact
        other_contact_id = rel.contact_b_id if rel.contact_a_id == contact_id else rel.contact_a_id
        other_contact = db.query(Contact).filter(Contact.id == other_contact_id).first()
        
        summary[category].append({
            'relationship_id': rel.id,
            'relationship_type': rel.relationship_type,
            'other_contact_id': other_contact_id,
            'other_contact_name': f"{other_contact.first_name} {other_contact.last_name or ''}".strip() if other_contact else "Unknown",
            'is_gender_resolved': rel.is_gender_resolved,
            'original_relationship_type': rel.original_relationship_type,
            'notes': rel.notes,
            'created_at': rel.created_at
        })
    
    return summary
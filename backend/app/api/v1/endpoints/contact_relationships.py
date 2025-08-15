"""
API endpoints for contact relationship management.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.contact_relationship import (
    ContactRelationshipCreate,
    ContactRelationshipUpdate,
    ContactRelationship,
    ContactRelationshipPair,
    RelationshipTypeOption
)
from app.crud import contact_relationship as crud_relationship
from app.services.relationship_mapping import relationship_mapping_service

router = APIRouter()


@router.get("/options", response_model=List[RelationshipTypeOption])
def get_relationship_options(
    include_base_types: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available relationship type options for UI selection.
    
    Args:
        include_base_types: Include base types like 'sibling' instead of specific types
    """
    return relationship_mapping_service.get_relationship_options(
        include_gender_specific_base=include_base_types
    )


@router.get("/categories")
def get_relationship_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available relationship categories."""
    return relationship_mapping_service.get_categories()


@router.post("/", response_model=ContactRelationshipPair)
def create_relationship(
    request: Request,
    relationship_in: ContactRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new bidirectional contact relationship.
    
    This endpoint automatically resolves gender-specific relationships based on
    the contacts' genders unless override_gender_resolution is True.
    """
    tenant_id = request.state.tenant.id
    
    try:
        return crud_relationship.create_contact_relationship(
            db=db,
            obj_in=relationship_in,
            created_by_user_id=current_user.id,
            tenant_id=tenant_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contact/{contact_id}", response_model=List[ContactRelationship])
def get_contact_relationships(
    contact_id: int,
    request: Request,
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all relationships for a specific contact."""
    tenant_id = request.state.tenant.id
    
    return crud_relationship.get_contact_relationships(
        db=db,
        contact_id=contact_id,
        tenant_id=tenant_id,
        include_inactive=include_inactive
    )


@router.get("/contact/{contact_id}/summary")
def get_contact_relationship_summary(
    contact_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of relationships for a contact, grouped by category."""
    tenant_id = request.state.tenant.id
    
    return crud_relationship.get_relationship_summary(
        db=db,
        contact_id=contact_id,
        tenant_id=tenant_id
    )


@router.put("/{contact_a_id}/{contact_b_id}", response_model=ContactRelationshipPair)
def update_bidirectional_relationship(
    contact_a_id: int,
    contact_b_id: int,
    request: Request,
    new_relationship_type: str,
    notes: str = None,
    override_gender_resolution: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bidirectional relationship between two contacts."""
    tenant_id = request.state.tenant.id
    
    try:
        return crud_relationship.update_bidirectional_relationship(
            db=db,
            contact_a_id=contact_a_id,
            contact_b_id=contact_b_id,
            new_relationship_type=new_relationship_type,
            tenant_id=tenant_id,
            notes=notes,
            override_gender_resolution=override_gender_resolution
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{contact_a_id}/{contact_b_id}")
def delete_relationship(
    contact_a_id: int,
    contact_b_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bidirectional relationship between two contacts."""
    tenant_id = request.state.tenant.id
    
    success = crud_relationship.delete_contact_relationship(
        db=db,
        contact_a_id=contact_a_id,
        contact_b_id=contact_b_id,
        tenant_id=tenant_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return {"message": "Relationship deleted successfully"}


@router.get("/{relationship_id}", response_model=ContactRelationship)
def get_relationship(
    relationship_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific relationship by ID."""
    tenant_id = request.state.tenant.id
    
    relationship = crud_relationship.get_contact_relationship(
        db=db,
        relationship_id=relationship_id,
        tenant_id=tenant_id
    )
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return relationship


@router.put("/{relationship_id}", response_model=ContactRelationship)
def update_relationship(
    relationship_id: int,
    request: Request,
    relationship_update: ContactRelationshipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific relationship (single side only)."""
    tenant_id = request.state.tenant.id
    
    relationship = crud_relationship.update_contact_relationship(
        db=db,
        relationship_id=relationship_id,
        obj_in=relationship_update,
        tenant_id=tenant_id
    )
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return relationship
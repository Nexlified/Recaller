from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ContactRelationshipBase(BaseModel):
    contact_a_id: int
    contact_b_id: int
    relationship_type: str
    relationship_category: str
    notes: Optional[str] = None
    is_active: Optional[bool] = True


class ContactRelationshipCreate(BaseModel):
    """
    Schema for creating a relationship. Supports both specific and base relationship types.
    If a base type is provided (e.g., 'sibling'), the service will resolve it to specific types.
    """
    contact_a_id: int
    contact_b_id: int
    relationship_type: str  # Can be base type ('sibling') or specific type ('brother')
    notes: Optional[str] = None
    override_gender_resolution: Optional[bool] = False  # Allow manual override of auto-resolution


class ContactRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ContactRelationshipInDBBase(ContactRelationshipBase):
    id: int
    tenant_id: int
    created_by_user_id: int
    is_gender_resolved: bool
    original_relationship_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContactRelationship(ContactRelationshipInDBBase):
    pass


class ContactRelationshipInDB(ContactRelationshipInDBBase):
    pass


class ContactRelationshipPair(BaseModel):
    """
    Represents a bidirectional relationship pair with resolved gender-specific types.
    """
    contact_a_id: int
    contact_b_id: int
    relationship_a_to_b: str
    relationship_b_to_a: str
    relationship_category: str
    is_gender_resolved: bool
    original_relationship_type: Optional[str] = None


class RelationshipMappingResult(BaseModel):
    """
    Result of relationship mapping including validation and resolution details.
    """
    success: bool
    relationship_a_to_b: str
    relationship_b_to_a: str
    relationship_category: str
    is_gender_resolved: bool
    original_relationship_type: Optional[str] = None
    validation_warnings: Optional[list[str]] = None
    error_message: Optional[str] = None


class RelationshipTypeOption(BaseModel):
    """
    Available relationship type option for UI selection.
    """
    key: str
    display_name: str
    category: str
    is_gender_specific: bool
    description: Optional[str] = None
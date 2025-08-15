from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class RelationshipStatus(str, Enum):
    """Status of the relationship between contacts."""
    ACTIVE = "active"
    DISTANT = "distant"
    ENDED = "ended"


class ContactRelationshipBase(BaseModel):
    contact_a_id: int
    contact_b_id: int
    relationship_type: str
    relationship_category: str
    relationship_strength: Optional[int] = Field(None, ge=1, le=10, description="Relationship strength from 1-10")
    relationship_status: Optional[RelationshipStatus] = RelationshipStatus.ACTIVE
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_mutual: Optional[bool] = True
    notes: Optional[str] = None
    context: Optional[str] = None
    is_active: Optional[bool] = True


class ContactRelationshipCreate(BaseModel):
    """
    Schema for creating a relationship. Supports both specific and base relationship types.
    If a base type is provided (e.g., 'sibling'), the service will resolve it to specific types.
    """
    contact_a_id: int
    contact_b_id: int
    relationship_type: str  # Can be base type ('sibling') or specific type ('brother')
    relationship_strength: Optional[int] = Field(None, ge=1, le=10, description="Relationship strength from 1-10")
    relationship_status: Optional[RelationshipStatus] = RelationshipStatus.ACTIVE
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_mutual: Optional[bool] = True
    notes: Optional[str] = None
    context: Optional[str] = None
    override_gender_resolution: Optional[bool] = False  # Allow manual override of auto-resolution


class ContactRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    relationship_strength: Optional[int] = Field(None, ge=1, le=10, description="Relationship strength from 1-10")
    relationship_status: Optional[RelationshipStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_mutual: Optional[bool] = None
    notes: Optional[str] = None
    context: Optional[str] = None
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


class RelationshipTypeOption(BaseModel):
    """
    Available relationship type option for UI selection.
    """
    key: str
    display_name: str
    category: str
    is_gender_specific: bool
    description: Optional[str] = None
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class RelationshipType(enum.Enum):
    # Family relationships
    PARENT = "parent"
    CHILD = "child" 
    SIBLING = "sibling"
    SPOUSE = "spouse"
    PARTNER = "partner"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    AUNT_UNCLE = "aunt_uncle"
    NEPHEW_NIECE = "nephew_niece"
    COUSIN = "cousin"
    
    # Professional relationships
    COLLEAGUE = "colleague"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CLIENT = "client"
    VENDOR = "vendor"
    MENTOR = "mentor"
    MENTEE = "mentee"
    
    # Social relationships
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"
    NEIGHBOR = "neighbor"
    ROOMMATE = "roommate"
    
    # Other
    OTHER = "other"


class RelationshipStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ESTRANGED = "estranged"
    DECEASED = "deceased"


class PersonRelationship(Base):
    """Rich bidirectional relationship mapping between persons"""
    __tablename__ = "person_relationships"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # The two persons in the relationship
    person_a_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    person_b_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Relationship from A's perspective to B
    relationship_a_to_b = Column(String(50), nullable=False)
    relationship_b_to_a = Column(String(50), nullable=False)
    
    # Additional relationship details
    relationship_status = Column(String(20), nullable=False, default=RelationshipStatus.ACTIVE.value)
    closeness_level = Column(Integer, default=3)  # 1-5 scale (1=distant, 5=very close)
    interaction_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, yearly, rarely
    
    # Context and notes
    how_they_met = Column(Text, nullable=True)
    relationship_context = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Important dates
    relationship_start_date = Column(DateTime(timezone=True), nullable=True)
    relationship_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Gender-specific relationship resolution
    auto_resolved = Column(Boolean, default=False)  # Whether this was auto-resolved from gender mapping
    manual_override = Column(Boolean, default=False)  # Whether user manually overrode auto-resolution
    original_relationship_type = Column(String(50), nullable=True)  # Original type before gender resolution
    
    # Tags for categorization
    tags = Column(JSON, default=list)
    
    # Privacy and visibility
    privacy_level = Column(String(10), nullable=False, default="private")
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    created_by = relationship("User")
    person_a = relationship("PersonProfile", foreign_keys=[person_a_id], back_populates="relationships_as_a")
    person_b = relationship("PersonProfile", foreign_keys=[person_b_id], back_populates="relationships_as_b")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_person_relationships_persons', 'person_a_id', 'person_b_id'),
        Index('idx_person_relationships_tenant', 'tenant_id', 'is_active'),
        Index('idx_person_relationships_a_type', 'person_a_id', 'relationship_a_to_b'),
        Index('idx_person_relationships_b_type', 'person_b_id', 'relationship_b_to_a'),
        # Ensure no duplicate relationships (A->B should not duplicate B->A)
        Index('idx_person_relationships_unique', 'person_a_id', 'person_b_id', unique=True),
    )

    def get_relationship_to(self, person_id: int) -> str:
        """Get the relationship type from this record's perspective to the given person"""
        if self.person_a_id == person_id:
            return self.relationship_b_to_a
        elif self.person_b_id == person_id:
            return self.relationship_a_to_b
        return None

    def get_other_person_id(self, person_id: int) -> int:
        """Get the other person's ID in this relationship"""
        if self.person_a_id == person_id:
            return self.person_b_id
        elif self.person_b_id == person_id:
            return self.person_a_id
        return None

    @property
    def bidirectional_summary(self) -> str:
        """Get a summary of the bidirectional relationship"""
        return f"{self.relationship_a_to_b} ↔ {self.relationship_b_to_a}"


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ContactRelationship(Base):
    """
    Stores bidirectional relationships between contacts.
    Each relationship is stored as two rows (A -> B and B -> A) for efficient querying.
    """
    __tablename__ = "contact_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship participants
    contact_a_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    contact_b_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    
    # Relationship details
    relationship_type = Column(String(50), nullable=False)  # e.g., 'brother', 'sister', 'friend'
    relationship_category = Column(String(20), nullable=False)  # e.g., 'family', 'professional', 'social'
    
    # Metadata
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Gender resolution metadata (for auditing/debugging)
    is_gender_resolved = Column(Boolean, default=False)  # True if automatically resolved from base type
    original_relationship_type = Column(String(50))  # Original base type if gender-resolved (e.g., 'sibling')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ensure unique bidirectional relationships per tenant
    __table_args__ = (
        UniqueConstraint('tenant_id', 'contact_a_id', 'contact_b_id', name='uq_tenant_contact_relationship'),
    )
    
    # Relationships
    tenant = relationship("Tenant")
    created_by = relationship("User")
    contact_a = relationship("Contact", foreign_keys=[contact_a_id])
    contact_b = relationship("Contact", foreign_keys=[contact_b_id])


# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.contact import Contact
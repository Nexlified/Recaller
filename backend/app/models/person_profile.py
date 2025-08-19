"""
Person Profile models for Relationship Management system.
Replaces the monolithic Contact model with normalized tables.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class PersonProfileVisibility(enum.Enum):
    """Visibility settings for person profile information."""
    PRIVATE = "private"
    TENANT_SHARED = "tenant_shared"  # Shared with other users in same tenant


class PersonProfile(Base):
    """
    Core person profile - minimal information needed to create a profile.
    This replaces the Contact model with a normalized approach.
    """
    __tablename__ = "person_profiles"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Core Information - only what's needed to create a profile
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)  # How user prefers to see this person
    
    # Basic metadata
    notes = Column(Text)  # General notes about this person
    gender = Column(String(20), nullable=True)  # For relationship mapping
    
    # Profile status
    is_active = Column(Boolean, default=True)
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="person_profiles")
    created_by = relationship("User", back_populates="person_profiles")
    
    # Related information tables
    contact_info = relationship("PersonContactInfo", back_populates="person", cascade="all, delete-orphan")
    professional_info = relationship("PersonProfessionalInfo", back_populates="person", cascade="all, delete-orphan")
    personal_info = relationship("PersonPersonalInfo", back_populates="person", cascade="all, delete-orphan")
    life_events = relationship("PersonLifeEvent", back_populates="person", cascade="all, delete-orphan")
    belongings = relationship("PersonBelonging", back_populates="person", cascade="all, delete-orphan")
    
    # Relationship connections
    relationships_as_a = relationship("PersonRelationship", foreign_keys="PersonRelationship.person_a_id", back_populates="person_a")
    relationships_as_b = relationship("PersonRelationship", foreign_keys="PersonRelationship.person_b_id", back_populates="person_b")
    
    @property
    def full_name(self):
        """Get the full name of the person."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def current_contact_info(self):
        """Get the current/primary contact information."""
        return next((info for info in self.contact_info if info.is_primary), None)
    
    @property
    def current_professional_info(self):
        """Get the current professional information."""
        return next((info for info in self.professional_info if info.is_current), None)


class PersonContactInfo(Base):
    """Contact information for a person (email, phone, addresses)."""
    __tablename__ = "person_contact_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Contact details
    email = Column(String(255), index=True)
    phone = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Metadata
    contact_type = Column(String(20), nullable=False, default="personal")  # personal, work, other
    is_primary = Column(Boolean, default=False)
    is_emergency_contact = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Privacy settings
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="contact_info")
    tenant = relationship("Tenant")


class PersonProfessionalInfo(Base):
    """Professional information for a person."""
    __tablename__ = "person_professional_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Professional details
    job_title = Column(String(255))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization_name = Column(String(255))  # In case organization is not in our system
    department = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)  # NULL if current position
    
    # Additional info
    salary_range = Column(String(50))  # Optional salary information
    work_location = Column(String(255))
    employment_type = Column(String(50))  # full-time, part-time, contract, etc.
    notes = Column(Text)
    
    # Status
    is_current = Column(Boolean, default=True)
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="professional_info")
    organization = relationship("Organization")
    tenant = relationship("Tenant")


class PersonPersonalInfo(Base):
    """Personal/family information for a person."""
    __tablename__ = "person_personal_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Personal dates
    date_of_birth = Column(Date)
    anniversary_date = Column(Date)  # Wedding or relationship anniversary
    
    # Family information
    maiden_name = Column(String(255))
    family_nickname = Column(String(100))  # e.g., "Grandma", "Uncle Bob"
    preferred_name = Column(String(255))  # What they like to be called
    
    # Personal preferences
    favorite_color = Column(String(50))
    favorite_food = Column(String(255))
    dietary_restrictions = Column(Text)
    allergies = Column(Text)
    
    # Additional personal details
    personality_notes = Column(Text)
    interests_hobbies = Column(Text)
    notes = Column(Text)
    
    # Privacy settings
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="personal_info")
    tenant = relationship("Tenant")


class PersonLifeEvent(Base):
    """Life events and milestones for a person."""
    __tablename__ = "person_life_events"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # birthday, wedding, graduation, job_change, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    location = Column(String(255))
    
    # Relationship to this event
    my_role = Column(String(100))  # How the user was involved: attended, organized, heard_about
    significance = Column(Integer)  # 1-10 scale of importance
    
    # Metadata
    is_recurring = Column(Boolean, default=False)  # For birthdays, anniversaries
    notes = Column(Text)
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="life_events")
    tenant = relationship("Tenant")


class PersonBelonging(Base):
    """Belongings associated with a person (things they own, like, etc.)."""
    __tablename__ = "person_belongings"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Belonging details
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # electronics, books, clothing, vehicles, etc.
    description = Column(Text)
    brand = Column(String(100))
    model = Column(String(100))
    
    # Value and acquisition
    estimated_value = Column(String(50))  # Keep as string for flexibility
    acquisition_date = Column(Date)
    acquisition_method = Column(String(50))  # purchased, gift, inherited, etc.
    
    # Relationship context
    relationship_context = Column(Text)  # Why this is relevant to know about them
    notes = Column(Text)
    
    # Privacy and status
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    is_active = Column(Boolean, default=True)  # Still owned/relevant
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="belongings")
    tenant = relationship("Tenant")


class PersonRelationship(Base):
    """
    Relationships between person profiles.
    Extends the existing ContactRelationship concept.
    """
    __tablename__ = "person_relationships"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship participants
    person_a_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    person_b_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Relationship details
    relationship_type = Column(String(50), nullable=False)  # brother, sister, friend, colleague, etc.
    relationship_category = Column(String(20), nullable=False)  # family, professional, social, romantic
    relationship_strength = Column(Integer)  # 1-10 scale
    
    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Context and notes
    how_we_met = Column(Text)
    context = Column(Text)
    notes = Column(Text)
    
    # Status
    is_mutual = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Privacy
    visibility = Column(String(20), nullable=False, default=PersonProfileVisibility.PRIVATE.value)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person_a = relationship("PersonProfile", foreign_keys=[person_a_id], back_populates="relationships_as_a")
    person_b = relationship("PersonProfile", foreign_keys=[person_b_id], back_populates="relationships_as_b")
    tenant = relationship("Tenant")
    created_by = relationship("User")


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.organization import Organization
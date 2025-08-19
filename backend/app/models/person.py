from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Numeric, Enum, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class PersonVisibility(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class ContactInfoType(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SOCIAL_MEDIA = "social_media"
    WEBSITE = "website"


class ContactInfoPrivacy(enum.Enum):
    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"


class LifeEventType(enum.Enum):
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    GRADUATION = "graduation"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    BIRTH_OF_CHILD = "birth_of_child"
    DEATH = "death"
    PROMOTION = "promotion"
    JOB_CHANGE = "job_change"
    RELOCATION = "relocation"
    RETIREMENT = "retirement"
    OTHER = "other"


class BelongingType(enum.Enum):
    GIFT_RECEIVED = "gift_received"
    GIFT_GIVEN = "gift_given"
    ITEM_BORROWED = "item_borrowed"
    ITEM_LENT = "item_lent"
    POSSESSION = "possession"
    RECOMMENDATION = "recommendation"
    OTHER = "other"


class PersonProfile(Base):
    """Core profile information for a person"""
    __tablename__ = "person_profiles"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic Information
    first_name = Column(String(255), nullable=False, index=True)
    last_name = Column(String(255), nullable=True, index=True)
    gender = Column(String(20), nullable=True)  # 'male', 'female', 'non_binary', 'prefer_not_to_say'
    
    # General notes about the person
    notes = Column(Text)
    
    # Visibility and status
    visibility = Column(String(10), nullable=False, default=PersonVisibility.PRIVATE.value, index=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="person_profiles")
    created_by = relationship("User", back_populates="person_profiles")
    contact_info = relationship("PersonContactInfo", back_populates="person", cascade="all, delete-orphan")
    professional_info = relationship("PersonProfessionalInfo", back_populates="person", cascade="all, delete-orphan")
    personal_info = relationship("PersonPersonalInfo", back_populates="person", cascade="all, delete-orphan")
    life_events = relationship("PersonLifeEvent", back_populates="person", cascade="all, delete-orphan")
    belongings = relationship("PersonBelonging", back_populates="person", cascade="all, delete-orphan")
    relationships_as_a = relationship("PersonRelationship", foreign_keys="PersonRelationship.person_a_id", back_populates="person_a")
    relationships_as_b = relationship("PersonRelationship", foreign_keys="PersonRelationship.person_b_id", back_populates="person_b")
    
    # Legacy relationships that need to be migrated to use person_id
    # These will be updated in the migration
    interactions = relationship("ContactInteraction", foreign_keys="ContactInteraction.contact_id", cascade="all, delete-orphan")
    task_contacts = relationship("TaskContact", foreign_keys="TaskContact.contact_id", cascade="all, delete-orphan")
    work_experiences = relationship("ContactWorkExperience", foreign_keys="ContactWorkExperience.contact_id", cascade="all, delete-orphan")
    personal_reminders = relationship("PersonalReminder", foreign_keys="PersonalReminder.contact_id", cascade="all, delete-orphan")
    gifts_received = relationship("Gift", foreign_keys="Gift.recipient_contact_id", cascade="all, delete-orphan")
    gift_ideas_for_them = relationship("GiftIdea", foreign_keys="GiftIdea.target_contact_id", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_person_profiles_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_person_profiles_name', 'first_name', 'last_name'),
    )


class PersonContactInfo(Base):
    """Email, phone, addresses with individual privacy settings"""
    __tablename__ = "person_contact_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Contact information type and value
    contact_type = Column(String(20), nullable=False)  # email, phone, address, social_media, website
    contact_value = Column(String(500), nullable=False)
    contact_label = Column(String(100), nullable=True)  # 'home', 'work', 'mobile', 'personal', etc.
    
    # Privacy settings for this specific contact method
    privacy_level = Column(String(10), nullable=False, default=ContactInfoPrivacy.PRIVATE.value)
    
    # Additional details for addresses
    address_street = Column(String(255), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_state = Column(String(100), nullable=True)
    address_postal_code = Column(String(20), nullable=True)
    address_country_code = Column(String(2), nullable=True)
    
    # Status and ordering
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="contact_info")
    
    # Indexes
    __table_args__ = (
        Index('idx_person_contact_info_person_type', 'person_id', 'contact_type'),
        Index('idx_person_contact_info_primary', 'person_id', 'is_primary', 'contact_type'),
    )


class PersonProfessionalInfo(Base):
    """Job history, organizations, work details"""
    __tablename__ = "person_professional_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Current/primary job information
    job_title = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    is_current_position = Column(Boolean, default=False)
    
    # Work dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Work contact information
    work_email = Column(String(255), nullable=True)
    work_phone = Column(String(50), nullable=True)
    work_address = Column(Text, nullable=True)
    
    # Professional details
    job_description = Column(Text, nullable=True)
    responsibilities = Column(JSON, default=list)  # List of responsibilities
    skills_used = Column(JSON, default=list)  # List of skills
    achievements = Column(JSON, default=list)  # List of achievements
    
    # Manager and reporting
    manager_person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=True)
    reporting_structure = Column(Text, nullable=True)
    
    # References
    can_be_reference = Column(Boolean, default=False)
    reference_notes = Column(Text, nullable=True)
    
    # LinkedIn and professional profiles
    linkedin_profile = Column(String(500), nullable=True)
    other_profiles = Column(JSON, default=dict)  # Other professional profiles
    
    # Salary information (optional)
    salary_range = Column(String(100), nullable=True)
    currency = Column(String(3), default='USD')
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="professional_info")
    organization = relationship("Organization", back_populates="person_professional_info")
    manager = relationship("PersonProfile", foreign_keys=[manager_person_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_person_professional_person_current', 'person_id', 'is_current_position'),
        Index('idx_person_professional_org', 'organization_id'),
    )


class PersonPersonalInfo(Base):
    """Birthday, preferences, family information"""
    __tablename__ = "person_personal_info"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Personal dates and information
    date_of_birth = Column(Date, nullable=True)
    anniversary_date = Column(Date, nullable=True)  # Wedding anniversary or other important date
    maiden_name = Column(String(255), nullable=True)  # Maiden name for genealogy
    family_nickname = Column(String(100), nullable=True)  # "Grandma", "Uncle Bob", etc.
    
    # Emergency contact designation
    is_emergency_contact = Column(Boolean, default=False, index=True)
    emergency_contact_priority = Column(Integer, default=0)  # 1=primary, 2=secondary, etc.
    
    # Personal preferences
    preferred_communication = Column(JSON, default=list)  # ['email', 'phone', 'text']
    communication_notes = Column(Text, nullable=True)
    
    # Family and relationship context
    marital_status = Column(String(20), nullable=True)  # single, married, divorced, widowed, etc.
    spouse_partner_person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=True)
    children_count = Column(Integer, default=0)
    
    # Cultural and personal details
    cultural_background = Column(String(100), nullable=True)
    languages_spoken = Column(JSON, default=list)
    religion = Column(String(100), nullable=True)
    dietary_restrictions = Column(JSON, default=list)
    
    # Interests and hobbies
    hobbies_interests = Column(JSON, default=list)
    favorite_activities = Column(JSON, default=list)
    
    # Privacy and preferences
    privacy_level = Column(String(10), nullable=False, default=ContactInfoPrivacy.PRIVATE.value)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="personal_info")
    spouse_partner = relationship("PersonProfile", foreign_keys=[spouse_partner_person_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_person_personal_person', 'person_id'),
        Index('idx_person_personal_emergency', 'is_emergency_contact', 'emergency_contact_priority'),
        Index('idx_person_personal_birth_month', 'date_of_birth'),
    )


class PersonLifeEvent(Base):
    """Important dates, milestones, life tracking"""
    __tablename__ = "person_life_events"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(30), nullable=False)  # birthday, anniversary, graduation, etc.
    event_date = Column(Date, nullable=False)
    event_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Event importance and tracking
    importance_level = Column(Integer, default=3)  # 1-5 scale
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String(20), nullable=True)  # yearly, monthly, etc.
    
    # Reminder settings
    should_remind = Column(Boolean, default=True)
    reminder_days_before = Column(Integer, default=7)
    
    # Location and participants
    location = Column(String(255), nullable=True)
    participants = Column(JSON, default=list)  # List of person IDs or names
    
    # Related entities
    related_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    tags = Column(JSON, default=list)  # Tags for categorization
    
    # Privacy
    privacy_level = Column(String(10), nullable=False, default=ContactInfoPrivacy.PRIVATE.value)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="life_events")
    related_organization = relationship("Organization")
    
    # Indexes
    __table_args__ = (
        Index('idx_person_life_events_person_date', 'person_id', 'event_date'),
        Index('idx_person_life_events_type_date', 'event_type', 'event_date'),
        Index('idx_person_life_events_remind', 'should_remind', 'event_date'),
    )


class PersonBelonging(Base):
    """Items, possessions, relationship context"""
    __tablename__ = "person_belongings"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=False, index=True)
    
    # Belonging details
    belonging_type = Column(String(20), nullable=False)  # gift_received, gift_given, etc.
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Value and importance
    estimated_value = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default='USD')
    sentimental_value = Column(Integer, default=3)  # 1-5 scale
    
    # Dates and occasions
    date_acquired = Column(Date, nullable=True)
    occasion = Column(String(255), nullable=True)  # Birthday, Christmas, etc.
    
    # Relationship context
    related_person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=True)
    relationship_context = Column(Text, nullable=True)
    
    # Item details
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    condition = Column(String(20), nullable=True)  # new, excellent, good, fair, poor
    
    # Location and status
    current_location = Column(String(255), nullable=True)
    is_borrowed = Column(Boolean, default=False)
    borrowed_to_person_id = Column(Integer, ForeignKey("person_profiles.id"), nullable=True)
    borrowed_date = Column(Date, nullable=True)
    expected_return_date = Column(Date, nullable=True)
    
    # Photos and documentation
    photos = Column(JSON, default=list)  # List of photo URLs
    receipts = Column(JSON, default=list)  # List of receipt URLs
    documents = Column(JSON, default=list)  # List of document URLs
    
    # Categories and tags
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    
    # Privacy
    privacy_level = Column(String(10), nullable=False, default=ContactInfoPrivacy.PRIVATE.value)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    person = relationship("PersonProfile", back_populates="belongings")
    related_person = relationship("PersonProfile", foreign_keys=[related_person_id])
    borrowed_to_person = relationship("PersonProfile", foreign_keys=[borrowed_to_person_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_person_belongings_person_type', 'person_id', 'belonging_type'),
        Index('idx_person_belongings_borrowed', 'is_borrowed', 'borrowed_date'),
        Index('idx_person_belongings_category', 'category', 'subcategory'),
    )


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.organization import Organization
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class EmploymentType(enum.Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    VOLUNTEER = "volunteer"

class WorkLocation(enum.Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"
    TRAVEL = "travel"

class WorkExperienceVisibility(enum.Enum):
    PRIVATE = "private"
    TEAM = "team"  
    PUBLIC = "public"

class ContactWorkExperience(Base):
    __tablename__ = "contact_work_experience"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Company Information
    company_name = Column(String(255), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Position Details
    job_title = Column(String(255), nullable=False, index=True)
    department = Column(String(255))
    employment_type = Column(String(50))  # EmploymentType enum values
    work_location = Column(String(255))
    
    # Duration
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False, index=True)
    
    # Contact Information
    work_phone = Column(String(50))
    work_email = Column(String(255))
    work_address = Column(Text)
    
    # Professional Details
    job_description = Column(Text)
    key_achievements = Column(ARRAY(Text))
    skills_used = Column(ARRAY(Text))
    
    # Compensation
    salary_range = Column(String(100))
    currency = Column(String(3), default='USD')
    
    # Professional Networks
    linkedin_profile = Column(String(500))
    other_profiles = Column(JSONB)
    
    # Relationships
    manager_contact_id = Column(Integer, ForeignKey("contacts.id"))
    reporting_structure = Column(Text)
    
    # Reference Information
    can_be_reference = Column(Boolean, default=False)
    reference_notes = Column(Text)
    
    # Metadata
    visibility = Column(String(20), default=WorkExperienceVisibility.PRIVATE.value, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", foreign_keys=[contact_id], back_populates="work_experiences")
    company = relationship("Organization", foreign_keys=[company_id])
    manager = relationship("Contact", foreign_keys=[manager_contact_id])
    tenant = relationship("Tenant")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date >= start_date', name='check_end_date_after_start'),
        CheckConstraint('NOT (is_current = true AND end_date IS NOT NULL)', name='check_current_position'),
    )

# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.contact import Contact
from app.models.organization import Organization
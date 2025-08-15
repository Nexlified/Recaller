from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    VOLUNTEER = "volunteer"


class WorkLocation(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"
    TRAVEL = "travel"


class WorkExperienceVisibility(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class ContactWorkExperienceBase(BaseModel):
    company_name: str
    company_id: Optional[int] = None
    job_title: str
    department: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    work_phone: Optional[str] = None
    work_email: Optional[EmailStr] = None
    work_address: Optional[str] = None
    job_description: Optional[str] = None
    key_achievements: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None
    salary_range: Optional[str] = None
    currency: str = "USD"
    linkedin_profile: Optional[str] = None
    other_profiles: Optional[Dict[str, Any]] = None
    manager_contact_id: Optional[int] = None
    reporting_structure: Optional[str] = None
    can_be_reference: bool = False
    reference_notes: Optional[str] = None
    visibility: WorkExperienceVisibility = WorkExperienceVisibility.PRIVATE


class ContactWorkExperienceCreate(ContactWorkExperienceBase):
    pass


class ContactWorkExperienceUpdate(BaseModel):
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    work_phone: Optional[str] = None
    work_email: Optional[EmailStr] = None
    work_address: Optional[str] = None
    job_description: Optional[str] = None
    key_achievements: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None
    salary_range: Optional[str] = None
    currency: Optional[str] = None
    linkedin_profile: Optional[str] = None
    other_profiles: Optional[Dict[str, Any]] = None
    manager_contact_id: Optional[int] = None
    reporting_structure: Optional[str] = None
    can_be_reference: Optional[bool] = None
    reference_notes: Optional[str] = None
    visibility: Optional[WorkExperienceVisibility] = None


class ContactWorkExperienceInDBBase(ContactWorkExperienceBase):
    id: int
    contact_id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContactWorkExperience(ContactWorkExperienceInDBBase):
    pass


class ContactWorkExperienceInDB(ContactWorkExperienceInDBBase):
    pass


# Professional network response schemas
class ProfessionalConnection(BaseModel):
    contact_id: int
    contact_name: str
    connection_type: str  # "current_colleague", "former_colleague", "manager", "report"
    company_name: str
    shared_companies: List[str]
    mutual_connections: int


class CompanyNetwork(BaseModel):
    company_name: str
    current_employees: List[ContactWorkExperience]
    former_employees: List[ContactWorkExperience]
    total_connections: int


class CareerTimeline(BaseModel):
    contact_id: int
    work_experiences: List[ContactWorkExperience]
    career_progression: List[str]
    total_experience_years: float
    skills_evolution: Dict[str, List[str]]  # skill -> companies where used
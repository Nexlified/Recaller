from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import date

from app.models.contact_work_experience import ContactWorkExperience, WorkExperienceVisibility
from app.schemas.contact_work_experience import ContactWorkExperienceCreate, ContactWorkExperienceUpdate


def get_work_experience(db: Session, work_experience_id: int, tenant_id: int) -> Optional[ContactWorkExperience]:
    """Get work experience by ID within tenant"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.id == work_experience_id,
        ContactWorkExperience.tenant_id == tenant_id
    ).first()


def get_contact_work_experiences(
    db: Session, 
    contact_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ContactWorkExperience]:
    """Get all work experiences for a contact ordered by start date (most recent first)"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.contact_id == contact_id,
        ContactWorkExperience.tenant_id == tenant_id
    ).order_by(desc(ContactWorkExperience.start_date)).offset(skip).limit(limit).all()


def get_current_work_experience(db: Session, contact_id: int, tenant_id: int) -> Optional[ContactWorkExperience]:
    """Get current work experience for a contact"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.contact_id == contact_id,
        ContactWorkExperience.tenant_id == tenant_id,
        ContactWorkExperience.is_current == True
    ).first()


def get_work_experiences_by_company(
    db: Session,
    company_name: str,
    tenant_id: int,
    current_only: bool = False,
    skip: int = 0,
    limit: int = 100
) -> List[ContactWorkExperience]:
    """Get all work experiences at a specific company"""
    query = db.query(ContactWorkExperience).filter(
        ContactWorkExperience.company_name.ilike(f"%{company_name}%"),
        ContactWorkExperience.tenant_id == tenant_id
    )
    
    if current_only:
        query = query.filter(ContactWorkExperience.is_current == True)
    
    return query.order_by(desc(ContactWorkExperience.start_date)).offset(skip).limit(limit).all()


def get_contacts_by_company(
    db: Session,
    company_name: str,
    tenant_id: int,
    current_only: bool = False
) -> List[int]:
    """Get contact IDs who worked/work at a specific company"""
    query = db.query(ContactWorkExperience.contact_id).filter(
        ContactWorkExperience.company_name.ilike(f"%{company_name}%"),
        ContactWorkExperience.tenant_id == tenant_id
    )
    
    if current_only:
        query = query.filter(ContactWorkExperience.is_current == True)
    
    return [result[0] for result in query.distinct().all()]


def get_professional_network(
    db: Session,
    contact_id: int,
    tenant_id: int,
    depth: int = 1
) -> List[ContactWorkExperience]:
    """Get professional network connections for a contact"""
    # Get all companies where the contact worked
    contact_companies = db.query(ContactWorkExperience.company_name).filter(
        ContactWorkExperience.contact_id == contact_id,
        ContactWorkExperience.tenant_id == tenant_id
    ).distinct().all()
    
    company_names = [company[0] for company in contact_companies]
    
    if not company_names:
        return []
    
    # Find other contacts who worked at the same companies
    network_experiences = db.query(ContactWorkExperience).filter(
        ContactWorkExperience.company_name.in_(company_names),
        ContactWorkExperience.tenant_id == tenant_id,
        ContactWorkExperience.contact_id != contact_id  # Exclude the original contact
    ).order_by(desc(ContactWorkExperience.start_date)).all()
    
    return network_experiences


def get_contacts_with_skills(
    db: Session,
    skills: List[str],
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ContactWorkExperience]:
    """Get work experiences that include any of the specified skills"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.tenant_id == tenant_id,
        ContactWorkExperience.skills_used.op('&&')(skills)  # PostgreSQL array overlap operator
    ).order_by(desc(ContactWorkExperience.start_date)).offset(skip).limit(limit).all()


def get_potential_references(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ContactWorkExperience]:
    """Get work experiences where the person can be used as a reference"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.tenant_id == tenant_id,
        ContactWorkExperience.can_be_reference == True
    ).order_by(desc(ContactWorkExperience.start_date)).offset(skip).limit(limit).all()


def create_work_experience(
    db: Session,
    obj_in: ContactWorkExperienceCreate,
    contact_id: int,
    tenant_id: int
) -> ContactWorkExperience:
    """Create new work experience for a contact"""
    # If this is marked as current, unset any other current positions for this contact
    if obj_in.is_current:
        db.query(ContactWorkExperience).filter(
            ContactWorkExperience.contact_id == contact_id,
            ContactWorkExperience.tenant_id == tenant_id,
            ContactWorkExperience.is_current == True
        ).update({"is_current": False})
    
    db_obj = ContactWorkExperience(
        contact_id=contact_id,
        tenant_id=tenant_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_work_experience(
    db: Session,
    db_obj: ContactWorkExperience,
    obj_in: Union[ContactWorkExperienceUpdate, Dict[str, Any]]
) -> ContactWorkExperience:
    """Update work experience"""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # If updating is_current to True, unset other current positions for this contact
    if update_data.get("is_current") is True:
        db.query(ContactWorkExperience).filter(
            ContactWorkExperience.contact_id == db_obj.contact_id,
            ContactWorkExperience.tenant_id == db_obj.tenant_id,
            ContactWorkExperience.is_current == True,
            ContactWorkExperience.id != db_obj.id
        ).update({"is_current": False})
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_work_experience(
    db: Session,
    work_experience_id: int,
    tenant_id: int
) -> Optional[ContactWorkExperience]:
    """Delete work experience"""
    work_experience = get_work_experience(db, work_experience_id=work_experience_id, tenant_id=tenant_id)
    if work_experience:
        db.delete(work_experience)
        db.commit()
    return work_experience


def search_work_experiences(
    db: Session,
    query: str,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ContactWorkExperience]:
    """Search work experiences by company name, job title, or description"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.tenant_id == tenant_id,
        or_(
            ContactWorkExperience.company_name.ilike(f"%{query}%"),
            ContactWorkExperience.job_title.ilike(f"%{query}%"),
            ContactWorkExperience.job_description.ilike(f"%{query}%"),
            ContactWorkExperience.department.ilike(f"%{query}%")
        )
    ).order_by(desc(ContactWorkExperience.start_date)).offset(skip).limit(limit).all()


def get_career_timeline(db: Session, contact_id: int, tenant_id: int) -> List[ContactWorkExperience]:
    """Get career timeline for a contact"""
    return db.query(ContactWorkExperience).filter(
        ContactWorkExperience.contact_id == contact_id,
        ContactWorkExperience.tenant_id == tenant_id
    ).order_by(asc(ContactWorkExperience.start_date)).all()


def get_companies_in_tenant(db: Session, tenant_id: int) -> List[str]:
    """Get unique company names in tenant"""
    companies = db.query(ContactWorkExperience.company_name).filter(
        ContactWorkExperience.tenant_id == tenant_id
    ).distinct().all()
    return [company[0] for company in companies]


def get_skills_in_tenant(db: Session, tenant_id: int) -> List[str]:
    """Get all unique skills used across work experiences in tenant"""
    # This is a complex query due to array unnesting, simplified for now
    experiences = db.query(ContactWorkExperience.skills_used).filter(
        ContactWorkExperience.tenant_id == tenant_id,
        ContactWorkExperience.skills_used.isnot(None)
    ).all()
    
    skills = set()
    for exp in experiences:
        if exp.skills_used:
            skills.update(exp.skills_used)
    
    return sorted(list(skills))
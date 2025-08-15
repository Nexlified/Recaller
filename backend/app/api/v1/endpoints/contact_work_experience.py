from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import contact as contact_crud, contact_work_experience as work_experience_crud
from app.models.user import User
from app.schemas.contact_work_experience import (
    ContactWorkExperience, 
    ContactWorkExperienceCreate, 
    ContactWorkExperienceUpdate,
    ProfessionalConnection,
    CompanyNetwork,
    CareerTimeline
)

router = APIRouter()


@router.get("/contacts/{contact_id}/work-experience", response_model=List[ContactWorkExperience])
def get_contact_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all work experiences for a contact.
    """
    # Verify contact exists and user has access
    contact = contact_crud.get_contact_with_user_access(
        db, 
        contact_id=contact_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    work_experiences = work_experience_crud.get_contact_work_experiences(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return work_experiences


@router.get("/contacts/{contact_id}/work-experience/current", response_model=Optional[ContactWorkExperience])
def get_current_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current work experience for a contact.
    """
    # Verify contact exists and user has access
    contact = contact_crud.get_contact_with_user_access(
        db, 
        contact_id=contact_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    work_experience = work_experience_crud.get_current_work_experience(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    return work_experience


@router.post("/contacts/{contact_id}/work-experience", response_model=ContactWorkExperience)
def create_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    work_experience_in: ContactWorkExperienceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new work experience for contact. Only contact owner can add work experience.
    """
    # Verify contact exists and user can edit it
    contact = contact_crud.get_contact(
        db, 
        contact_id=contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if not contact_crud.can_user_edit_contact(contact, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="You can only add work experience to contacts you created"
        )
    
    work_experience = work_experience_crud.create_work_experience(
        db, 
        obj_in=work_experience_in, 
        contact_id=contact_id,
        tenant_id=current_user.tenant_id
    )
    return work_experience


@router.get("/work-experience/{work_experience_id}", response_model=ContactWorkExperience)
def get_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    work_experience_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get work experience by ID.
    """
    work_experience = work_experience_crud.get_work_experience(
        db, 
        work_experience_id=work_experience_id, 
        tenant_id=current_user.tenant_id
    )
    if not work_experience:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    # Check if user has access to the associated contact
    contact = contact_crud.get_contact_with_user_access(
        db, 
        contact_id=work_experience.contact_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return work_experience


@router.put("/work-experience/{work_experience_id}", response_model=ContactWorkExperience)
def update_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    work_experience_id: int,
    work_experience_in: ContactWorkExperienceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update work experience. Only contact owner can update work experience.
    """
    work_experience = work_experience_crud.get_work_experience(
        db, 
        work_experience_id=work_experience_id, 
        tenant_id=current_user.tenant_id
    )
    if not work_experience:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    # Check if user can edit the associated contact
    contact = contact_crud.get_contact(
        db, 
        contact_id=work_experience.contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact or not contact_crud.can_user_edit_contact(contact, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="You can only update work experience for contacts you created"
        )
    
    work_experience = work_experience_crud.update_work_experience(
        db, 
        db_obj=work_experience, 
        obj_in=work_experience_in
    )
    return work_experience


@router.delete("/work-experience/{work_experience_id}")
def delete_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    work_experience_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete work experience. Only contact owner can delete work experience.
    """
    work_experience = work_experience_crud.get_work_experience(
        db, 
        work_experience_id=work_experience_id, 
        tenant_id=current_user.tenant_id
    )
    if not work_experience:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    # Check if user can edit the associated contact
    contact = contact_crud.get_contact(
        db, 
        contact_id=work_experience.contact_id, 
        tenant_id=current_user.tenant_id
    )
    if not contact or not contact_crud.can_user_edit_contact(contact, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="You can only delete work experience for contacts you created"
        )
    
    work_experience_crud.delete_work_experience(
        db, 
        work_experience_id=work_experience_id, 
        tenant_id=current_user.tenant_id
    )
    return {"message": "Work experience deleted successfully"}


@router.get("/work-experience/by-company", response_model=List[ContactWorkExperience])
def get_contacts_by_company(
    *,
    db: Session = Depends(deps.get_db),
    company_name: str = Query(..., description="Company name to search for"),
    current_only: bool = Query(False, description="Only return current employees"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all contacts who worked/work at a specific company.
    """
    work_experiences = work_experience_crud.get_work_experiences_by_company(
        db,
        company_name=company_name,
        tenant_id=current_user.tenant_id,
        current_only=current_only,
        skip=skip,
        limit=limit
    )
    return work_experiences


@router.get("/contacts/{contact_id}/professional-network", response_model=List[ContactWorkExperience])
def get_professional_network(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    depth: int = Query(1, ge=1, le=3, description="Network depth (1-3)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get professional network connections for a contact.
    """
    # Verify contact exists and user has access
    contact = contact_crud.get_contact_with_user_access(
        db, 
        contact_id=contact_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    network = work_experience_crud.get_professional_network(
        db,
        contact_id=contact_id,
        tenant_id=current_user.tenant_id,
        depth=depth
    )
    return network


@router.get("/contacts/{contact_id}/career-timeline", response_model=List[ContactWorkExperience])
def get_career_timeline(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get career timeline for a contact (chronological work history).
    """
    # Verify contact exists and user has access
    contact = contact_crud.get_contact_with_user_access(
        db, 
        contact_id=contact_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    timeline = work_experience_crud.get_career_timeline(
        db,
        contact_id=contact_id,
        tenant_id=current_user.tenant_id
    )
    return timeline


@router.get("/work-experience/search", response_model=List[ContactWorkExperience])
def search_work_experiences(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search work experiences by company, job title, or description.
    """
    # Sanitize search query
    from app.core.validation import InputSanitizer
    try:
        sanitized_query = InputSanitizer.sanitize_search_query(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    work_experiences = work_experience_crud.search_work_experiences(
        db,
        query=sanitized_query,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return work_experiences


@router.get("/work-experience/references", response_model=List[ContactWorkExperience])
def get_potential_references(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contacts who can be used as references.
    """
    references = work_experience_crud.get_potential_references(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return references


@router.get("/work-experience/companies", response_model=List[str])
def get_companies(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of unique companies in tenant.
    """
    companies = work_experience_crud.get_companies_in_tenant(
        db, 
        tenant_id=current_user.tenant_id
    )
    return companies


@router.get("/work-experience/skills", response_model=List[str])
def get_skills(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of unique skills across all work experiences in tenant.
    """
    skills = work_experience_crud.get_skills_in_tenant(
        db, 
        tenant_id=current_user.tenant_id
    )
    return skills


@router.get("/work-experience/by-skills", response_model=List[ContactWorkExperience])
def get_contacts_by_skills(
    *,
    db: Session = Depends(deps.get_db),
    skills: str = Query(..., description="Comma-separated list of skills"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get work experiences that include any of the specified skills.
    """
    skill_list = [skill.strip() for skill in skills.split(",")]
    work_experiences = work_experience_crud.get_contacts_with_skills(
        db,
        skills=skill_list,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return work_experiences
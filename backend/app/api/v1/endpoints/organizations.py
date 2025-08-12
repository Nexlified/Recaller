from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud
from app.schemas import organization as org_schema
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=org_schema.Organization)
def create_organization(
    *,
    organization_in: org_schema.OrganizationCreate,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new organization.
    """
    organization = crud.organization.create_with_tenant(
        db=db, obj_in=organization_in, tenant_id=tenant_id
    )
    return organization

@router.get("/", response_model=List[org_schema.Organization])
def read_organizations(
    db: Session = Depends(deps.get_db),
    tenant_id: int = Depends(deps.get_tenant_id),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve organizations.
    """
    organizations = crud.organization.get_multi_by_tenant(
        db, tenant_id=tenant_id, skip=skip, limit=limit
    )
    return organizations

@router.get("/{organization_id}", response_model=org_schema.Organization)
def read_organization(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization or organization.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.put("/{organization_id}", response_model=org_schema.Organization)
def update_organization(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    organization_id: int,
    organization_in: org_schema.OrganizationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization or organization.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = crud.organization.update(db=db, db_obj=organization, obj_in=organization_in)
    return organization

@router.delete("/{organization_id}", response_model=org_schema.Organization)
def delete_organization(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization or organization.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = crud.organization.remove(db=db, id=organization_id)
    return organization

# Social Group endpoints

@router.post("/social-groups/", response_model=org_schema.SocialGroup)
def create_social_group(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    social_group_in: org_schema.SocialGroupCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new social group.
    """
    social_group = crud.social_group.create_with_tenant(
        db=db, obj_in=social_group_in, tenant_id=tenant_id
    )
    return social_group

@router.get("/social-groups/", response_model=List[org_schema.SocialGroup])
def read_social_groups(
    db: Session = Depends(deps.get_db),
    tenant_id: int = Depends(deps.get_tenant_id),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve social groups.
    """
    social_groups = crud.social_group.get_multi_by_tenant(
        db, tenant_id=tenant_id, skip=skip, limit=limit
    )
    return social_groups
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.crud import organization as crud_organization
from app.api import deps
from app.schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationSearchResult,
    OrganizationListResponse,
    OrganizationAlias,
    OrganizationAliasCreate,
    OrganizationLocation,
    OrganizationLocationCreate,
    OrganizationLocationUpdate,
)

router = APIRouter()


def get_pagination_meta(page: int, per_page: int, total: int) -> dict:
    """Generate pagination metadata"""
    total_pages = (total + per_page - 1) // per_page
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.get("/", response_model=OrganizationListResponse)
def list_organizations(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    organization_type: Optional[str] = Query(None, description="Filter by organization type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    search: Optional[str] = Query(None, description="Search in name, description, etc."),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(deps.get_db),
) -> Any:
    """List organizations with pagination and filtering"""
    tenant_id = request.state.tenant.id
    skip = (page - 1) * per_page
    
    organizations = crud_organization.get_organizations(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=per_page,
        organization_type=organization_type,
        industry=industry,
        search=search,
        is_active=is_active
    )
    
    total = crud_organization.get_organizations_count(
        db=db,
        tenant_id=tenant_id,
        organization_type=organization_type,
        industry=industry,
        search=search,
        is_active=is_active
    )
    
    # Convert to search result format
    data = [
        OrganizationSearchResult(
            id=org.id,
            name=org.name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            industry=org.industry,
            size_category=org.size_category,
            website=org.website,
            logo_url=org.logo_url,
            employee_count=org.employee_count,
            address_city=org.address_city,
            address_state=org.address_state,
            address_country_code=org.address_country_code,
            contact_count=0  # TODO: Implement when contacts are added
        )
        for org in organizations
    ]
    
    return OrganizationListResponse(
        data=data,
        pagination=get_pagination_meta(page, per_page, total)
    )


@router.get("/search", response_model=List[OrganizationSearchResult])
def search_organizations(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    organization_type: Optional[str] = Query(None, description="Filter by organization type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Search organizations by name, industry, location"""
    tenant_id = request.state.tenant.id
    
    organizations = crud_organization.search_organizations(
        db=db,
        tenant_id=tenant_id,
        query=query,
        organization_type=organization_type,
        industry=industry,
        limit=limit
    )
    
    return [
        OrganizationSearchResult(
            id=org.id,
            name=org.name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            industry=org.industry,
            size_category=org.size_category,
            website=org.website,
            logo_url=org.logo_url,
            employee_count=org.employee_count,
            address_city=org.address_city,
            address_state=org.address_state,
            address_country_code=org.address_country_code,
            contact_count=0  # TODO: Implement when contacts are added
        )
        for org in organizations
    ]


@router.get("/suggestions", response_model=List[OrganizationSearchResult])
def get_organization_suggestions(
    request: Request,
    name: str = Query(..., min_length=1, description="Organization name query for autocomplete"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get organization suggestions for autocomplete"""
    tenant_id = request.state.tenant.id
    
    organizations = crud_organization.get_organization_suggestions(
        db=db,
        tenant_id=tenant_id,
        name_query=name,
        limit=limit
    )
    
    return [
        OrganizationSearchResult(
            id=org.id,
            name=org.name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            industry=org.industry,
            size_category=org.size_category,
            website=org.website,
            logo_url=org.logo_url,
            employee_count=org.employee_count,
            address_city=org.address_city,
            address_state=org.address_state,
            address_country_code=org.address_country_code,
            contact_count=0
        )
        for org in organizations
    ]


@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: int,
    request: Request,
    include: Optional[str] = Query(None, description="Comma-separated list: locations,aliases"),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get organization by ID with optional related data"""
    tenant_id = request.state.tenant.id
    
    include_aliases = False
    include_locations = False
    
    if include:
        includes = [i.strip() for i in include.split(",")]
        include_aliases = "aliases" in includes
        include_locations = "locations" in includes
    
    organization = crud_organization.get_organization_by_id(
        db=db,
        organization_id=organization_id,
        tenant_id=tenant_id,
        include_aliases=include_aliases,
        include_locations=include_locations
    )
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


@router.post("/", response_model=Organization)
def create_organization(
    *,
    request: Request,
    organization_in: OrganizationCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Create new organization"""
    tenant_id = request.state.tenant.id
    
    organization = crud_organization.create_organization(
        db=db,
        obj_in=organization_in,
        tenant_id=tenant_id,
        created_by_user_id=current_user.id
    )
    
    return organization


@router.put("/{organization_id}", response_model=Organization)
def update_organization(
    *,
    organization_id: int,
    request: Request,
    organization_in: OrganizationUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Update organization"""
    tenant_id = request.state.tenant.id
    
    organization = crud_organization.get_organization_by_id(
        db=db, organization_id=organization_id, tenant_id=tenant_id
    )
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    organization = crud_organization.update_organization(
        db=db, db_obj=organization, obj_in=organization_in
    )
    
    return organization


@router.delete("/{organization_id}")
def delete_organization(
    *,
    organization_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Delete organization"""
    tenant_id = request.state.tenant.id
    
    organization = crud_organization.delete_organization(
        db=db, organization_id=organization_id, tenant_id=tenant_id
    )
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return {"message": "Organization deleted successfully"}


@router.get("/types/{organization_type}", response_model=List[OrganizationSearchResult])
def get_organizations_by_type(
    organization_type: str,
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get organizations by type (school, company, etc.)"""
    tenant_id = request.state.tenant.id
    skip = (page - 1) * per_page
    
    organizations = crud_organization.get_organizations_by_type(
        db=db,
        tenant_id=tenant_id,
        organization_type=organization_type,
        skip=skip,
        limit=per_page
    )
    
    return [
        OrganizationSearchResult(
            id=org.id,
            name=org.name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            industry=org.industry,
            size_category=org.size_category,
            website=org.website,
            logo_url=org.logo_url,
            employee_count=org.employee_count,
            address_city=org.address_city,
            address_state=org.address_state,
            address_country_code=org.address_country_code,
            contact_count=0
        )
        for org in organizations
    ]


@router.get("/industry/{industry}", response_model=List[OrganizationSearchResult])
def get_organizations_by_industry(
    industry: str,
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get organizations by industry"""
    tenant_id = request.state.tenant.id
    skip = (page - 1) * per_page
    
    organizations = crud_organization.get_organizations_by_industry(
        db=db,
        tenant_id=tenant_id,
        industry=industry,
        skip=skip,
        limit=per_page
    )
    
    return [
        OrganizationSearchResult(
            id=org.id,
            name=org.name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            industry=org.industry,
            size_category=org.size_category,
            website=org.website,
            logo_url=org.logo_url,
            employee_count=org.employee_count,
            address_city=org.address_city,
            address_state=org.address_state,
            address_country_code=org.address_country_code,
            contact_count=0
        )
        for org in organizations
    ]


# Organization Aliases
@router.post("/{organization_id}/aliases", response_model=OrganizationAlias)
def add_organization_alias(
    *,
    organization_id: int,
    request: Request,
    alias_in: OrganizationAliasCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Add alias to organization"""
    tenant_id = request.state.tenant.id
    
    alias = crud_organization.create_organization_alias(
        db=db,
        organization_id=organization_id,
        alias_in=alias_in,
        tenant_id=tenant_id
    )
    
    if not alias:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return alias


@router.delete("/{organization_id}/aliases/{alias_id}")
def remove_organization_alias(
    *,
    organization_id: int,
    alias_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Remove alias from organization"""
    tenant_id = request.state.tenant.id
    
    alias = crud_organization.delete_organization_alias(
        db=db,
        alias_id=alias_id,
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    if not alias:
        raise HTTPException(status_code=404, detail="Organization or alias not found")
    
    return {"message": "Alias removed successfully"}


# Organization Locations
@router.get("/{organization_id}/locations", response_model=List[OrganizationLocation])
def get_organization_locations(
    organization_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get organization locations"""
    tenant_id = request.state.tenant.id
    
    locations = crud_organization.get_organization_locations(
        db=db,
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    return locations


@router.post("/{organization_id}/locations", response_model=OrganizationLocation)
def add_organization_location(
    *,
    organization_id: int,
    request: Request,
    location_in: OrganizationLocationCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Add location to organization"""
    tenant_id = request.state.tenant.id
    
    location = crud_organization.create_organization_location(
        db=db,
        organization_id=organization_id,
        location_in=location_in,
        tenant_id=tenant_id
    )
    
    if not location:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return location


@router.put("/{organization_id}/locations/{location_id}", response_model=OrganizationLocation)
def update_organization_location(
    *,
    organization_id: int,
    location_id: int,
    request: Request,
    location_in: OrganizationLocationUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Update organization location"""
    tenant_id = request.state.tenant.id
    
    location = crud_organization.update_organization_location(
        db=db,
        location_id=location_id,
        location_in=location_in,
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    if not location:
        raise HTTPException(status_code=404, detail="Organization or location not found")
    
    return location


@router.delete("/{organization_id}/locations/{location_id}")
def remove_organization_location(
    *,
    organization_id: int,
    location_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Remove organization location"""
    tenant_id = request.state.tenant.id
    
    location = crud_organization.delete_organization_location(
        db=db,
        location_id=location_id,
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    if not location:
        raise HTTPException(status_code=404, detail="Organization or location not found")
    
    return {"message": "Location removed successfully"}
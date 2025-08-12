from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.models.organization import Organization, OrganizationAlias, OrganizationLocation
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationAliasCreate,
    OrganizationLocationCreate,
    OrganizationLocationUpdate
)


def get_organization_by_id(
    db: Session, 
    organization_id: int, 
    tenant_id: int,
    include_aliases: bool = False,
    include_locations: bool = False
) -> Optional[Organization]:
    query = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.tenant_id == tenant_id
    )
    
    if include_aliases:
        query = query.options(joinedload(Organization.aliases))
    if include_locations:
        query = query.options(joinedload(Organization.locations))
    
    return query.first()


def get_organizations(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    organization_type: Optional[str] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Organization]:
    query = db.query(Organization).filter(Organization.tenant_id == tenant_id)
    
    if organization_type:
        query = query.filter(Organization.organization_type == organization_type)
    
    if industry:
        query = query.filter(Organization.industry == industry)
    
    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Organization.name.ilike(search_term),
                Organization.short_name.ilike(search_term),
                Organization.description.ilike(search_term),
                Organization.industry.ilike(search_term)
            )
        )
    
    return query.offset(skip).limit(limit).all()


def get_organizations_count(
    db: Session,
    tenant_id: int,
    organization_type: Optional[str] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    query = db.query(func.count(Organization.id)).filter(Organization.tenant_id == tenant_id)
    
    if organization_type:
        query = query.filter(Organization.organization_type == organization_type)
    
    if industry:
        query = query.filter(Organization.industry == industry)
    
    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Organization.name.ilike(search_term),
                Organization.short_name.ilike(search_term),
                Organization.description.ilike(search_term),
                Organization.industry.ilike(search_term)
            )
        )
    
    return query.scalar()


def create_organization(
    db: Session, 
    obj_in: OrganizationCreate, 
    tenant_id: int,
    created_by_user_id: int
) -> Organization:
    db_obj = Organization(
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_organization(
    db: Session, 
    db_obj: Organization, 
    obj_in: Union[OrganizationUpdate, Dict[str, Any]]
) -> Organization:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_organization(db: Session, organization_id: int, tenant_id: int) -> Optional[Organization]:
    organization = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.tenant_id == tenant_id
    ).first()
    
    if organization:
        db.delete(organization)
        db.commit()
    return organization


def search_organizations(
    db: Session,
    tenant_id: int,
    query: str,
    organization_type: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 10
) -> List[Organization]:
    search_term = f"%{query}%"
    db_query = db.query(Organization).filter(Organization.tenant_id == tenant_id)
    
    # Search in name, short_name, and aliases
    alias_subquery = db.query(OrganizationAlias.organization_id).filter(
        OrganizationAlias.alias_name.ilike(search_term)
    )
    
    db_query = db_query.filter(
        or_(
            Organization.name.ilike(search_term),
            Organization.short_name.ilike(search_term),
            Organization.id.in_(alias_subquery)
        )
    )
    
    if organization_type:
        db_query = db_query.filter(Organization.organization_type == organization_type)
    
    if industry:
        db_query = db_query.filter(Organization.industry == industry)
    
    return db_query.filter(Organization.is_active == True).limit(limit).all()


def get_organization_suggestions(
    db: Session,
    tenant_id: int,
    name_query: str,
    limit: int = 5
) -> List[Organization]:
    """Get organization suggestions for autocomplete"""
    search_term = f"{name_query}%"  # Prefix search for better autocomplete
    
    return db.query(Organization).filter(
        and_(
            Organization.tenant_id == tenant_id,
            Organization.is_active == True,
            or_(
                Organization.name.ilike(search_term),
                Organization.short_name.ilike(search_term)
            )
        )
    ).order_by(Organization.name).limit(limit).all()


def get_organizations_by_type(
    db: Session,
    tenant_id: int,
    organization_type: str,
    skip: int = 0,
    limit: int = 100
) -> List[Organization]:
    return db.query(Organization).filter(
        and_(
            Organization.tenant_id == tenant_id,
            Organization.organization_type == organization_type,
            Organization.is_active == True
        )
    ).offset(skip).limit(limit).all()


def get_organizations_by_industry(
    db: Session,
    tenant_id: int,
    industry: str,
    skip: int = 0,
    limit: int = 100
) -> List[Organization]:
    return db.query(Organization).filter(
        and_(
            Organization.tenant_id == tenant_id,
            Organization.industry == industry,
            Organization.is_active == True
        )
    ).offset(skip).limit(limit).all()


# Organization Alias CRUD
def create_organization_alias(
    db: Session,
    organization_id: int,
    alias_in: OrganizationAliasCreate,
    tenant_id: int
) -> Optional[OrganizationAlias]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return None
    
    db_obj = OrganizationAlias(
        organization_id=organization_id,
        **alias_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_organization_alias(
    db: Session,
    alias_id: int,
    organization_id: int,
    tenant_id: int
) -> Optional[OrganizationAlias]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return None
    
    alias = db.query(OrganizationAlias).filter(
        OrganizationAlias.id == alias_id,
        OrganizationAlias.organization_id == organization_id
    ).first()
    
    if alias:
        db.delete(alias)
        db.commit()
    return alias


# Organization Location CRUD
def create_organization_location(
    db: Session,
    organization_id: int,
    location_in: OrganizationLocationCreate,
    tenant_id: int
) -> Optional[OrganizationLocation]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return None
    
    db_obj = OrganizationLocation(
        organization_id=organization_id,
        **location_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_organization_location(
    db: Session,
    location_id: int,
    location_in: OrganizationLocationUpdate,
    organization_id: int,
    tenant_id: int
) -> Optional[OrganizationLocation]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return None
    
    location = db.query(OrganizationLocation).filter(
        OrganizationLocation.id == location_id,
        OrganizationLocation.organization_id == organization_id
    ).first()
    
    if not location:
        return None
    
    update_data = location_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(location, field, update_data[field])
    
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def delete_organization_location(
    db: Session,
    location_id: int,
    organization_id: int,
    tenant_id: int
) -> Optional[OrganizationLocation]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return None
    
    location = db.query(OrganizationLocation).filter(
        OrganizationLocation.id == location_id,
        OrganizationLocation.organization_id == organization_id
    ).first()
    
    if location:
        db.delete(location)
        db.commit()
    return location


def get_organization_locations(
    db: Session,
    organization_id: int,
    tenant_id: int
) -> List[OrganizationLocation]:
    # Verify organization exists and belongs to tenant
    organization = get_organization_by_id(db, organization_id, tenant_id)
    if not organization:
        return []
    
    return db.query(OrganizationLocation).filter(
        OrganizationLocation.organization_id == organization_id
    ).all()

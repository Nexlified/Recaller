from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import social_group as social_group_crud
from app.models.user import User
from app.schemas.social_group import (
    SocialGroup, SocialGroupCreate, SocialGroupUpdate,
    SocialGroupMembership, SocialGroupMembershipCreate, SocialGroupMembershipUpdate,
    SocialGroupActivity, SocialGroupActivityCreate, SocialGroupActivityUpdate,
    SocialGroupActivityAttendance, SocialGroupActivityAttendanceCreate, SocialGroupActivityAttendanceUpdate
)

router = APIRouter()

# Social Group CRUD Operations
@router.get("/", response_model=List[SocialGroup])
def read_social_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    group_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve social groups with pagination & filtering.
    """
    social_groups = social_group_crud.get_social_groups(
        db, 
        skip=skip, 
        limit=limit,
        tenant_id=current_user.tenant_id,
        group_type=group_type,
        is_active=is_active
    )
    return social_groups

@router.get("/search", response_model=List[SocialGroup])
def search_social_groups(
    query: str = Query(..., description="Search query"),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search groups by name, type, description.
    """
    social_groups = social_group_crud.search_social_groups(
        db, 
        query=query,
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return social_groups

@router.get("/types/{group_type}", response_model=List[SocialGroup])
def get_groups_by_type(
    group_type: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get groups by type (friends, hobby, etc.).
    """
    social_groups = social_group_crud.get_social_groups(
        db, 
        skip=skip, 
        limit=limit,
        tenant_id=current_user.tenant_id,
        group_type=group_type
    )
    return social_groups

@router.get("/active", response_model=List[SocialGroup])
def get_active_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get active groups only.
    """
    social_groups = social_group_crud.get_social_groups(
        db, 
        skip=skip, 
        limit=limit,
        tenant_id=current_user.tenant_id,
        is_active=True
    )
    return social_groups

@router.get("/my-groups", response_model=List[SocialGroup])
def get_my_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Groups created by current user.
    """
    social_groups = social_group_crud.get_social_groups(
        db, 
        skip=skip, 
        limit=limit,
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id
    )
    return social_groups

@router.post("/", response_model=SocialGroup)
def create_social_group(
    *,
    db: Session = Depends(deps.get_db),
    social_group_in: SocialGroupCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new social group.
    """
    social_group = social_group_crud.create_social_group(
        db=db, 
        obj_in=social_group_in, 
        created_by_user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    return social_group

@router.get("/{social_group_id}", response_model=SocialGroup)
def read_social_group(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get group details.
    """
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    return social_group

@router.put("/{social_group_id}", response_model=SocialGroup)
def update_social_group(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    social_group_in: SocialGroupUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update social group.
    """
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    # Check if user has permission to update
    if social_group.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    social_group = social_group_crud.update_social_group(
        db=db, db_obj=social_group, obj_in=social_group_in
    )
    return social_group

@router.delete("/{social_group_id}", response_model=SocialGroup)
def delete_social_group(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete social group.
    """
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    # Check if user has permission to delete
    if social_group.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    social_group = social_group_crud.delete_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    return social_group

# Membership Management
@router.get("/{social_group_id}/members", response_model=List[SocialGroupMembership])
def read_group_members(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get group members with details.
    """
    # Verify group exists and user has access
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    members = social_group_crud.get_group_members(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id, status=status
    )
    return members

@router.post("/{social_group_id}/members", response_model=SocialGroupMembership)
def add_group_member(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    membership_in: SocialGroupMembershipCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add member to group.
    """
    # Verify group exists and user has access
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    # Ensure the membership is for the correct group
    membership_in.social_group_id = social_group_id
    
    # Check if membership already exists
    existing = social_group_crud.get_membership(
        db=db, 
        contact_id=membership_in.contact_id, 
        social_group_id=social_group_id, 
        tenant_id=current_user.tenant_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Contact is already a member of this group")
    
    membership = social_group_crud.create_membership(
        db=db, obj_in=membership_in, invited_by_user_id=current_user.id
    )
    return membership

@router.put("/{social_group_id}/members/{contact_id}", response_model=SocialGroupMembership)
def update_group_member(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    contact_id: int,
    membership_in: SocialGroupMembershipUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update member role/status.
    """
    membership = social_group_crud.get_membership(
        db=db, 
        contact_id=contact_id, 
        social_group_id=social_group_id, 
        tenant_id=current_user.tenant_id
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    membership = social_group_crud.update_membership(
        db=db, db_obj=membership, obj_in=membership_in
    )
    return membership

@router.delete("/{social_group_id}/members/{contact_id}", response_model=SocialGroupMembership)
def remove_group_member(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove member from group.
    """
    membership = social_group_crud.remove_membership(
        db=db, 
        contact_id=contact_id, 
        social_group_id=social_group_id, 
        tenant_id=current_user.tenant_id
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.models.social_group import SocialGroup, ContactSocialGroupMembership, SocialGroupActivity, SocialGroupActivityAttendance
from app.schemas.social_group import (
    SocialGroupCreate, SocialGroupUpdate, 
    SocialGroupMembershipCreate, SocialGroupMembershipUpdate,
    SocialGroupActivityCreate, SocialGroupActivityUpdate,
    SocialGroupActivityAttendanceCreate, SocialGroupActivityAttendanceUpdate
)

# Social Group CRUD operations
def get_social_group(db: Session, social_group_id: int, tenant_id: int = 1) -> Optional[SocialGroup]:
    return db.query(SocialGroup).filter(
        SocialGroup.id == social_group_id,
        SocialGroup.tenant_id == tenant_id
    ).first()

def get_social_groups(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: int = 1,
    group_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    created_by_user_id: Optional[int] = None
) -> List[SocialGroup]:
    query = db.query(SocialGroup).filter(SocialGroup.tenant_id == tenant_id)
    
    if group_type:
        query = query.filter(SocialGroup.group_type == group_type)
    if is_active is not None:
        query = query.filter(SocialGroup.is_active == is_active)
    if created_by_user_id:
        query = query.filter(SocialGroup.created_by_user_id == created_by_user_id)
    
    return query.order_by(desc(SocialGroup.created_at)).offset(skip).limit(limit).all()

def search_social_groups(
    db: Session,
    query: str,
    tenant_id: int = 1,
    skip: int = 0,
    limit: int = 100
) -> List[SocialGroup]:
    search_filter = or_(
        SocialGroup.name.ilike(f"%{query}%"),
        SocialGroup.description.ilike(f"%{query}%"),
        SocialGroup.tags.op('&&')(f"{{{query}}}")  # PostgreSQL array contains
    )
    
    return db.query(SocialGroup).filter(
        and_(SocialGroup.tenant_id == tenant_id, search_filter)
    ).order_by(desc(SocialGroup.created_at)).offset(skip).limit(limit).all()

def create_social_group(
    db: Session, 
    obj_in: SocialGroupCreate, 
    created_by_user_id: int,
    tenant_id: int = 1
) -> SocialGroup:
    db_obj = SocialGroup(
        tenant_id=tenant_id,
        created_by_user_id=created_by_user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_social_group(
    db: Session, 
    db_obj: SocialGroup, 
    obj_in: Union[SocialGroupUpdate, Dict[str, Any]]
) -> SocialGroup:
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

def delete_social_group(db: Session, social_group_id: int, tenant_id: int = 1) -> Optional[SocialGroup]:
    social_group = get_social_group(db, social_group_id=social_group_id, tenant_id=tenant_id)
    if social_group:
        db.delete(social_group)
        db.commit()
    return social_group

# Membership CRUD operations
def get_group_members(
    db: Session, 
    social_group_id: int, 
    tenant_id: int = 1,
    status: Optional[str] = None
) -> List[ContactSocialGroupMembership]:
    query = db.query(ContactSocialGroupMembership).join(SocialGroup).filter(
        SocialGroup.id == social_group_id,
        SocialGroup.tenant_id == tenant_id
    )
    
    if status:
        query = query.filter(ContactSocialGroupMembership.membership_status == status)
    
    return query.all()

def get_membership(
    db: Session, 
    contact_id: int, 
    social_group_id: int, 
    tenant_id: int = 1
) -> Optional[ContactSocialGroupMembership]:
    return db.query(ContactSocialGroupMembership).join(SocialGroup).filter(
        ContactSocialGroupMembership.contact_id == contact_id,
        ContactSocialGroupMembership.social_group_id == social_group_id,
        SocialGroup.tenant_id == tenant_id
    ).first()

def create_membership(
    db: Session, 
    obj_in: SocialGroupMembershipCreate,
    invited_by_user_id: Optional[int] = None
) -> ContactSocialGroupMembership:
    db_obj = ContactSocialGroupMembership(
        invited_by_user_id=invited_by_user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    
    # Update member count
    social_group = get_social_group(db, obj_in.social_group_id)
    if social_group:
        social_group.member_count = (social_group.member_count or 0) + 1
        db.add(social_group)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_membership(
    db: Session, 
    db_obj: ContactSocialGroupMembership, 
    obj_in: Union[SocialGroupMembershipUpdate, Dict[str, Any]]
) -> ContactSocialGroupMembership:
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

def remove_membership(
    db: Session, 
    contact_id: int, 
    social_group_id: int, 
    tenant_id: int = 1
) -> Optional[ContactSocialGroupMembership]:
    membership = get_membership(db, contact_id, social_group_id, tenant_id)
    if membership:
        db.delete(membership)
        
        # Update member count
        social_group = get_social_group(db, social_group_id, tenant_id)
        if social_group and social_group.member_count > 0:
            social_group.member_count = social_group.member_count - 1
            db.add(social_group)
        
        db.commit()
    return membership

# Activity CRUD operations
def get_group_activities(
    db: Session, 
    social_group_id: int, 
    tenant_id: int = 1,
    skip: int = 0,
    limit: int = 100
) -> List[SocialGroupActivity]:
    return db.query(SocialGroupActivity).join(SocialGroup).filter(
        SocialGroup.id == social_group_id,
        SocialGroup.tenant_id == tenant_id
    ).order_by(desc(SocialGroupActivity.scheduled_date)).offset(skip).limit(limit).all()

def get_activity(db: Session, activity_id: int, tenant_id: int = 1) -> Optional[SocialGroupActivity]:
    return db.query(SocialGroupActivity).join(SocialGroup).filter(
        SocialGroupActivity.id == activity_id,
        SocialGroup.tenant_id == tenant_id
    ).first()

def create_activity(
    db: Session, 
    obj_in: SocialGroupActivityCreate,
    created_by_user_id: int
) -> SocialGroupActivity:
    db_obj = SocialGroupActivity(
        created_by_user_id=created_by_user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_activity(
    db: Session, 
    db_obj: SocialGroupActivity, 
    obj_in: Union[SocialGroupActivityUpdate, Dict[str, Any]]
) -> SocialGroupActivity:
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

def delete_activity(db: Session, activity_id: int, tenant_id: int = 1) -> Optional[SocialGroupActivity]:
    activity = get_activity(db, activity_id=activity_id, tenant_id=tenant_id)
    if activity:
        db.delete(activity)
        db.commit()
    return activity

# Attendance CRUD operations
def get_activity_attendance(
    db: Session, 
    activity_id: int, 
    tenant_id: int = 1
) -> List[SocialGroupActivityAttendance]:
    return db.query(SocialGroupActivityAttendance).join(SocialGroupActivity).join(SocialGroup).filter(
        SocialGroupActivityAttendance.activity_id == activity_id,
        SocialGroup.tenant_id == tenant_id
    ).all()

def create_or_update_attendance(
    db: Session, 
    obj_in: SocialGroupActivityAttendanceCreate
) -> SocialGroupActivityAttendance:
    # Check if attendance record already exists
    existing = db.query(SocialGroupActivityAttendance).filter(
        SocialGroupActivityAttendance.activity_id == obj_in.activity_id,
        SocialGroupActivityAttendance.contact_id == obj_in.contact_id
    ).first()
    
    if existing:
        # Update existing record
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(existing, field, update_data[field])
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new record
        db_obj = SocialGroupActivityAttendance(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
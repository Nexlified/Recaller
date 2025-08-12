from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import social_group as social_group_crud
from app.models.user import User
from app.schemas.social_group import (
    SocialGroupActivity, SocialGroupActivityCreate, SocialGroupActivityUpdate,
    SocialGroupActivityAttendance, SocialGroupActivityAttendanceCreate, SocialGroupActivityAttendanceUpdate
)

router = APIRouter()

# Group Activities
@router.get("/{social_group_id}/activities", response_model=List[SocialGroupActivity])
def read_group_activities(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get group activities/events.
    """
    # Verify group exists and user has access
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    activities = social_group_crud.get_group_activities(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return activities

@router.post("/{social_group_id}/activities", response_model=SocialGroupActivity)
def create_group_activity(
    *,
    db: Session = Depends(deps.get_db),
    social_group_id: int,
    activity_in: SocialGroupActivityCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create group activity.
    """
    # Verify group exists and user has access
    social_group = social_group_crud.get_social_group(
        db=db, social_group_id=social_group_id, tenant_id=current_user.tenant_id
    )
    if not social_group:
        raise HTTPException(status_code=404, detail="Social group not found")
    
    # Ensure the activity is for the correct group
    activity_in.social_group_id = social_group_id
    
    activity = social_group_crud.create_activity(
        db=db, obj_in=activity_in, created_by_user_id=current_user.id
    )
    return activity

@router.get("/activities/{activity_id}", response_model=SocialGroupActivity)
def read_activity(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get activity details.
    """
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/activities/{activity_id}", response_model=SocialGroupActivity)
def update_activity(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    activity_in: SocialGroupActivityUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update activity.
    """
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if user has permission to update
    if activity.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    activity = social_group_crud.update_activity(
        db=db, db_obj=activity, obj_in=activity_in
    )
    return activity

@router.delete("/activities/{activity_id}", response_model=SocialGroupActivity)
def delete_activity(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete activity.
    """
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if user has permission to delete
    if activity.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    activity = social_group_crud.delete_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    return activity

# Activity Attendance
@router.get("/activities/{activity_id}/attendance", response_model=List[SocialGroupActivityAttendance])
def read_activity_attendance(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get attendance list.
    """
    # Verify activity exists and user has access
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    attendance = social_group_crud.get_activity_attendance(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    return attendance

@router.post("/activities/{activity_id}/attendance", response_model=SocialGroupActivityAttendance)
def create_or_update_attendance(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    attendance_in: SocialGroupActivityAttendanceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    RSVP to activity.
    """
    # Verify activity exists and user has access
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Ensure the attendance is for the correct activity
    attendance_in.activity_id = activity_id
    
    attendance = social_group_crud.create_or_update_attendance(
        db=db, obj_in=attendance_in
    )
    return attendance

@router.put("/activities/{activity_id}/attendance/{contact_id}", response_model=SocialGroupActivityAttendance)
def update_attendance(
    *,
    db: Session = Depends(deps.get_db),
    activity_id: int,
    contact_id: int,
    attendance_in: SocialGroupActivityAttendanceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update attendance.
    """
    # Verify activity exists and user has access
    activity = social_group_crud.get_activity(
        db=db, activity_id=activity_id, tenant_id=current_user.tenant_id
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Create attendance record with specific contact and activity
    attendance_data = SocialGroupActivityAttendanceCreate(
        activity_id=activity_id,
        contact_id=contact_id,
        **attendance_in.model_dump(exclude_unset=True)
    )
    
    attendance = social_group_crud.create_or_update_attendance(
        db=db, obj_in=attendance_data
    )
    return attendance
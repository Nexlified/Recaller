from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user, get_tenant_context
from app.crud import shared_activity
from app.schemas.shared_activity import SharedActivity, SharedActivityCreate, SharedActivityUpdate, ActivityInsights
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=SharedActivity)
def create_activity(
    *,
    request: Request,
    db: Session = Depends(get_db),
    activity_in: SharedActivityCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new shared activity"""
    tenant_id = get_tenant_context(request)
    return shared_activity.create_activity_with_participants(
        db=db, obj_in=activity_in, user_id=current_user.id, tenant_id=tenant_id
    )

@router.get("/", response_model=List[SharedActivity])
def get_activities(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get user's activities"""
    tenant_id = get_tenant_context(request)
    return shared_activity.get_activities_by_user(
        db=db, user_id=current_user.id, tenant_id=tenant_id, skip=skip, limit=limit
    )

@router.get("/upcoming", response_model=List[SharedActivity])
def get_upcoming_activities(
    request: Request,
    db: Session = Depends(get_db),
    days_ahead: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming activities"""
    tenant_id = get_tenant_context(request)
    return shared_activity.get_upcoming_activities(
        db=db, user_id=current_user.id, tenant_id=tenant_id, days_ahead=days_ahead
    )

@router.get("/contact/{contact_id}", response_model=List[SharedActivity])
def get_activities_with_contact(
    contact_id: int,
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get activities with specific contact"""
    tenant_id = get_tenant_context(request)
    return shared_activity.get_activities_by_contact(
        db=db, contact_id=contact_id, tenant_id=tenant_id, skip=skip, limit=limit
    )

@router.get("/insights", response_model=ActivityInsights)
def get_activity_insights(
    request: Request,
    db: Session = Depends(get_db),
    days_back: int = Query(365, ge=30, le=1095),
    current_user: User = Depends(get_current_user)
):
    """Get activity insights and analytics"""
    tenant_id = get_tenant_context(request)
    insights = shared_activity.get_activity_insights(
        db=db, user_id=current_user.id, tenant_id=tenant_id, days_back=days_back
    )
    return ActivityInsights(**insights)

@router.get("/{activity_id}", response_model=SharedActivity)
def get_activity(
    activity_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific activity"""
    tenant_id = get_tenant_context(request)
    activity = shared_activity.get_activity(db=db, activity_id=activity_id, tenant_id=tenant_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/{activity_id}", response_model=SharedActivity)
def update_activity(
    activity_id: int,
    *,
    request: Request,
    db: Session = Depends(get_db),
    activity_in: SharedActivityUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update activity"""
    tenant_id = get_tenant_context(request)
    activity = shared_activity.get_activity(db=db, activity_id=activity_id, tenant_id=tenant_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return shared_activity.update_activity(db=db, db_obj=activity, obj_in=activity_in)

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete activity"""
    tenant_id = get_tenant_context(request)
    success = shared_activity.delete_activity(db=db, activity_id=activity_id, tenant_id=tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {"message": "Activity deleted successfully"}
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, extract
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

from app.models.shared_activity import SharedActivity, SharedActivityParticipant
from app.schemas.shared_activity import SharedActivityCreate, SharedActivityUpdate

def create_activity_with_participants(
    db: Session, *, obj_in: SharedActivityCreate, user_id: int, tenant_id: int
) -> SharedActivity:
    """Create activity with participants"""
    # Create activity
    activity_data = obj_in.dict(exclude={'participants'})
    activity = SharedActivity(
        **activity_data,
        created_by_user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(activity)
    db.flush()  # Get the ID
    
    # Create participants
    for participant_data in obj_in.participants:
        participant = SharedActivityParticipant(
            **participant_data.dict(),
            activity_id=activity.id,
            tenant_id=tenant_id
        )
        db.add(participant)
    
    db.commit()
    db.refresh(activity)
    return activity

def get_activity(db: Session, activity_id: int, tenant_id: int) -> Optional[SharedActivity]:
    """Get activity by ID with tenant filtering"""
    return (
        db.query(SharedActivity)
        .filter(
            and_(
                SharedActivity.id == activity_id,
                SharedActivity.tenant_id == tenant_id
            )
        )
        .options(joinedload(SharedActivity.participants))
        .first()
    )

def get_activities_by_user(
    db: Session, *, user_id: int, tenant_id: int, skip: int = 0, limit: int = 100
) -> List[SharedActivity]:
    """Get activities created by user"""
    return (
        db.query(SharedActivity)
        .filter(
            and_(
                SharedActivity.created_by_user_id == user_id,
                SharedActivity.tenant_id == tenant_id
            )
        )
        .options(joinedload(SharedActivity.participants))
        .order_by(desc(SharedActivity.activity_date))
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_activities_by_contact(
    db: Session, *, contact_id: int, tenant_id: int, skip: int = 0, limit: int = 100
) -> List[SharedActivity]:
    """Get activities involving specific contact"""
    return (
        db.query(SharedActivity)
        .join(SharedActivityParticipant)
        .filter(
            and_(
                SharedActivityParticipant.contact_id == contact_id,
                SharedActivity.tenant_id == tenant_id
            )
        )
        .options(joinedload(SharedActivity.participants))
        .order_by(desc(SharedActivity.activity_date))
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_upcoming_activities(
    db: Session, *, user_id: int, tenant_id: int, days_ahead: int = 30
) -> List[SharedActivity]:
    """Get upcoming activities"""
    end_date = date.today() + timedelta(days=days_ahead)
    return (
        db.query(SharedActivity)
        .filter(
            and_(
                SharedActivity.created_by_user_id == user_id,
                SharedActivity.tenant_id == tenant_id,
                SharedActivity.activity_date >= date.today(),
                SharedActivity.activity_date <= end_date,
                SharedActivity.status.in_(['planned', 'confirmed'])
            )
        )
        .options(joinedload(SharedActivity.participants))
        .order_by(SharedActivity.activity_date)
        .all()
    )

def update_activity(
    db: Session, *, db_obj: SharedActivity, obj_in: SharedActivityUpdate
) -> SharedActivity:
    """Update activity"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_activity(db: Session, *, activity_id: int, tenant_id: int) -> bool:
    """Delete activity and its participants"""
    activity = get_activity(db=db, activity_id=activity_id, tenant_id=tenant_id)
    if activity:
        db.delete(activity)
        db.commit()
        return True
    return False

def get_activity_insights(
    db: Session, *, user_id: int, tenant_id: int, days_back: int = 365
) -> Dict[str, Any]:
    """Get activity insights and analytics"""
    start_date = date.today() - timedelta(days=days_back)
    
    # Base query
    base_query = db.query(SharedActivity).filter(
        and_(
            SharedActivity.created_by_user_id == user_id,
            SharedActivity.tenant_id == tenant_id,
            SharedActivity.activity_date >= start_date,
            SharedActivity.status == 'completed'
        )
    )
    
    # Total activities
    total_activities = base_query.count()
    
    # Activities this month
    current_month_start = date.today().replace(day=1)
    activities_this_month = base_query.filter(
        SharedActivity.activity_date >= current_month_start
    ).count()
    
    # Favorite activity type
    activity_type_counts = (
        base_query
        .with_entities(SharedActivity.activity_type, func.count(SharedActivity.id))
        .group_by(SharedActivity.activity_type)
        .order_by(desc(func.count(SharedActivity.id)))
        .first()
    )
    favorite_activity_type = activity_type_counts[0] if activity_type_counts else None
    
    # Average quality rating
    avg_rating = base_query.with_entities(
        func.avg(SharedActivity.quality_rating)
    ).scalar()
    
    # Total spent
    total_spent = base_query.with_entities(
        func.sum(SharedActivity.total_cost)
    ).scalar()
    
    # Activity frequency by type
    activity_frequency_results = (
        base_query
        .with_entities(SharedActivity.activity_type, func.count(SharedActivity.id))
        .group_by(SharedActivity.activity_type)
        .all()
    )
    activity_frequency = {activity_type: count for activity_type, count in activity_frequency_results}
    
    return {
        'total_activities': total_activities,
        'activities_this_month': activities_this_month,
        'favorite_activity_type': favorite_activity_type,
        'average_quality_rating': float(avg_rating) if avg_rating else None,
        'total_spent': float(total_spent) if total_spent else None,
        'most_active_contacts': [],  # This would need a more complex query
        'activity_frequency': activity_frequency,
    }
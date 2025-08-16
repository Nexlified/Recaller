from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import date, datetime

from app.models.gift import Gift, GiftIdea, GiftStatus, GiftPriority
from app.schemas.gift_system import GiftCreate, GiftUpdate, GiftIdeaCreate, GiftIdeaUpdate


# Gift CRUD Operations
def get_gift(db: Session, gift_id: int, tenant_id: int) -> Optional[Gift]:
    """Get gift by ID within tenant"""
    return db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True
    ).first()


def get_gift_with_user_access(
    db: Session, 
    gift_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[Gift]:
    """Get gift if user has access (owns it within tenant)"""
    return db.query(Gift).filter(
        and_(
            Gift.id == gift_id,
            Gift.tenant_id == tenant_id,
            Gift.user_id == user_id,
            Gift.is_active == True
        )
    ).first()


def get_gifts(
    db: Session, 
    user_id: int,
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    occasion: Optional[str] = None,
    recipient_contact_id: Optional[int] = None
) -> List[Gift]:
    """Get gifts for user with optional filtering"""
    query = db.query(Gift).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True
    )
    
    if status:
        query = query.filter(Gift.status == status)
    if category:
        query = query.filter(Gift.category == category)
    if occasion:
        query = query.filter(Gift.occasion == occasion)
    if recipient_contact_id:
        query = query.filter(Gift.recipient_contact_id == recipient_contact_id)
    
    return query.order_by(desc(Gift.created_at)).offset(skip).limit(limit).all()


def create_gift(
    db: Session, 
    obj_in: GiftCreate, 
    user_id: int,
    tenant_id: int
) -> Gift:
    """Create new gift"""
    db_obj = Gift(
        tenant_id=tenant_id,
        user_id=user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_gift(
    db: Session, 
    db_obj: Gift, 
    obj_in: Union[GiftUpdate, Dict[str, Any]]
) -> Gift:
    """Update gift"""
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


def delete_gift(db: Session, db_obj: Gift) -> Gift:
    """Soft delete gift by marking as inactive"""
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_gifts_by_recipient(
    db: Session,
    user_id: int,
    tenant_id: int,
    recipient_contact_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Gift]:
    """Get gifts for a specific recipient"""
    return db.query(Gift).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.recipient_contact_id == recipient_contact_id,
        Gift.is_active == True
    ).order_by(desc(Gift.created_at)).offset(skip).limit(limit).all()


def get_gifts_by_occasion_date_range(
    db: Session,
    user_id: int,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> List[Gift]:
    """Get gifts within a date range"""
    return db.query(Gift).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.occasion_date >= start_date,
        Gift.occasion_date <= end_date,
        Gift.is_active == True
    ).order_by(asc(Gift.occasion_date)).all()


# Gift Idea CRUD Operations
def get_gift_idea(db: Session, idea_id: int, tenant_id: int) -> Optional[GiftIdea]:
    """Get gift idea by ID within tenant"""
    return db.query(GiftIdea).filter(
        GiftIdea.id == idea_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.is_active == True
    ).first()


def get_gift_idea_with_user_access(
    db: Session, 
    idea_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[GiftIdea]:
    """Get gift idea if user has access (owns it within tenant)"""
    return db.query(GiftIdea).filter(
        and_(
            GiftIdea.id == idea_id,
            GiftIdea.tenant_id == tenant_id,
            GiftIdea.user_id == user_id,
            GiftIdea.is_active == True
        )
    ).first()


def get_gift_ideas(
    db: Session, 
    user_id: int,
    tenant_id: int,
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    target_contact_id: Optional[int] = None,
    is_favorite: Optional[bool] = None,
    min_rating: Optional[int] = None
) -> List[GiftIdea]:
    """Get gift ideas for user with optional filtering"""
    query = db.query(GiftIdea).filter(
        GiftIdea.user_id == user_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.is_active == True
    )
    
    if category:
        query = query.filter(GiftIdea.category == category)
    if target_contact_id:
        query = query.filter(GiftIdea.target_contact_id == target_contact_id)
    if is_favorite is not None:
        query = query.filter(GiftIdea.is_favorite == is_favorite)
    if min_rating:
        query = query.filter(GiftIdea.rating >= min_rating)
    
    return query.order_by(desc(GiftIdea.created_at)).offset(skip).limit(limit).all()


def create_gift_idea(
    db: Session, 
    obj_in: GiftIdeaCreate, 
    user_id: int,
    tenant_id: int
) -> GiftIdea:
    """Create new gift idea"""
    db_obj = GiftIdea(
        tenant_id=tenant_id,
        user_id=user_id,
        **obj_in.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_gift_idea(
    db: Session, 
    db_obj: GiftIdea, 
    obj_in: Union[GiftIdeaUpdate, Dict[str, Any]]
) -> GiftIdea:
    """Update gift idea"""
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


def delete_gift_idea(db: Session, db_obj: GiftIdea) -> GiftIdea:
    """Soft delete gift idea by marking as inactive"""
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def search_gift_ideas(
    db: Session,
    user_id: int,
    tenant_id: int,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[GiftIdea]:
    """Search gift ideas by title, description, tags, or category"""
    search_term = f"%{query}%"
    return db.query(GiftIdea).filter(
        GiftIdea.user_id == user_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.is_active == True,
        or_(
            GiftIdea.title.ilike(search_term),
            GiftIdea.description.ilike(search_term),
            GiftIdea.category.ilike(search_term),
            GiftIdea.notes.ilike(search_term)
        )
    ).order_by(desc(GiftIdea.created_at)).offset(skip).limit(limit).all()


def get_gift_ideas_for_contact(
    db: Session,
    user_id: int,
    tenant_id: int,
    contact_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[GiftIdea]:
    """Get gift ideas for a specific contact"""
    return db.query(GiftIdea).filter(
        GiftIdea.user_id == user_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.target_contact_id == contact_id,
        GiftIdea.is_active == True
    ).order_by(desc(GiftIdea.rating), desc(GiftIdea.created_at)).offset(skip).limit(limit).all()


def get_popular_gift_ideas(
    db: Session,
    user_id: int,
    tenant_id: int,
    limit: int = 10
) -> List[GiftIdea]:
    """Get most popular gift ideas (by times_gifted)"""
    return db.query(GiftIdea).filter(
        GiftIdea.user_id == user_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.is_active == True,
        GiftIdea.times_gifted > 0
    ).order_by(desc(GiftIdea.times_gifted), desc(GiftIdea.rating)).limit(limit).all()


def mark_gift_idea_as_gifted(
    db: Session,
    db_obj: GiftIdea,
    gifted_date: date = None
) -> GiftIdea:
    """Mark gift idea as gifted (increment counter and update last gifted date)"""
    db_obj.times_gifted += 1
    db_obj.last_gifted_date = gifted_date or date.today()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# Analytics Helper Functions
def get_gift_analytics(
    db: Session,
    user_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """Get basic gift analytics for user"""
    
    # Basic counts
    total_gifts = db.query(Gift).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True
    ).count()
    
    total_ideas = db.query(GiftIdea).filter(
        GiftIdea.user_id == user_id,
        GiftIdea.tenant_id == tenant_id,
        GiftIdea.is_active == True
    ).count()
    
    # Status breakdown
    status_counts = db.query(
        Gift.status,
        func.count(Gift.id).label('count')
    ).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True
    ).group_by(Gift.status).all()
    
    # Category breakdown
    category_counts = db.query(
        Gift.category,
        func.count(Gift.id).label('count')
    ).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True,
        Gift.category.isnot(None)
    ).group_by(Gift.category).all()
    
    # Budget analytics
    budget_stats = db.query(
        func.sum(Gift.budget_amount).label('total_budget'),
        func.sum(Gift.actual_amount).label('total_spent'),
        func.avg(Gift.budget_amount).label('avg_budget'),
        func.avg(Gift.actual_amount).label('avg_spent')
    ).filter(
        Gift.user_id == user_id,
        Gift.tenant_id == tenant_id,
        Gift.is_active == True
    ).first()
    
    return {
        "total_gifts": total_gifts,
        "total_ideas": total_ideas,
        "status_breakdown": {status: count for status, count in status_counts},
        "category_breakdown": {category: count for category, count in category_counts},
        "budget_analytics": {
            "total_budget": float(budget_stats.total_budget or 0),
            "total_spent": float(budget_stats.total_spent or 0),
            "average_budget": float(budget_stats.avg_budget or 0),
            "average_spent": float(budget_stats.avg_spent or 0)
        }
    }
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.transaction_category import TransactionCategory
from app.schemas.transaction_category import TransactionCategoryCreate, TransactionCategoryUpdate

def get_transaction_category(
    db: Session,
    category_id: int,
    tenant_id: int
) -> Optional[TransactionCategory]:
    """Get a single transaction category by ID"""
    return db.query(TransactionCategory).filter(
        and_(
            TransactionCategory.id == category_id,
            TransactionCategory.tenant_id == tenant_id
        )
    ).first()

def get_transaction_category_by_user(
    db: Session,
    category_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[TransactionCategory]:
    """Get a transaction category by ID for a specific user (includes system categories)"""
    return db.query(TransactionCategory).filter(
        and_(
            TransactionCategory.id == category_id,
            TransactionCategory.tenant_id == tenant_id,
            or_(
                TransactionCategory.user_id == user_id,
                TransactionCategory.is_system == True
            )
        )
    ).first()

def get_transaction_categories_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    include_system: bool = True
) -> List[TransactionCategory]:
    """Get transaction categories for a user"""
    query = db.query(TransactionCategory).filter(
        TransactionCategory.tenant_id == tenant_id
    )
    
    if include_system:
        query = query.filter(
            or_(
                TransactionCategory.user_id == user_id,
                TransactionCategory.is_system == True
            )
        )
    else:
        query = query.filter(TransactionCategory.user_id == user_id)
    
    return query.order_by(TransactionCategory.name).all()

def get_system_categories(
    db: Session,
    tenant_id: int
) -> List[TransactionCategory]:
    """Get all system transaction categories"""
    return db.query(TransactionCategory).filter(
        and_(
            TransactionCategory.tenant_id == tenant_id,
            TransactionCategory.is_system == True
        )
    ).order_by(TransactionCategory.name).all()

def create_transaction_category(
    db: Session,
    *,
    obj_in: TransactionCategoryCreate,
    user_id: int,
    tenant_id: int,
    is_system: bool = False
) -> TransactionCategory:
    """Create a new transaction category"""
    db_obj = TransactionCategory(
        **obj_in.dict(),
        user_id=user_id if not is_system else None,
        tenant_id=tenant_id,
        is_system=is_system
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_transaction_category(
    db: Session,
    *,
    db_obj: TransactionCategory,
    obj_in: TransactionCategoryUpdate
) -> TransactionCategory:
    """Update an existing transaction category"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_transaction_category(
    db: Session,
    *,
    category_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[TransactionCategory]:
    """Delete a user-created transaction category (system categories cannot be deleted)"""
    db_obj = db.query(TransactionCategory).filter(
        and_(
            TransactionCategory.id == category_id,
            TransactionCategory.user_id == user_id,
            TransactionCategory.tenant_id == tenant_id,
            TransactionCategory.is_system == False
        )
    ).first()
    
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return db_obj
    return None
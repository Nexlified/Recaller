from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.transaction_subcategory import TransactionSubcategory
from app.schemas.transaction_subcategory import TransactionSubcategoryCreate, TransactionSubcategoryUpdate

def get_transaction_subcategory(
    db: Session,
    subcategory_id: int,
    tenant_id: int
) -> Optional[TransactionSubcategory]:
    """Get a single transaction subcategory by ID"""
    return db.query(TransactionSubcategory).filter(
        and_(
            TransactionSubcategory.id == subcategory_id,
            TransactionSubcategory.category.has(tenant_id=tenant_id)
        )
    ).first()

def get_transaction_subcategory_by_user(
    db: Session,
    subcategory_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[TransactionSubcategory]:
    """Get a transaction subcategory by ID for a specific user"""
    return db.query(TransactionSubcategory).join(
        TransactionSubcategory.category
    ).filter(
        and_(
            TransactionSubcategory.id == subcategory_id,
            TransactionSubcategory.category.has(tenant_id=tenant_id),
            or_(
                TransactionSubcategory.category.has(user_id=user_id),
                TransactionSubcategory.category.has(is_system=True)
            )
        )
    ).first()

def get_transaction_subcategories_by_category(
    db: Session,
    category_id: int,
    tenant_id: int
) -> List[TransactionSubcategory]:
    """Get all subcategories for a specific category"""
    return db.query(TransactionSubcategory).join(
        TransactionSubcategory.category
    ).filter(
        and_(
            TransactionSubcategory.category_id == category_id,
            TransactionSubcategory.category.has(tenant_id=tenant_id)
        )
    ).order_by(TransactionSubcategory.name).all()

def get_transaction_subcategories_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    category_id: Optional[int] = None
) -> List[TransactionSubcategory]:
    """Get transaction subcategories for a user"""
    query = db.query(TransactionSubcategory).join(
        TransactionSubcategory.category
    ).filter(
        and_(
            TransactionSubcategory.category.has(tenant_id=tenant_id),
            or_(
                TransactionSubcategory.category.has(user_id=user_id),
                TransactionSubcategory.category.has(is_system=True)
            )
        )
    )
    
    if category_id:
        query = query.filter(TransactionSubcategory.category_id == category_id)
    
    return query.order_by(TransactionSubcategory.name).all()

def create_transaction_subcategory(
    db: Session,
    *,
    obj_in: TransactionSubcategoryCreate,
    tenant_id: int
) -> TransactionSubcategory:
    """Create a new transaction subcategory"""
    # Verify the category exists and belongs to the tenant
    from app.models.transaction_category import TransactionCategory
    category = db.query(TransactionCategory).filter(
        and_(
            TransactionCategory.id == obj_in.category_id,
            TransactionCategory.tenant_id == tenant_id
        )
    ).first()
    
    if not category:
        raise ValueError("Category not found or does not belong to tenant")
    
    db_obj = TransactionSubcategory(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_transaction_subcategory(
    db: Session,
    *,
    db_obj: TransactionSubcategory,
    obj_in: TransactionSubcategoryUpdate
) -> TransactionSubcategory:
    """Update an existing transaction subcategory"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_transaction_subcategory(
    db: Session,
    *,
    subcategory_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[TransactionSubcategory]:
    """Delete a transaction subcategory (only if user owns the parent category)"""
    db_obj = db.query(TransactionSubcategory).join(
        TransactionSubcategory.category
    ).filter(
        and_(
            TransactionSubcategory.id == subcategory_id,
            TransactionSubcategory.category.has(user_id=user_id),
            TransactionSubcategory.category.has(tenant_id=tenant_id),
            TransactionSubcategory.category.has(is_system=False)
        )
    ).first()
    
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return db_obj
    return None
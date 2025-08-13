from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.financial_account import FinancialAccount
from app.schemas.financial_account import FinancialAccountCreate, FinancialAccountUpdate

def get_financial_account(
    db: Session,
    account_id: int,
    tenant_id: int
) -> Optional[FinancialAccount]:
    """Get a single financial account by ID"""
    return db.query(FinancialAccount).filter(
        and_(
            FinancialAccount.id == account_id,
            FinancialAccount.tenant_id == tenant_id
        )
    ).first()

def get_financial_account_by_user(
    db: Session,
    account_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[FinancialAccount]:
    """Get a financial account by ID for a specific user"""
    return db.query(FinancialAccount).filter(
        and_(
            FinancialAccount.id == account_id,
            FinancialAccount.user_id == user_id,
            FinancialAccount.tenant_id == tenant_id
        )
    ).first()

def get_financial_accounts_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    active_only: bool = True
) -> List[FinancialAccount]:
    """Get financial accounts for a user"""
    query = db.query(FinancialAccount).filter(
        and_(
            FinancialAccount.user_id == user_id,
            FinancialAccount.tenant_id == tenant_id
        )
    )
    
    if active_only:
        query = query.filter(FinancialAccount.is_active == True)
    
    return query.order_by(FinancialAccount.account_name).all()

def create_financial_account(
    db: Session,
    *,
    obj_in: FinancialAccountCreate,
    user_id: int,
    tenant_id: int
) -> FinancialAccount:
    """Create a new financial account"""
    db_obj = FinancialAccount(
        **obj_in.dict(),
        user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_financial_account(
    db: Session,
    *,
    db_obj: FinancialAccount,
    obj_in: FinancialAccountUpdate
) -> FinancialAccount:
    """Update an existing financial account"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_account_balance(
    db: Session,
    *,
    db_obj: FinancialAccount,
    new_balance: float
) -> FinancialAccount:
    """Update account balance"""
    db_obj.current_balance = new_balance
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_financial_account(
    db: Session,
    *,
    account_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[FinancialAccount]:
    """Delete a financial account (soft delete by setting is_active=False)"""
    db_obj = db.query(FinancialAccount).filter(
        and_(
            FinancialAccount.id == account_id,
            FinancialAccount.user_id == user_id,
            FinancialAccount.tenant_id == tenant_id
        )
    ).first()
    
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    return None
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate

def get(db: Session, id: int) -> Optional[Budget]:
    """Get a single budget by ID"""
    return db.query(Budget).filter(Budget.id == id).first()

def get_budget(
    db: Session,
    budget_id: int,
    tenant_id: int
) -> Optional[Budget]:
    """Get a single budget by ID"""
    return db.query(Budget).filter(
        and_(
            Budget.id == budget_id,
            Budget.tenant_id == tenant_id
        )
    ).first()

def get_budget_by_user(
    db: Session,
    budget_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[Budget]:
    """Get a budget by ID for a specific user"""
    return db.query(Budget).filter(
        and_(
            Budget.id == budget_id,
            Budget.user_id == user_id,
            Budget.tenant_id == tenant_id
        )
    ).first()

def get_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    active_only: bool = True
) -> List[Budget]:
    """Get budgets for a user"""
    query = db.query(Budget).filter(
        and_(
            Budget.user_id == user_id,
            Budget.tenant_id == tenant_id
        )
    )
    
    if active_only:
        query = query.filter(Budget.is_active == True)
    
    return query.order_by(Budget.name).all()

def get_budgets_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    active_only: bool = True
) -> List[Budget]:
    """Get budgets for a user"""
    return get_by_user(db, user_id=user_id, tenant_id=tenant_id, active_only=active_only)

def get_budget_spending_summary(
    db: Session,
    budget: Budget,
    current_date: date = None
) -> dict:
    """Calculate spending summary for a budget"""
    if current_date is None:
        current_date = date.today()
    
    # Calculate the current period based on budget period
    if budget.period == 'monthly':
        start_date = date(current_date.year, current_date.month, 1)
        if current_date.month == 12:
            end_date = date(current_date.year + 1, 1, 1)
        else:
            end_date = date(current_date.year, current_date.month + 1, 1)
    elif budget.period == 'quarterly':
        quarter = (current_date.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = date(current_date.year, start_month, 1)
        end_month = start_month + 3
        if end_month > 12:
            end_date = date(current_date.year + 1, end_month - 12, 1)
        else:
            end_date = date(current_date.year, end_month, 1)
    elif budget.period == 'yearly':
        start_date = date(current_date.year, 1, 1)
        end_date = date(current_date.year + 1, 1, 1)
    else:
        # Use budget dates if period is custom
        start_date = budget.start_date
        end_date = budget.end_date or current_date
    
    # Query transactions for the budget period
    query = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == budget.user_id,
            Transaction.tenant_id == budget.tenant_id,
            Transaction.type == 'debit',  # Only debits count toward budget spending
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
    )
    
    # Filter by category/subcategory if specified
    if budget.category_id:
        query = query.filter(Transaction.category_id == budget.category_id)
    if budget.subcategory_id:
        query = query.filter(Transaction.subcategory_id == budget.subcategory_id)
    
    spent_amount = query.scalar() or 0
    remaining_amount = budget.budget_amount - spent_amount
    spent_percentage = (spent_amount / budget.budget_amount) * 100 if budget.budget_amount > 0 else 0
    is_over_budget = spent_amount > budget.budget_amount
    
    # Calculate days remaining in period
    days_remaining = (end_date - current_date).days
    
    return {
        'spent_amount': spent_amount,
        'remaining_amount': remaining_amount,
        'spent_percentage': spent_percentage,
        'is_over_budget': is_over_budget,
        'days_remaining': max(0, days_remaining),
        'period_start': start_date,
        'period_end': end_date
    }

def create(
    db: Session,
    *,
    obj_in: BudgetCreate,
    user_id: int,
    tenant_id: int
) -> Budget:
    """Create a new budget"""
    db_obj = Budget(
        **obj_in.dict(),
        user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_budget(
    db: Session,
    *,
    obj_in: BudgetCreate,
    user_id: int,
    tenant_id: int
) -> Budget:
    """Create a new budget"""
    return create(db, obj_in=obj_in, user_id=user_id, tenant_id=tenant_id)

def update(
    db: Session,
    *,
    db_obj: Budget,
    obj_in: BudgetUpdate
) -> Budget:
    """Update an existing budget"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_budget(
    db: Session,
    *,
    db_obj: Budget,
    obj_in: BudgetUpdate
) -> Budget:
    """Update an existing budget"""
    return update(db, db_obj=db_obj, obj_in=obj_in)

def remove(db: Session, *, id: int) -> Optional[Budget]:
    """Delete a budget (hard delete)"""
    obj = db.query(Budget).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj

def delete_budget(
    db: Session,
    *,
    budget_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[Budget]:
    """Delete a budget (soft delete by setting is_active=False)"""
    db_obj = db.query(Budget).filter(
        and_(
            Budget.id == budget_id,
            Budget.user_id == user_id,
            Budget.tenant_id == tenant_id
        )
    ).first()
    
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    return None

def get_budgets_over_alert_threshold(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    current_date: date = None
) -> List[tuple[Budget, dict]]:
    """Get budgets that have exceeded their alert threshold"""
    if current_date is None:
        current_date = date.today()
    
    budgets = get_budgets_by_user(db, user_id=user_id, tenant_id=tenant_id, active_only=True)
    alert_budgets = []
    
    for budget in budgets:
        summary = get_budget_spending_summary(db, budget, current_date)
        if summary['spent_percentage'] >= budget.alert_percentage:
            alert_budgets.append((budget, summary))
    
    return alert_budgets
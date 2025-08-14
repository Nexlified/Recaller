from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.recurring_transaction import RecurringTransaction
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionUpdate

def get(db: Session, id: int) -> Optional[RecurringTransaction]:
    """Get a single recurring transaction by ID"""
    return db.query(RecurringTransaction).filter(RecurringTransaction.id == id).first()

def get_recurring_transaction(
    db: Session,
    recurring_id: int,
    tenant_id: int
) -> Optional[RecurringTransaction]:
    """Get a single recurring transaction by ID"""
    return db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.tenant_id == tenant_id
        )
    ).first()

def get_recurring_transaction_by_user(
    db: Session,
    recurring_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[RecurringTransaction]:
    """Get a recurring transaction by ID for a specific user"""
    return db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.tenant_id == tenant_id
        )
    ).first()

def get_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    active_only: bool = True
) -> List[RecurringTransaction]:
    """Get recurring transactions for a user"""
    query = db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.tenant_id == tenant_id
        )
    )
    
    if active_only:
        query = query.filter(RecurringTransaction.is_active == True)
    
    return query.order_by(RecurringTransaction.next_due_date).all()

def get_recurring_transactions_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    active_only: bool = True
) -> List[RecurringTransaction]:
    """Get recurring transactions for a user"""
    return get_by_user(db, user_id=user_id, tenant_id=tenant_id, active_only=active_only)

def get_due_reminders(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    reminder_date: date
) -> List[RecurringTransaction]:
    """Get recurring transactions due for reminders"""
    return db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.tenant_id == tenant_id,
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_due_date <= reminder_date
        )
    ).all()

def get_all_due(
    db: Session,
    *,
    reminder_date: date
) -> List[RecurringTransaction]:
    """Get all due recurring transactions across all users"""
    return db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_due_date <= reminder_date
        )
    ).all()

def increment_occurrences(
    db: Session,
    *,
    recurring_id: int
) -> bool:
    """Increment the occurrence count for a recurring transaction"""
    db_obj = db.query(RecurringTransaction).filter(
        RecurringTransaction.id == recurring_id
    ).first()
    if db_obj:
        if not hasattr(db_obj, 'occurrence_count') or db_obj.occurrence_count is None:
            db_obj.occurrence_count = 0
        db_obj.occurrence_count += 1
        db.add(db_obj)
        db.commit()
        return True
    return False

def calculate_next_due_date(recurring_transaction: RecurringTransaction) -> date:
    """Calculate the next due date based on frequency and interval"""
    current_date = recurring_transaction.next_due_date or recurring_transaction.start_date
    
    if recurring_transaction.frequency == 'daily':
        return current_date + timedelta(days=recurring_transaction.interval_count)
    elif recurring_transaction.frequency == 'weekly':
        return current_date + timedelta(weeks=recurring_transaction.interval_count)
    elif recurring_transaction.frequency == 'monthly':
        # Handle month-end dates properly
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        return next_month
    elif recurring_transaction.frequency == 'quarterly':
        # Add 3 months
        month = current_date.month + 3
        year = current_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        return current_date.replace(year=year, month=month)
    elif recurring_transaction.frequency == 'yearly':
        return current_date.replace(year=current_date.year + recurring_transaction.interval_count)
    
    return current_date

def create(
    db: Session,
    *,
    obj_in: RecurringTransactionCreate,
    user_id: int,
    tenant_id: int
) -> RecurringTransaction:
    """Create a new recurring transaction"""
    db_obj = RecurringTransaction(
        **obj_in.dict(),
        user_id=user_id,
        tenant_id=tenant_id,
        next_due_date=obj_in.start_date
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_recurring_transaction(
    db: Session,
    *,
    obj_in: RecurringTransactionCreate,
    user_id: int,
    tenant_id: int
) -> RecurringTransaction:
    """Create a new recurring transaction"""
    return create(db, obj_in=obj_in, user_id=user_id, tenant_id=tenant_id)

def update(
    db: Session,
    *,
    db_obj: RecurringTransaction,
    obj_in: RecurringTransactionUpdate
) -> RecurringTransaction:
    """Update an existing recurring transaction"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # Recalculate next due date if frequency or start date changed
    if 'frequency' in update_data or 'start_date' in update_data or 'interval_count' in update_data:
        db_obj.next_due_date = calculate_next_due_date(db_obj)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_recurring_transaction(
    db: Session,
    *,
    db_obj: RecurringTransaction,
    obj_in: RecurringTransactionUpdate
) -> RecurringTransaction:
    """Update an existing recurring transaction"""
    return update(db, db_obj=db_obj, obj_in=obj_in)

def update_next_due_date(
    db: Session,
    *,
    db_obj: RecurringTransaction
) -> RecurringTransaction:
    """Update the next due date for a recurring transaction"""
    db_obj.next_due_date = calculate_next_due_date(db_obj)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, id: int) -> Optional[RecurringTransaction]:
    """Delete a recurring transaction (hard delete)"""
    obj = db.query(RecurringTransaction).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj

def delete_recurring_transaction(
    db: Session,
    *,
    recurring_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[RecurringTransaction]:
    """Delete a recurring transaction (soft delete by setting is_active=False)"""
    db_obj = db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.tenant_id == tenant_id
        )
    ).first()
    
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    return None
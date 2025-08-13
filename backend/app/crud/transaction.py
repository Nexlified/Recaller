from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

def get_transaction(db: Session, transaction_id: int, tenant_id: int) -> Optional[Transaction]:
    """Get a single transaction by ID"""
    return db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.tenant_id == tenant_id
        )
    ).first()

def get_transaction_by_user(
    db: Session,
    transaction_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[Transaction]:
    """Get a transaction by ID for a specific user"""
    return db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
            Transaction.tenant_id == tenant_id
        )
    ).first()

def get_transactions_by_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Transaction]:
    """Get transactions for a user with optional filters"""
    query = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.tenant_id == tenant_id
        )
    )
    
    if filters:
        if filters.get('type'):
            query = query.filter(Transaction.type == filters['type'])
        if filters.get('category_id'):
            query = query.filter(Transaction.category_id == filters['category_id'])
        if filters.get('account_id'):
            query = query.filter(Transaction.account_id == filters['account_id'])
        if filters.get('date_from'):
            query = query.filter(Transaction.transaction_date >= filters['date_from'])
        if filters.get('date_to'):
            query = query.filter(Transaction.transaction_date <= filters['date_to'])
        if filters.get('amount_min'):
            query = query.filter(Transaction.amount >= filters['amount_min'])
        if filters.get('amount_max'):
            query = query.filter(Transaction.amount <= filters['amount_max'])
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.reference_number.ilike(search_term)
                )
            )
    
    return query.order_by(desc(Transaction.transaction_date)).offset(skip).limit(limit).all()

def get_monthly_summary(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    year: int,
    month: int
) -> Dict[str, Any]:
    """Get monthly transaction summary for a user"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    query = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.tenant_id == tenant_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
    )
    
    total_credits = query.filter(Transaction.type == 'credit').with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    total_debits = query.filter(Transaction.type == 'debit').with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    return {
        'total_credits': total_credits,
        'total_debits': total_debits,
        'net_amount': total_credits - total_debits,
        'transaction_count': query.count()
    }

def get_category_breakdown(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Get transaction breakdown by category"""
    query = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.tenant_id == tenant_id
        )
    )
    
    if date_from:
        query = query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(Transaction.transaction_date <= date_to)
    
    return query.group_by(Transaction.category_id).all()

def get_account_summary(
    db: Session,
    *,
    account_id: int,
    user_id: int
) -> Dict[str, Any]:
    """Get transaction summary for a specific account"""
    query = db.query(Transaction).filter(
        and_(
            Transaction.account_id == account_id,
            Transaction.user_id == user_id
        )
    )
    
    total_credits = query.filter(Transaction.type == 'credit').with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    total_debits = query.filter(Transaction.type == 'debit').with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    transaction_count = query.count()
    
    last_transaction = query.order_by(desc(Transaction.transaction_date)).first()
    last_transaction_date = last_transaction.transaction_date if last_transaction else None
    
    return {
        'transaction_count': transaction_count,
        'total_credits': total_credits,
        'total_debits': total_debits,
        'last_transaction_date': last_transaction_date
    }

def count_by_account(db: Session, account_id: int) -> int:
    """Count transactions for a specific account"""
    return db.query(Transaction).filter(Transaction.account_id == account_id).count()

def create_transaction(
    db: Session,
    *,
    obj_in: TransactionCreate,
    user_id: int,
    tenant_id: int
) -> Transaction:
    """Create a new transaction"""
    db_obj = Transaction(
        **obj_in.dict(),
        user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create(
    db: Session,
    *,
    obj_in: TransactionCreate
) -> Transaction:
    """Create a new transaction (alternative method)"""
    db_obj = Transaction(**obj_in.dict())
    db.add(db_obj)
    db.commit() 
    db.refresh(db_obj)
    return db_obj

def get_by_recurring_and_date(
    db: Session,
    *,
    recurring_id: int,
    transaction_date: date
) -> Optional[Transaction]:
    """Check if a transaction already exists for this recurring template and date"""
    return db.query(Transaction).filter(
        and_(
            Transaction.recurring_template_id == recurring_id,
            Transaction.transaction_date == transaction_date
        )
    ).first()

def update_transaction(
    db: Session,
    *,
    db_obj: Transaction,
    obj_in: TransactionUpdate
) -> Transaction:
    """Update an existing transaction"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_transaction(
    db: Session,
    *,
    transaction_id: int,
    user_id: int,
    tenant_id: int
) -> Optional[Transaction]:
    """Delete a transaction"""
    db_obj = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
            Transaction.tenant_id == tenant_id
        )
    ).first()
    
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return db_obj
    return None
from typing import List, Optional
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.personal_debt import PersonalDebt, DebtPayment, DebtStatus, PaymentStatus
from app.schemas.personal_debt import PersonalDebtCreate, PersonalDebtUpdate, DebtPaymentCreate, DebtPaymentUpdate


def get_personal_debt(db: Session, debt_id: int, tenant_id: int) -> Optional[PersonalDebt]:
    """Get a personal debt by ID within tenant."""
    return db.query(PersonalDebt).filter(
        and_(
            PersonalDebt.id == debt_id,
            PersonalDebt.tenant_id == tenant_id
        )
    ).first()


def get_personal_debt_by_user(
    db: Session, 
    debt_id: int,
    user_id: int, 
    tenant_id: int
) -> Optional[PersonalDebt]:
    """Get personal debt with user access validation."""
    return db.query(PersonalDebt).filter(
        and_(
            PersonalDebt.id == debt_id,
            PersonalDebt.user_id == user_id,
            PersonalDebt.tenant_id == tenant_id
        )
    ).first()


def get_personal_debts_by_user(
    db: Session, 
    user_id: int, 
    tenant_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[PersonalDebt]:
    """Get personal debts for a specific user within their tenant."""
    return db.query(PersonalDebt).filter(
        and_(
            PersonalDebt.user_id == user_id,
            PersonalDebt.tenant_id == tenant_id
        )
    ).offset(skip).limit(limit).all()


def get_debts_where_user_is_creditor(
    db: Session,
    user_id: int,
    tenant_id: int,
    status: Optional[DebtStatus] = None
) -> List[PersonalDebt]:
    """Get debts where the user is the creditor (money owed TO the user)."""
    query = db.query(PersonalDebt).join(
        Contact, PersonalDebt.creditor_contact_id == Contact.id
    ).filter(
        and_(
            Contact.created_by_user_id == user_id,
            PersonalDebt.tenant_id == tenant_id
        )
    )
    
    if status:
        query = query.filter(PersonalDebt.status == status)
        
    return query.all()


def get_debts_where_user_is_debtor(
    db: Session,
    user_id: int,
    tenant_id: int,
    status: Optional[DebtStatus] = None
) -> List[PersonalDebt]:
    """Get debts where the user is the debtor (money the user OWES)."""
    query = db.query(PersonalDebt).join(
        Contact, PersonalDebt.debtor_contact_id == Contact.id
    ).filter(
        and_(
            Contact.created_by_user_id == user_id,
            PersonalDebt.tenant_id == tenant_id
        )
    )
    
    if status:
        query = query.filter(PersonalDebt.status == status)
        
    return query.all()


def get_overdue_debts(
    db: Session,
    user_id: int,
    tenant_id: int,
    as_of_date: Optional[date] = None
) -> List[PersonalDebt]:
    """Get overdue debts for a user."""
    if as_of_date is None:
        as_of_date = date.today()
        
    return db.query(PersonalDebt).filter(
        and_(
            PersonalDebt.user_id == user_id,
            PersonalDebt.tenant_id == tenant_id,
            PersonalDebt.due_date < as_of_date,
            PersonalDebt.status == DebtStatus.ACTIVE,
            PersonalDebt.payment_status != PaymentStatus.PAID
        )
    ).all()


def get_debt_summary(
    db: Session,
    user_id: int,
    tenant_id: int
) -> dict:
    """Get summary statistics for user's debts."""
    # Get debts where user is creditor (money owed TO user)
    creditor_debts = get_debts_where_user_is_creditor(db, user_id, tenant_id, DebtStatus.ACTIVE)
    
    # Get debts where user is debtor (money user OWES)
    debtor_debts = get_debts_where_user_is_debtor(db, user_id, tenant_id, DebtStatus.ACTIVE)
    
    # Calculate totals
    total_owed_to_me = sum(debt.amount for debt in creditor_debts if debt.payment_status != PaymentStatus.PAID)
    total_i_owe = sum(debt.amount for debt in debtor_debts if debt.payment_status != PaymentStatus.PAID)
    
    # Count overdue debts
    overdue_count = len(get_overdue_debts(db, user_id, tenant_id))
    
    return {
        "total_debts": len(creditor_debts) + len(debtor_debts),
        "total_amount_owed_to_me": total_owed_to_me,
        "total_amount_i_owe": total_i_owe,
        "active_debts": len([d for d in creditor_debts + debtor_debts if d.status == DebtStatus.ACTIVE]),
        "overdue_debts": overdue_count
    }


def create_personal_debt(
    db: Session,
    obj_in: PersonalDebtCreate,
    user_id: int,
    tenant_id: int
) -> PersonalDebt:
    """Create a personal debt with user and tenant information."""
    obj_data = obj_in.dict()
    obj_data["user_id"] = user_id
    obj_data["tenant_id"] = tenant_id
    
    db_obj = PersonalDebt(**obj_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_personal_debt(
    db: Session,
    db_obj: PersonalDebt,
    obj_in: PersonalDebtUpdate
) -> PersonalDebt:
    """Update a personal debt."""
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_personal_debt(db: Session, debt_id: int, tenant_id: int) -> Optional[PersonalDebt]:
    """Delete a personal debt."""
    debt = get_personal_debt(db, debt_id=debt_id, tenant_id=tenant_id)
    if debt:
        db.delete(debt)
        db.commit()
    return debt


# Debt Payment functions
def get_debt_payment(db: Session, payment_id: int) -> Optional[DebtPayment]:
    """Get a debt payment by ID."""
    return db.query(DebtPayment).filter(DebtPayment.id == payment_id).first()


def get_payments_by_debt(
    db: Session,
    debt_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[DebtPayment]:
    """Get payments for a specific debt."""
    return db.query(DebtPayment).filter(
        DebtPayment.debt_id == debt_id
    ).order_by(desc(DebtPayment.payment_date)).offset(skip).limit(limit).all()


def get_total_paid(
    db: Session,
    debt_id: int
) -> Decimal:
    """Get total amount paid for a debt."""
    result = db.query(func.sum(DebtPayment.amount)).filter(
        DebtPayment.debt_id == debt_id
    ).scalar()
    return result or Decimal('0.00')


def create_debt_payment(
    db: Session,
    obj_in: DebtPaymentCreate
) -> DebtPayment:
    """Create a debt payment and update debt payment status."""
    # Create the payment
    obj_data = obj_in.dict()
    payment = DebtPayment(**obj_data)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Update debt payment status
    debt = db.query(PersonalDebt).filter(PersonalDebt.id == obj_in.debt_id).first()
    if debt:
        total_paid = get_total_paid(db, obj_in.debt_id)
        
        if total_paid >= debt.amount:
            debt.payment_status = PaymentStatus.PAID
            debt.status = DebtStatus.PAID
        elif total_paid > 0:
            debt.payment_status = PaymentStatus.PARTIAL
        
        db.commit()
        db.refresh(debt)
    
    return payment


def update_debt_payment(
    db: Session,
    db_obj: DebtPayment,
    obj_in: DebtPaymentUpdate
) -> DebtPayment:
    """Update a debt payment."""
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_debt_payment(db: Session, payment_id: int) -> Optional[DebtPayment]:
    """Delete a debt payment."""
    payment = get_debt_payment(db, payment_id)
    if payment:
        db.delete(payment)
        db.commit()
    return payment


# Import Contact after functions to avoid circular imports
from app.models.contact import Contact
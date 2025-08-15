from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.models.personal_debt import DebtStatus, PaymentStatus
from app.crud import personal_debt as debt_crud
from app.schemas.personal_debt import (
    PersonalDebt, PersonalDebtCreate, PersonalDebtUpdate, PersonalDebtWithPayments, PersonalDebtSummary,
    DebtPayment, DebtPaymentCreate, DebtPaymentUpdate
)

router = APIRouter()


@router.post("/", response_model=PersonalDebt)
def create_personal_debt(
    *,
    db: Session = Depends(deps.get_db),
    debt_in: PersonalDebtCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Create new personal debt."""
    tenant_id = current_user.tenant_id
    
    # Verify contacts exist and belong to user's tenant
    creditor = crud.contact.get_contact_with_user_access(
        db, debt_in.creditor_contact_id, current_user.id, tenant_id
    )
    debtor = crud.contact.get_contact_with_user_access(
        db, debt_in.debtor_contact_id, current_user.id, tenant_id
    )
    
    if not creditor:
        raise HTTPException(status_code=404, detail="Creditor contact not found")
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor contact not found")
    
    debt = debt_crud.create_personal_debt(
        db=db, 
        obj_in=debt_in, 
        user_id=current_user.id, 
        tenant_id=tenant_id
    )
    return debt


@router.get("/", response_model=List[PersonalDebt])
def read_personal_debts(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: DebtStatus = Query(None, description="Filter by debt status"),
) -> Any:
    """Retrieve personal debts."""
    tenant_id = current_user.tenant_id
    
    if status:
        # Filter by status using existing methods
        if status == DebtStatus.ACTIVE:
            creditor_debts = debt_crud.get_debts_where_user_is_creditor(
                db, current_user.id, tenant_id, status
            )
            debtor_debts = debt_crud.get_debts_where_user_is_debtor(
                db, current_user.id, tenant_id, status
            )
            debts = creditor_debts + debtor_debts
        else:
            debts = debt_crud.get_personal_debts_by_user(
                db, user_id=current_user.id, tenant_id=tenant_id, skip=skip, limit=limit
            )
            debts = [d for d in debts if d.status == status]
    else:
        debts = debt_crud.get_personal_debts_by_user(
            db, user_id=current_user.id, tenant_id=tenant_id, skip=skip, limit=limit
        )
    
    return debts


@router.get("/summary", response_model=PersonalDebtSummary)
def get_debt_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get debt summary for current user."""
    tenant_id = current_user.tenant_id
    summary = debt_crud.get_debt_summary(db, current_user.id, tenant_id)
    return summary


@router.get("/overdue", response_model=List[PersonalDebt])
def get_overdue_debts(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get overdue debts for current user."""
    tenant_id = current_user.tenant_id
    overdue_debts = debt_crud.get_overdue_debts(db, current_user.id, tenant_id)
    return overdue_debts


@router.get("/owed-to-me", response_model=List[PersonalDebt])
def get_debts_owed_to_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    status: DebtStatus = Query(DebtStatus.ACTIVE, description="Filter by debt status"),
) -> Any:
    """Get debts where money is owed to current user."""
    tenant_id = current_user.tenant_id
    debts = debt_crud.get_debts_where_user_is_creditor(
        db, current_user.id, tenant_id, status
    )
    return debts


@router.get("/i-owe", response_model=List[PersonalDebt])
def get_debts_i_owe(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    status: DebtStatus = Query(DebtStatus.ACTIVE, description="Filter by debt status"),
) -> Any:
    """Get debts where current user owes money."""
    tenant_id = current_user.tenant_id
    debts = debt_crud.get_debts_where_user_is_debtor(
        db, current_user.id, tenant_id, status
    )
    return debts


@router.get("/{debt_id}", response_model=PersonalDebtWithPayments)
def read_personal_debt(
    *,
    db: Session = Depends(deps.get_db),
    debt_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get specific personal debt with payment history."""
    tenant_id = current_user.tenant_id
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Personal debt not found")
    
    # Get payments for this debt
    payments = debt_crud.get_payments_by_debt(db, debt_id)
    total_paid = debt_crud.get_total_paid(db, debt_id)
    
    # Create response with payments
    debt_dict = PersonalDebt.from_orm(debt).dict()
    debt_dict["payments"] = [DebtPayment.from_orm(p) for p in payments]
    debt_dict["total_paid"] = total_paid
    debt_dict["remaining_balance"] = debt.amount - total_paid
    
    return PersonalDebtWithPayments(**debt_dict)


@router.put("/{debt_id}", response_model=PersonalDebt)
def update_personal_debt(
    *,
    db: Session = Depends(deps.get_db),
    debt_id: int,
    debt_in: PersonalDebtUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update personal debt."""
    tenant_id = current_user.tenant_id
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Personal debt not found")
    
    # Verify contacts if being updated
    if debt_in.creditor_contact_id:
        creditor = crud.contact.get_contact_with_user_access(
            db, debt_in.creditor_contact_id, current_user.id, tenant_id
        )
        if not creditor:
            raise HTTPException(status_code=404, detail="Creditor contact not found")
    
    if debt_in.debtor_contact_id:
        debtor = crud.contact.get_contact_with_user_access(
            db, debt_in.debtor_contact_id, current_user.id, tenant_id
        )
        if not debtor:
            raise HTTPException(status_code=404, detail="Debtor contact not found")
    
    debt = debt_crud.update_personal_debt(db=db, db_obj=debt, obj_in=debt_in)
    return debt


@router.delete("/{debt_id}")
def delete_personal_debt(
    *,
    db: Session = Depends(deps.get_db),
    debt_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete personal debt."""
    tenant_id = current_user.tenant_id
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Personal debt not found")
    
    debt = debt_crud.delete_personal_debt(db=db, debt_id=debt_id, tenant_id=tenant_id)
    return {"message": "Personal debt deleted successfully"}


# Debt Payment endpoints
@router.post("/{debt_id}/payments", response_model=DebtPayment)
def create_debt_payment(
    *,
    db: Session = Depends(deps.get_db),
    debt_id: int,
    payment_in: DebtPaymentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a payment for a debt."""
    tenant_id = current_user.tenant_id
    
    # Verify debt exists and user has access
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Personal debt not found")
    
    # Set debt_id on payment
    payment_in.debt_id = debt_id
    payment = debt_crud.create_debt_payment(db=db, obj_in=payment_in)
    return payment


@router.get("/{debt_id}/payments", response_model=List[DebtPayment])
def read_debt_payments(
    *,
    db: Session = Depends(deps.get_db),
    debt_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """Get payments for a specific debt."""
    tenant_id = current_user.tenant_id
    
    # Verify debt exists and user has access
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Personal debt not found")
    
    payments = debt_crud.get_payments_by_debt(db, debt_id, skip=skip, limit=limit)
    return payments


@router.put("/payments/{payment_id}", response_model=DebtPayment)
def update_debt_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_id: int,
    payment_in: DebtPaymentUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update debt payment."""
    tenant_id = current_user.tenant_id
    
    # Get payment and verify access through debt
    payment = debt_crud.get_debt_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=payment.debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Access denied")
    
    payment = debt_crud.update_debt_payment(db=db, db_obj=payment, obj_in=payment_in)
    
    # Recalculate debt payment status
    total_paid = debt_crud.get_total_paid(db, payment.debt_id)
    if total_paid >= debt.amount:
        debt.payment_status = PaymentStatus.PAID
        debt.status = DebtStatus.PAID
    elif total_paid > 0:
        debt.payment_status = PaymentStatus.PARTIAL
    else:
        debt.payment_status = PaymentStatus.UNPAID
    
    db.commit()
    return payment


@router.delete("/payments/{payment_id}")
def delete_debt_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete debt payment."""
    tenant_id = current_user.tenant_id
    
    # Get payment and verify access through debt
    payment = debt_crud.get_debt_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    debt = debt_crud.get_personal_debt_by_user(
        db, debt_id=payment.debt_id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not debt:
        raise HTTPException(status_code=404, detail="Access denied")
    
    debt_id = payment.debt_id
    debt_crud.delete_debt_payment(db=db, payment_id=payment_id)
    
    # Recalculate debt payment status
    total_paid = debt_crud.get_total_paid(db, debt_id)
    if total_paid >= debt.amount:
        debt.payment_status = PaymentStatus.PAID
        debt.status = DebtStatus.PAID
    elif total_paid > 0:
        debt.payment_status = PaymentStatus.PARTIAL
    else:
        debt.payment_status = PaymentStatus.UNPAID
    
    db.commit()
    return {"message": "Payment deleted successfully"}
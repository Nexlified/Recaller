from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate, TransactionWithDetails
from app.api import deps

router = APIRouter()

@router.post("/", response_model=Transaction)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Create new transaction."""
    tenant_id = current_user.tenant_id
    transaction = crud.transaction.create_transaction(
        db=db, 
        obj_in=transaction_in,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return transaction

@router.get("/", response_model=List[Transaction])
def read_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve transactions."""
    tenant_id = current_user.tenant_id
    transactions = crud.transaction.get_transactions_by_user(
        db, 
        user_id=current_user.id, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=limit
    )
    return transactions

@router.get("/{id}", response_model=Transaction)
def read_transaction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Get transaction by ID."""
    tenant_id = current_user.tenant_id
    transaction = crud.transaction.get_transaction_by_user(
        db=db, transaction_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
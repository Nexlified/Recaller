from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas import transaction as transaction_schemas
from app.schemas import financial_account as financial_account_schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=transaction_schemas.Transaction)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: transaction_transaction_schemas.TransactionCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Create new transaction."""
    tenant_id = current_user.tenant_id
    transaction_data = transaction_in.dict()
    transaction_data["user_id"] = current_user.id
    transaction_data["tenant_id"] = tenant_id
    
    transaction = crud.transaction.create_transaction(
        db=db, 
        obj_in=transaction_transaction_schemas.TransactionCreate(**transaction_data),
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    # Update account balance if account is specified
    if transaction.account_id:
        account = crud.financial_account.get_financial_account_by_user(
            db=db, account_id=transaction.account_id, user_id=current_user.id, tenant_id=tenant_id
        )
        if account:
            if transaction.type == "credit":
                new_balance = float(account.current_balance) + float(transaction.amount)
            else:
                new_balance = float(account.current_balance) - float(transaction.amount)
            crud.financial_account.update_account_balance(db=db, db_obj=account, new_balance=new_balance)
    
    return transaction

@router.get("/", response_model=List[transaction_schemas.Transaction])
def read_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    account_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve transactions with filtering."""
    tenant_id = current_user.tenant_id
    
    filters = {}
    if type:
        filters["type"] = type
    if category_id:
        filters["category_id"] = category_id
    if account_id:
        filters["account_id"] = account_id
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    if search:
        filters["search"] = search
    
    transactions = crud.transaction.get_transactions_by_user(
        db, 
        user_id=current_user.id, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=limit, 
        filters=filters
    )
    return transactions

@router.get("/{id}", response_model=transaction_transaction_schemas.TransactionWithDetails)
def read_transaction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Get transaction by ID."""
    tenant_id = current_user.tenant_id
    transaction = crud.transaction.get_transaction_by_user(
        db=db, transaction_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{id}", response_model=transaction_schemas.Transaction)
def update_transaction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    transaction_in: transaction_transaction_schemas.TransactionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Update transaction."""
    tenant_id = current_user.tenant_id
    transaction = crud.transaction.get_transaction_by_user(
        db=db, transaction_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Handle account balance updates
    old_amount = float(transaction.amount)
    old_type = transaction.type
    old_account_id = transaction.account_id
    
    transaction = crud.transaction.update_transaction(db=db, db_obj=transaction, obj_in=transaction_in)
    
    # Update account balances if needed
    if old_account_id or transaction.account_id:
        # Revert old transaction effect
        if old_account_id:
            old_account = crud.financial_account.get_financial_account_by_user(
                db=db, account_id=old_account_id, user_id=current_user.id, tenant_id=tenant_id
            )
            if old_account:
                revert_amount = old_amount if old_type == "debit" else -old_amount
                new_balance = float(old_account.current_balance) + revert_amount
                crud.financial_account.update_account_balance(db=db, db_obj=old_account, new_balance=new_balance)
        
        # Apply new transaction effect
        if transaction.account_id:
            account = crud.financial_account.get_financial_account_by_user(
                db=db, account_id=transaction.account_id, user_id=current_user.id, tenant_id=tenant_id
            )
            if account:
                effect_amount = float(transaction.amount) if transaction.type == "credit" else -float(transaction.amount)
                new_balance = float(account.current_balance) + effect_amount
                crud.financial_account.update_account_balance(db=db, db_obj=account, new_balance=new_balance)
    
    return transaction

@router.delete("/{id}")
def delete_transaction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Delete transaction."""
    tenant_id = current_user.tenant_id
    transaction = crud.transaction.get_transaction_by_user(
        db=db, transaction_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Revert account balance if needed
    if transaction.account_id:
        account = crud.financial_account.get_financial_account_by_user(
            db=db, account_id=transaction.account_id, user_id=current_user.id, tenant_id=tenant_id
        )
        if account:
            revert_amount = float(transaction.amount) if transaction.type == "debit" else -float(transaction.amount)
            new_balance = float(account.current_balance) + revert_amount
            crud.financial_account.update_account_balance(db=db, db_obj=account, new_balance=new_balance)
    
    transaction = crud.transaction.delete_transaction(
        db=db, transaction_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    return {"message": "Transaction deleted successfully"}

@router.get("/summary/monthly")
def get_monthly_summary(
    *,
    db: Session = Depends(deps.get_db),
    year: int = Query(...),
    month: int = Query(...),
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Get monthly transaction summary."""
    tenant_id = current_user.tenant_id
    summary = crud.transaction.get_monthly_summary(
        db, user_id=current_user.id, tenant_id=tenant_id, year=year, month=month
    )
    return summary

@router.get("/analytics/category-breakdown")
def get_category_breakdown(
    *,
    db: Session = Depends(deps.get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Get spending breakdown by category."""
    tenant_id = current_user.tenant_id
    breakdown = crud.transaction.get_category_breakdown(
        db, user_id=current_user.id, tenant_id=tenant_id, date_from=date_from, date_to=date_to
    )
    return breakdown

@router.post("/bulk")
def bulk_create_transactions(
    *,
    db: Session = Depends(deps.get_db),
    transactions_in: List[transaction_transaction_schemas.TransactionCreate],
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Bulk create transactions (for import)."""
    tenant_id = current_user.tenant_id
    created_transactions = []
    failed_transactions = []
    
    for transaction_data in transactions_in:
        try:
            transaction_dict = transaction_data.dict()
            transaction_dict["user_id"] = current_user.id
            transaction_dict["tenant_id"] = tenant_id
            
            transaction = crud.transaction.create_transaction(
                db=db, 
                obj_in=transaction_transaction_schemas.TransactionCreate(**transaction_dict),
                user_id=current_user.id,
                tenant_id=tenant_id
            )
            created_transactions.append(transaction)
            
            # Update account balance
            if transaction.account_id:
                account = crud.financial_account.get_financial_account_by_user(
                    db=db, account_id=transaction.account_id, user_id=current_user.id, tenant_id=tenant_id
                )
                if account:
                    if transaction.type == "credit":
                        new_balance = float(account.current_balance) + float(transaction.amount)
                    else:
                        new_balance = float(account.current_balance) - float(transaction.amount)
                    crud.financial_account.update_account_balance(db=db, db_obj=account, new_balance=new_balance)
        except Exception as e:
            failed_transactions.append({"data": transaction_data.dict(), "error": str(e)})
    
    return {
        "created": len(created_transactions),
        "failed": len(failed_transactions),
        "transactions": created_transactions,
        "errors": failed_transactions
    }
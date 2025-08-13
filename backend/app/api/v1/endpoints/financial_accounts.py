from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.financial_account import FinancialAccount, FinancialAccountCreate, FinancialAccountUpdate, FinancialAccountWithSummary
from app.api import deps

router = APIRouter()

@router.post("/", response_model=FinancialAccount)
def create_financial_account(
    *,
    db: Session = Depends(deps.get_db),
    account_in: FinancialAccountCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Create new financial account."""
    tenant_id = current_user.tenant_id
    account_data = account_in.dict()
    account_data["user_id"] = current_user.id
    account_data["tenant_id"] = tenant_id
    
    account = crud.financial_account.create_financial_account(
        db=db, 
        obj_in=FinancialAccountCreate(**account_data),
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return account

@router.get("/", response_model=List[FinancialAccountWithSummary])
def read_financial_accounts(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Retrieve financial accounts with transaction summaries."""
    tenant_id = current_user.tenant_id
    accounts = crud.financial_account.get_financial_accounts_by_user(
        db, user_id=current_user.id, tenant_id=tenant_id
    )
    
    # Add transaction summaries
    accounts_with_summary = []
    for account in accounts:
        # Get transaction summary for this account
        summary = crud.transaction.get_account_summary(db, account_id=account.id, user_id=current_user.id)
        account_dict = FinancialAccount.from_orm(account).dict()
        account_dict.update(summary)
        accounts_with_summary.append(FinancialAccountWithSummary(**account_dict))
    
    return accounts_with_summary

@router.get("/{id}", response_model=FinancialAccount)
def read_financial_account(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Get financial account by ID."""
    tenant_id = current_user.tenant_id
    account = crud.financial_account.get_financial_account_by_user(
        db=db, account_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not account:
        raise HTTPException(status_code=404, detail="Financial account not found")
    return account

@router.put("/{id}", response_model=FinancialAccount)
def update_financial_account(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    account_in: FinancialAccountUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Update financial account."""
    tenant_id = current_user.tenant_id
    account = crud.financial_account.get_financial_account_by_user(
        db=db, account_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not account:
        raise HTTPException(status_code=404, detail="Financial account not found")
    
    account = crud.financial_account.update_financial_account(db=db, db_obj=account, obj_in=account_in)
    return account

@router.delete("/{id}")
def delete_financial_account(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """Delete financial account."""
    tenant_id = current_user.tenant_id
    account = crud.financial_account.get_financial_account_by_user(
        db=db, account_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not account:
        raise HTTPException(status_code=404, detail="Financial account not found")
    
    # Check if account has transactions
    transaction_count = crud.transaction.count_by_account(db, account_id=id)
    if transaction_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete account with {transaction_count} transactions. Please delete transactions first or deactivate the account."
        )
    
    account = crud.financial_account.delete_financial_account(
        db=db, account_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    return {"message": "Financial account deleted successfully"}
from typing import Any, List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.recurring_transaction_service import RecurringTransactionService

router = APIRouter()

@router.post("/", response_model=schemas.RecurringTransaction)
def create_recurring_transaction(
    *,
    db: Session = Depends(deps.get_db),
    recurring_in: schemas.RecurringTransactionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Create new recurring transaction."""
    tenant_id = request.state.tenant.id
    recurring_data = recurring_in.dict()
    recurring_data["user_id"] = current_user.id
    recurring_data["tenant_id"] = tenant_id
    
    # Calculate next due date
    service = RecurringTransactionService(db)
    next_due = service.calculate_next_due_date(
        start_date=recurring_in.start_date,
        frequency=recurring_in.frequency,
        interval_count=recurring_in.interval_count
    )
    recurring_data["next_due_date"] = next_due
    
    recurring = crud.recurring_transaction.create(
        db=db, 
        obj_in=schemas.RecurringTransactionCreate(**recurring_data),
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return recurring

@router.get("/", response_model=List[schemas.RecurringTransactionWithNext])
def read_recurring_transactions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Retrieve recurring transactions with next occurrence info."""
    tenant_id = request.state.tenant.id
    recurring_transactions = crud.recurring_transaction.get_by_user(
        db, user_id=current_user.id, tenant_id=tenant_id
    )
    
    # Add next occurrence info
    service = RecurringTransactionService(db)
    result = []
    for recurring in recurring_transactions:
        recurring_dict = schemas.RecurringTransaction.from_orm(recurring).dict()
        next_info = service.get_next_occurrence_info(recurring)
        recurring_dict.update(next_info)
        result.append(schemas.RecurringTransactionWithNext(**recurring_dict))
    
    return result

@router.get("/due-reminders")
def get_due_reminders(
    *,
    db: Session = Depends(deps.get_db),
    days_ahead: int = 7,
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get recurring transactions due for reminders."""
    tenant_id = request.state.tenant.id
    reminder_date = date.today() + timedelta(days=days_ahead)
    
    due_reminders = crud.recurring_transaction.get_due_reminders(
        db, user_id=current_user.id, tenant_id=tenant_id, reminder_date=reminder_date
    )
    return due_reminders

@router.post("/{id}/generate-transaction")
def generate_transaction_from_recurring(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Generate transaction from recurring template."""
    tenant_id = request.state.tenant.id
    recurring = crud.recurring_transaction.get_recurring_transaction_by_user(
        db=db, recurring_id=id, user_id=current_user.id, tenant_id=tenant_id
    )
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    service = RecurringTransactionService(db)
    transaction = service.generate_transaction_from_template(recurring)
    
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
    
    # Update next due date
    next_due = service.calculate_next_due_date_from_recurring(recurring)
    crud.recurring_transaction.update(
        db=db, 
        db_obj=recurring, 
        obj_in=schemas.RecurringTransactionUpdate(next_due_date=next_due)
    )
    
    return transaction

@router.post("/process-all-due")
def process_all_due_recurring(
    *,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Process all due recurring transactions for the user."""
    tenant_id = request.state.tenant.id
    service = RecurringTransactionService(db)
    
    background_tasks.add_task(
        service.process_due_recurring_transactions,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return {"message": "Processing due recurring transactions in background"}
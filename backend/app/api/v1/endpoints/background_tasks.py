from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.api import deps
from app.services.background_tasks import (
    process_all_recurring_transactions,
    process_user_recurring_transactions,
    send_recurring_transaction_reminders,
    get_task_status
)

router = APIRouter()

@router.post("/recurring-transactions/process")
def trigger_recurring_transaction_processing(
    *,
    db: Session = Depends(deps.get_db),
    dry_run: bool = False,
    current_user: User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Trigger processing of user's recurring transactions."""
    tenant_id = deps.get_tenant_context(request)
    
    # Trigger background task for this user
    task = process_user_recurring_transactions.delay(
        user_id=current_user.id,
        tenant_id=tenant_id,
        dry_run=dry_run
    )
    
    return {
        "task_id": task.id,
        "message": f"{'Dry run' if dry_run else 'Processing'} recurring transactions in background",
        "user_id": current_user.id
    }

@router.post("/recurring-transactions/send-reminders")
def trigger_recurring_transaction_reminders(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Trigger sending of recurring transaction reminders for user."""
    tenant_id = deps.get_tenant_context(request)
    
    # Trigger background task for this user
    task = send_recurring_transaction_reminders.delay(
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return {
        "task_id": task.id,
        "message": "Sending recurring transaction reminders in background",
        "user_id": current_user.id
    }

@router.get("/tasks/{task_id}/status")
def get_background_task_status(
    *,
    task_id: str,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Get status of a background task."""
    try:
        task_status = get_task_status.delay(task_id)
        return task_status.get(timeout=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get task status: {str(e)}")

# Admin endpoints (for system-wide operations)
@router.post("/admin/recurring-transactions/process-all")
def admin_trigger_all_recurring_processing(
    *,
    db: Session = Depends(deps.get_db),
    dry_run: bool = False,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Admin endpoint to trigger processing of all recurring transactions."""
    task = process_all_recurring_transactions.delay(dry_run=dry_run)
    
    return {
        "task_id": task.id,
        "message": f"{'Dry run' if dry_run else 'Processing'} all recurring transactions in background"
    }

@router.post("/admin/send-all-reminders")
def admin_trigger_all_reminders(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Admin endpoint to trigger sending of all recurring transaction reminders."""
    task = send_recurring_transaction_reminders.delay()
    
    return {
        "task_id": task.id,
        "message": "Sending all recurring transaction reminders in background"
    }
from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.budget_service import BudgetService

router = APIRouter()

@router.post("/", response_model=schemas.Budget)
def create_budget(
    *,
    db: Session = Depends(deps.get_db),
    budget_in: schemas.BudgetCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Create new budget."""
    tenant_id = request.state.tenant.id
    budget_data = budget_in.dict()
    budget_data["user_id"] = current_user.id
    budget_data["tenant_id"] = tenant_id
    
    budget = crud.budget.create(
        db=db, 
        obj_in=schemas.BudgetCreate(**budget_data),
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return budget

@router.get("/", response_model=List[schemas.BudgetWithSummary])
def read_budgets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Retrieve budgets with spending summaries."""
    tenant_id = request.state.tenant.id
    budgets = crud.budget.get_by_user(db, user_id=current_user.id, tenant_id=tenant_id)
    
    # Add spending summaries
    service = BudgetService(db)
    budgets_with_summary = []
    for budget in budgets:
        budget_dict = schemas.Budget.from_orm(budget).dict()
        summary = service.get_budget_summary(budget, current_user.id)
        budget_dict.update(summary)
        budgets_with_summary.append(schemas.BudgetWithSummary(**budget_dict))
    
    return budgets_with_summary

@router.get("/alerts")
def get_budget_alerts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get budget alerts for overspending."""
    tenant_id = request.state.tenant.id
    service = BudgetService(db)
    alerts = service.get_budget_alerts(user_id=current_user.id, tenant_id=tenant_id)
    return alerts
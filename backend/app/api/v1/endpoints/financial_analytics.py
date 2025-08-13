from typing import Any, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.services.financial_analytics_service import FinancialAnalyticsService

router = APIRouter()

@router.get("/dashboard-summary")
def get_dashboard_summary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get financial dashboard summary."""
    tenant_id = request.state.tenant.id
    service = FinancialAnalyticsService(db)
    
    summary = service.get_dashboard_summary(user_id=current_user.id, tenant_id=tenant_id)
    return summary

@router.get("/cash-flow")
def get_cash_flow_analysis(
    *,
    db: Session = Depends(deps.get_db),
    months: int = Query(default=6, le=24),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get cash flow analysis for specified months."""
    tenant_id = request.state.tenant.id
    service = FinancialAnalyticsService(db)
    
    cash_flow = service.get_cash_flow_analysis(
        user_id=current_user.id, 
        tenant_id=tenant_id, 
        months=months
    )
    return cash_flow

@router.get("/spending-trends")
def get_spending_trends(
    *,
    db: Session = Depends(deps.get_db),
    period: str = Query(default="monthly", regex="^(weekly|monthly|quarterly)$"),
    months: int = Query(default=12, le=24),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get spending trends analysis."""
    tenant_id = request.state.tenant.id
    service = FinancialAnalyticsService(db)
    
    trends = service.get_spending_trends(
        user_id=current_user.id,
        tenant_id=tenant_id,
        period=period,
        months=months
    )
    return trends

@router.get("/net-worth")
def get_net_worth_tracking(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get net worth tracking data."""
    tenant_id = request.state.tenant.id
    service = FinancialAnalyticsService(db)
    
    net_worth = service.calculate_net_worth(user_id=current_user.id, tenant_id=tenant_id)
    return net_worth

@router.get("/category-analysis")
def get_category_analysis(
    *,
    db: Session = Depends(deps.get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
    request: Request
) -> Any:
    """Get detailed category spending analysis."""
    tenant_id = request.state.tenant.id
    service = FinancialAnalyticsService(db)
    
    if not date_from:
        date_from = date.today() - timedelta(days=90)
    if not date_to:
        date_to = date.today()
    
    analysis = service.get_category_analysis(
        user_id=current_user.id,
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to
    )
    return analysis
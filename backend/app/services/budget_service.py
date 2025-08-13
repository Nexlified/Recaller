from typing import List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from app import crud
from app.models.budget import Budget

class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def get_budget_summary(self, budget: Budget, user_id: int) -> Dict[str, Any]:
        """Get spending summary for a budget"""
        return crud.budget.get_budget_spending_summary(self.db, budget)

    def get_budget_alerts(self, user_id: int, tenant_id: int) -> List[Dict[str, Any]]:
        """Get budget alerts for overspending"""
        alert_budgets = crud.budget.get_budgets_over_alert_threshold(
            self.db, user_id=user_id, tenant_id=tenant_id
        )
        
        alerts = []
        for budget, summary in alert_budgets:
            alert = {
                "budget_id": budget.id,
                "budget_name": budget.name,
                "budget_amount": budget.budget_amount,
                "spent_amount": summary["spent_amount"],
                "spent_percentage": summary["spent_percentage"],
                "is_over_budget": summary["is_over_budget"],
                "alert_percentage": budget.alert_percentage,
                "days_remaining": summary["days_remaining"],
                "period": budget.period,
                "severity": self._get_alert_severity(summary["spent_percentage"], budget.alert_percentage)
            }
            alerts.append(alert)
        
        return alerts

    def _get_alert_severity(self, spent_percentage: float, alert_percentage: int) -> str:
        """Determine alert severity based on spending percentage"""
        if spent_percentage >= 100:
            return "critical"
        elif spent_percentage >= alert_percentage + 10:
            return "high"
        elif spent_percentage >= alert_percentage:
            return "medium"
        else:
            return "low"
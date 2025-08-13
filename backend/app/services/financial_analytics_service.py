from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app import crud
from app.models.transaction import Transaction
from app.models.financial_account import FinancialAccount

class FinancialAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(self, user_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get financial dashboard summary"""
        today = date.today()
        
        # Current month summary
        current_month_summary = crud.transaction.get_monthly_summary(
            self.db, user_id=user_id, tenant_id=tenant_id, 
            year=today.year, month=today.month
        )
        
        # Previous month summary for comparison
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
            
        prev_month_summary = crud.transaction.get_monthly_summary(
            self.db, user_id=user_id, tenant_id=tenant_id,
            year=prev_year, month=prev_month
        )
        
        # Account balances
        accounts = crud.financial_account.get_financial_accounts_by_user(
            self.db, user_id=user_id, tenant_id=tenant_id, active_only=True
        )
        
        total_balance = sum(float(account.current_balance) for account in accounts)
        
        # Recent transactions
        recent_transactions = crud.transaction.get_transactions_by_user(
            self.db, user_id=user_id, tenant_id=tenant_id, skip=0, limit=5
        )
        
        # Calculate changes
        income_change = self._calculate_percentage_change(
            float(current_month_summary['total_credits']),
            float(prev_month_summary['total_credits'])
        )
        
        expense_change = self._calculate_percentage_change(
            float(current_month_summary['total_debits']),
            float(prev_month_summary['total_debits'])
        )
        
        return {
            "total_balance": total_balance,
            "current_month": {
                "income": current_month_summary['total_credits'],
                "expenses": current_month_summary['total_debits'],
                "net": current_month_summary['net_amount'],
                "transaction_count": current_month_summary['transaction_count']
            },
            "changes": {
                "income_change": income_change,
                "expense_change": expense_change
            },
            "account_count": len(accounts),
            "recent_transactions": recent_transactions
        }

    def get_cash_flow_analysis(self, user_id: int, tenant_id: int, months: int = 6) -> Dict[str, Any]:
        """Get cash flow analysis for specified months"""
        today = date.today()
        cash_flow_data = []
        
        for i in range(months):
            # Calculate the month/year for this iteration
            month_date = today.replace(day=1) - timedelta(days=i*30)
            month = month_date.month
            year = month_date.year
            
            # Get monthly summary
            summary = crud.transaction.get_monthly_summary(
                self.db, user_id=user_id, tenant_id=tenant_id, year=year, month=month
            )
            
            cash_flow_data.append({
                "month": month_date.strftime("%Y-%m"),
                "income": summary['total_credits'],
                "expenses": summary['total_debits'],
                "net_flow": summary['net_amount']
            })
        
        # Reverse to show oldest to newest
        cash_flow_data.reverse()
        
        # Calculate averages
        avg_income = sum(float(item['income']) for item in cash_flow_data) / len(cash_flow_data)
        avg_expenses = sum(float(item['expenses']) for item in cash_flow_data) / len(cash_flow_data)
        avg_net = sum(float(item['net_flow']) for item in cash_flow_data) / len(cash_flow_data)
        
        return {
            "cash_flow": cash_flow_data,
            "averages": {
                "avg_income": avg_income,
                "avg_expenses": avg_expenses,
                "avg_net": avg_net
            }
        }

    def get_spending_trends(self, user_id: int, tenant_id: int, period: str = "monthly", months: int = 12) -> Dict[str, Any]:
        """Get spending trends analysis"""
        today = date.today()
        trends_data = []
        
        # Get category breakdown for trend analysis
        category_breakdown = crud.transaction.get_category_breakdown(
            self.db, user_id=user_id, tenant_id=tenant_id,
            date_from=today - timedelta(days=months*30),
            date_to=today
        )
        
        # Process trend data based on period
        for i in range(months):
            period_start = today.replace(day=1) - timedelta(days=i*30)
            period_end = period_start.replace(day=28) + timedelta(days=4)  # End of month
            
            period_summary = crud.transaction.get_monthly_summary(
                self.db, user_id=user_id, tenant_id=tenant_id,
                year=period_start.year, month=period_start.month
            )
            
            trends_data.append({
                "period": period_start.strftime("%Y-%m"),
                "total_spending": period_summary['total_debits'],
                "transaction_count": period_summary['transaction_count']
            })
        
        trends_data.reverse()
        
        return {
            "trends": trends_data,
            "category_breakdown": category_breakdown
        }

    def calculate_net_worth(self, user_id: int, tenant_id: int) -> Dict[str, Any]:
        """Calculate net worth tracking data"""
        accounts = crud.financial_account.get_financial_accounts_by_user(
            self.db, user_id=user_id, tenant_id=tenant_id, active_only=True
        )
        
        assets = []
        liabilities = []
        
        for account in accounts:
            account_data = {
                "account_name": account.account_name,
                "account_type": account.account_type,
                "balance": float(account.current_balance),
                "currency": account.currency
            }
            
            # Categorize as asset or liability based on account type
            if account.account_type in ['checking', 'savings', 'investment']:
                assets.append(account_data)
            elif account.account_type in ['credit_card', 'loan', 'mortgage']:
                liabilities.append(account_data)
            else:
                # Default to asset for unknown types
                assets.append(account_data)
        
        total_assets = sum(account['balance'] for account in assets)
        total_liabilities = sum(abs(account['balance']) for account in liabilities)  # Absolute value for liabilities
        net_worth = total_assets - total_liabilities
        
        return {
            "net_worth": net_worth,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "assets": assets,
            "liabilities": liabilities,
            "calculation_date": date.today().isoformat()
        }

    def get_category_analysis(self, user_id: int, tenant_id: int, date_from: date, date_to: date) -> Dict[str, Any]:
        """Get detailed category spending analysis"""
        category_breakdown = crud.transaction.get_category_breakdown(
            self.db, user_id=user_id, tenant_id=tenant_id,
            date_from=date_from, date_to=date_to
        )
        
        # Calculate total spending for percentage calculations
        total_spending = sum(float(item.total_amount) for item in category_breakdown)
        
        # Format the breakdown with percentages
        formatted_breakdown = []
        for item in category_breakdown:
            percentage = (float(item.total_amount) / total_spending * 100) if total_spending > 0 else 0
            formatted_breakdown.append({
                "category_id": item.category_id,
                "total_amount": float(item.total_amount),
                "transaction_count": item.transaction_count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by amount descending
        formatted_breakdown.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "total_spending": total_spending,
            "category_breakdown": formatted_breakdown
        }

    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
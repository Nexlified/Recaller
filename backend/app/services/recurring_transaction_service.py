from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction

class RecurringTransactionService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_next_due_date(
        self, 
        start_date: date, 
        frequency: str, 
        interval_count: int = 1
    ) -> date:
        """Calculate next due date based on frequency and interval."""
        if frequency == "daily":
            return start_date + timedelta(days=interval_count)
        elif frequency == "weekly":
            return start_date + timedelta(weeks=interval_count)
        elif frequency == "monthly":
            month = start_date.month + interval_count
            year = start_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                return start_date.replace(year=year, month=month)
            except ValueError:
                # Handle cases like January 31 -> February 31 (doesn't exist)
                # Fall back to last day of month
                if month == 12:
                    next_month = date(year + 1, 1, 1)
                else:
                    next_month = date(year, month + 1, 1)
                return next_month - timedelta(days=1)
        elif frequency == "quarterly":
            return self.calculate_next_due_date(start_date, "monthly", interval_count * 3)
        elif frequency == "yearly":
            try:
                return start_date.replace(year=start_date.year + interval_count)
            except ValueError:
                # Handle leap year edge case (February 29)
                return start_date.replace(year=start_date.year + interval_count, month=2, day=28)
        return start_date

    def calculate_next_due_date_from_recurring(self, recurring: RecurringTransaction) -> date:
        """Calculate next due date from current due date"""
        current_due = recurring.next_due_date or recurring.start_date
        return self.calculate_next_due_date(
            start_date=current_due,
            frequency=recurring.frequency,
            interval_count=recurring.interval_count
        )

    def get_next_occurrence_info(self, recurring: RecurringTransaction) -> Dict[str, Any]:
        """Get next occurrence information for a recurring transaction"""
        next_due = recurring.next_due_date
        if not next_due:
            return {"next_due_date": None, "days_until_due": None, "is_overdue": False}
        
        today = date.today()
        days_until_due = (next_due - today).days
        is_overdue = next_due < today
        
        return {
            "next_due_date": next_due,
            "days_until_due": days_until_due,
            "is_overdue": is_overdue
        }

    def generate_transaction_from_template(
        self, 
        recurring: RecurringTransaction
    ) -> Transaction:
        """Generate a transaction from recurring template."""
        transaction_data = schemas.TransactionCreate(
            type=recurring.type,
            amount=recurring.amount,
            currency=recurring.currency,
            description=recurring.description,
            transaction_date=recurring.next_due_date or date.today(),
            category_id=recurring.category_id,
            subcategory_id=recurring.subcategory_id,
            account_id=recurring.account_id,
            is_recurring=True,
            recurring_template_id=recurring.id,
            extra_data={"auto_generated": True, "recurring_id": recurring.id}
        )
        
        return crud.transaction.create_transaction(
            db=self.db, 
            obj_in=transaction_data,
            user_id=recurring.user_id,
            tenant_id=recurring.tenant_id
        )

    def process_due_recurring_transactions(
        self, 
        user_id: int, 
        tenant_id: int
    ) -> Dict[str, Any]:
        """Process all due recurring transactions for a user."""
        today = date.today()
        due_recurring = crud.recurring_transaction.get_due_reminders(
            self.db, user_id=user_id, tenant_id=tenant_id, reminder_date=today
        )
        
        processed = []
        failed = []
        
        for recurring in due_recurring:
            try:
                # Generate transaction
                transaction = self.generate_transaction_from_template(recurring)
                
                # Update account balance if account is specified
                if transaction.account_id:
                    account = crud.financial_account.get_financial_account_by_user(
                        self.db, account_id=transaction.account_id, user_id=user_id, tenant_id=tenant_id
                    )
                    if account:
                        if transaction.type == "credit":
                            new_balance = float(account.current_balance) + float(transaction.amount)
                        else:
                            new_balance = float(account.current_balance) - float(transaction.amount)
                        crud.financial_account.update_account_balance(
                            self.db, db_obj=account, new_balance=new_balance
                        )
                
                # Update next due date
                next_due = self.calculate_next_due_date_from_recurring(recurring)
                crud.recurring_transaction.update(
                    db=self.db,
                    db_obj=recurring,
                    obj_in=schemas.RecurringTransactionUpdate(next_due_date=next_due)
                )
                
                processed.append({
                    "recurring_id": recurring.id,
                    "transaction_id": transaction.id,
                    "amount": transaction.amount
                })
                
            except Exception as e:
                failed.append({
                    "recurring_id": recurring.id,
                    "error": str(e)
                })
        
        return {
            "processed": len(processed),
            "failed": len(failed),
            "details": processed,
            "errors": failed
        }
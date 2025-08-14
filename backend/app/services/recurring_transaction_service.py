from typing import List, Dict, Any, Optional
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
import logging

from app import crud, schemas, models
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

class RecurringTransactionService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_next_due_date(
        self, 
        start_date: date, 
        frequency: str, 
        interval_count: int = 1,
        occurrence_count: Optional[int] = None
    ) -> Optional[date]:
        """Calculate next due date based on frequency and interval."""
        if frequency == "daily":
            next_date = start_date + timedelta(days=interval_count)
        elif frequency == "weekly":
            next_date = start_date + timedelta(weeks=interval_count)
        elif frequency == "monthly":
            month = start_date.month + interval_count
            year = start_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                next_date = start_date.replace(year=year, month=month)
            except ValueError:
                # Handle case where day doesn't exist in target month (e.g., Jan 31 -> Feb 31)
                last_day_of_month = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year + 1, 1, 1) - timedelta(days=1)
                next_date = start_date.replace(year=year, month=month, day=min(start_date.day, last_day_of_month.day))
        elif frequency == "quarterly":
            return self.calculate_next_due_date(start_date, "monthly", interval_count * 3)
        elif frequency == "yearly":
            try:
                next_date = start_date.replace(year=start_date.year + interval_count)
            except ValueError:
                # Handle leap year edge case (Feb 29)
                next_date = start_date.replace(year=start_date.year + interval_count, month=2, day=28)
        else:
            logger.warning(f"Unknown frequency: {frequency}")
            return start_date
        
        return next_date

    def calculate_next_due_date_from_recurring(self, recurring: RecurringTransaction) -> Optional[date]:
        """Calculate next due date from existing recurring transaction."""
        current_date = recurring.next_due_date or recurring.start_date
        return self.calculate_next_due_date(
            current_date, 
            recurring.frequency, 
            recurring.interval_count
        )

    def get_next_occurrence_info(self, recurring: RecurringTransaction) -> Dict[str, Any]:
        """Get information about the next occurrence of a recurring transaction."""
        next_due = recurring.next_due_date
        if not next_due:
            return {"next_due_date": None, "days_until_due": None, "is_overdue": False}
        
        today = date.today()
        days_until = (next_due - today).days
        
        return {
            "next_due_date": next_due,
            "days_until_due": days_until,
            "is_overdue": days_until < 0,
            "is_due_today": days_until == 0,
            "is_due_soon": 0 <= days_until <= 3
        }

    def generate_transaction_from_template(
        self, 
        recurring: RecurringTransaction,
        override_date: Optional[date] = None
    ) -> Transaction:
        """Generate a transaction from recurring template."""
        transaction_date = override_date or recurring.next_due_date or date.today()
        
        transaction_data = schemas.TransactionCreate(
            type=recurring.type,
            amount=recurring.amount,
            currency=recurring.currency,
            description=f"{recurring.description} (Auto-generated)",
            transaction_date=transaction_date,
            category_id=recurring.category_id,
            subcategory_id=recurring.subcategory_id,
            account_id=recurring.account_id,
            is_recurring=True,
            recurring_template_id=recurring.id,
            extra_data={
                "auto_generated": True, 
                "recurring_id": recurring.id,
                "generated_at": datetime.utcnow().isoformat(),
                "original_due_date": recurring.next_due_date.isoformat() if recurring.next_due_date else None
            }
        )
        
        transaction_dict = transaction_data.dict()
        transaction_dict["user_id"] = recurring.user_id
        transaction_dict["tenant_id"] = recurring.tenant_id
        
        # Create transaction
        transaction = crud.transaction.create(
            db=self.db, 
            obj_in=schemas.TransactionCreate(**transaction_dict)
        )
        
        # Update account balance if account exists
        if transaction.account_id:
            account = crud.financial_account.get(db=self.db, id=transaction.account_id)
            if account and account.user_id == recurring.user_id:
                if transaction.type == "credit":
                    new_balance = account.current_balance + transaction.amount
                else:
                    new_balance = account.current_balance - transaction.amount
                crud.financial_account.update_balance(
                    db=self.db, 
                    db_obj=account, 
                    new_balance=new_balance
                )
        
        # Update recurring transaction statistics
        crud.recurring_transaction.increment_occurrences(db=self.db, recurring_id=recurring.id)
        
        return transaction

    def process_due_recurring_transactions(
        self, 
        user_id: Optional[int] = None, 
        tenant_id: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Process all due recurring transactions."""
        today = date.today()
        
        # Get all due recurring transactions
        if user_id and tenant_id:
            due_recurring = crud.recurring_transaction.get_due_reminders(
                self.db, user_id=user_id, tenant_id=tenant_id, reminder_date=today
            )
        else:
            # Process for all users (background job)
            due_recurring = crud.recurring_transaction.get_all_due(self.db, reminder_date=today)
        
        processed = []
        failed = []
        skipped = []
        
        for recurring in due_recurring:
            try:
                # Check if already processed today
                existing_transaction = crud.transaction.get_by_recurring_and_date(
                    self.db, 
                    recurring_id=recurring.id, 
                    transaction_date=today
                )
                
                if existing_transaction:
                    skipped.append({
                        "recurring_id": recurring.id,
                        "reason": "Already processed today",
                        "existing_transaction_id": existing_transaction.id
                    })
                    continue
                
                # Check if recurring transaction is still active
                if not recurring.is_active:
                    skipped.append({
                        "recurring_id": recurring.id,
                        "reason": "Recurring transaction is inactive"
                    })
                    continue
                
                # Check end date
                if recurring.end_date and today > recurring.end_date:
                    # Deactivate expired recurring transaction
                    crud.recurring_transaction.update(
                        db=self.db,
                        db_obj=recurring,
                        obj_in=schemas.RecurringTransactionUpdate(is_active=False)
                    )
                    skipped.append({
                        "recurring_id": recurring.id,
                        "reason": "Recurring transaction has expired"
                    })
                    continue
                
                # Check max occurrences
                if (hasattr(recurring, 'max_occurrences') and recurring.max_occurrences and 
                    hasattr(recurring, 'occurrence_count') and recurring.occurrence_count and 
                    recurring.occurrence_count >= recurring.max_occurrences):
                    crud.recurring_transaction.update(
                        db=self.db,
                        db_obj=recurring,
                        obj_in=schemas.RecurringTransactionUpdate(is_active=False)
                    )
                    skipped.append({
                        "recurring_id": recurring.id,
                        "reason": "Maximum occurrences reached"
                    })
                    continue
                
                if not dry_run:
                    # Generate transaction
                    transaction = self.generate_transaction_from_template(recurring)
                    
                    # Update next due date
                    next_due = self.calculate_next_due_date_from_recurring(recurring)
                    crud.recurring_transaction.update(
                        db=self.db,
                        db_obj=recurring,
                        obj_in=schemas.RecurringTransactionUpdate(
                            next_due_date=next_due,
                            last_processed_date=today
                        )
                    )
                    
                    processed.append({
                        "recurring_id": recurring.id,
                        "transaction_id": transaction.id,
                        "amount": transaction.amount,
                        "description": transaction.description,
                        "user_id": recurring.user_id,
                        "tenant_id": recurring.tenant_id
                    })
                else:
                    # Dry run - just log what would be processed
                    processed.append({
                        "recurring_id": recurring.id,
                        "amount": recurring.amount,
                        "description": recurring.description,
                        "user_id": recurring.user_id,
                        "tenant_id": recurring.tenant_id,
                        "would_process": True
                    })
                
            except Exception as e:
                logger.error(f"Failed to process recurring transaction {recurring.id}: {str(e)}")
                failed.append({
                    "recurring_id": recurring.id,
                    "error": str(e),
                    "user_id": getattr(recurring, 'user_id', None),
                    "tenant_id": getattr(recurring, 'tenant_id', None)
                })
        
        result = {
            "processed": len(processed),
            "failed": len(failed),
            "skipped": len(skipped),
            "total_due": len(due_recurring),
            "details": processed,
            "errors": failed,
            "skipped_details": skipped,
            "dry_run": dry_run,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Processed recurring transactions: {result}")
        return result

    def get_upcoming_recurring_transactions(
        self, 
        user_id: int, 
        tenant_id: int, 
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming recurring transactions for notifications."""
        end_date = date.today() + timedelta(days=days_ahead)
        
        recurring_transactions = crud.recurring_transaction.get_by_user(
            self.db, user_id=user_id, tenant_id=tenant_id
        )
        
        upcoming = []
        for recurring in recurring_transactions:
            if not recurring.is_active:
                continue
                
            next_info = self.get_next_occurrence_info(recurring)
            if (next_info["next_due_date"] and 
                next_info["next_due_date"] <= end_date and 
                next_info["days_until_due"] >= 0):
                
                upcoming.append({
                    "recurring_id": recurring.id,
                    "description": recurring.description,
                    "amount": recurring.amount,
                    "currency": recurring.currency,
                    "type": recurring.type,
                    "next_due_date": next_info["next_due_date"],
                    "days_until_due": next_info["days_until_due"],
                    "is_due_soon": next_info["is_due_soon"],
                    "category_name": recurring.category.name if recurring.category else None,
                    "account_name": recurring.account.name if recurring.account else None
                })
        
        # Sort by due date
        upcoming.sort(key=lambda x: x["next_due_date"])
        return upcoming
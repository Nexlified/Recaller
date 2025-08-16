from typing import Optional
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.recurring_transaction_service import RecurringTransactionService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "recaller",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Process recurring transactions daily at 6 AM
        'process-recurring-transactions': {
            'task': 'app.services.background_tasks.process_all_recurring_transactions',
            'schedule': crontab(hour=6, minute=0),
        },
        # Send reminders daily at 8 AM
        'send-recurring-reminders': {
            'task': 'app.services.background_tasks.send_recurring_transaction_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        # Health check every hour
        'health-check': {
            'task': 'app.services.background_tasks.health_check',
            'schedule': crontab(minute=0),
        },
        # Process personal reminders daily at 7 AM
        'process-personal-reminders': {
            'task': 'app.services.background_tasks.process_personal_reminders',
            'schedule': crontab(hour=7, minute=0),
        },
    },
)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_all_recurring_transactions(self, dry_run: bool = False):
    """Background task to process all due recurring transactions."""
    try:
        db = SessionLocal()
        service = RecurringTransactionService(db)
        
        result = service.process_due_recurring_transactions(dry_run=dry_run)
        
        logger.info(f"Processed recurring transactions: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process recurring transactions: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_user_recurring_transactions(
    self, 
    user_id: int, 
    tenant_id: int, 
    dry_run: bool = False
):
    """Background task to process recurring transactions for a specific user."""
    try:
        db = SessionLocal()
        service = RecurringTransactionService(db)
        
        result = service.process_due_recurring_transactions(
            user_id=user_id, 
            tenant_id=tenant_id, 
            dry_run=dry_run
        )
        
        logger.info(f"Processed recurring transactions for user {user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process recurring transactions for user {user_id}: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_recurring_transaction_reminders(
    self, 
    user_id: Optional[int] = None, 
    tenant_id: Optional[int] = None
):
    """Background task to send recurring transaction reminders."""
    try:
        db = SessionLocal()
        service = NotificationService(db)
        
        result = service.send_recurring_transaction_reminders(
            user_id=user_id, 
            tenant_id=tenant_id
        )
        
        logger.info(f"Sent recurring transaction reminders: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send recurring transaction reminders: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task
def health_check():
    """Simple health check task."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Background tasks are running"
    }

# Background task management endpoints
@celery_app.task
def get_task_status(task_id: str):
    """Get status of a background task."""
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result,
        "traceback": result.traceback
    }


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_personal_reminders(self, user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    """Background task to process personal reminders and create tasks."""
    try:
        from datetime import date
        from app.crud import personal_reminder, task
        from app.schemas.task import TaskCreate
        from app.models.personal_reminder import PersonalReminder
        
        db = SessionLocal()
        logger.info("Starting personal reminders processing")
        
        today = date.today()
        processed_count = 0
        created_tasks = 0
        
        # Get all users and tenants to process if not specified
        if user_id and tenant_id:
            user_tenant_pairs = [(user_id, tenant_id)]
        else:
            # Get all active users and their tenants
            from app.models.user import User
            users = db.query(User).filter(User.is_active == True).all()
            user_tenant_pairs = [(user.id, user.tenant_id) for user in users]
        
        for user_id, tenant_id in user_tenant_pairs:
            # Get reminders that should trigger today
            triggered_reminders = personal_reminder.get_reminders_for_date(
                db=db,
                user_id=user_id,
                tenant_id=tenant_id,
                target_date=today
            )
            
            for reminder in triggered_reminders:
                # Check if task creation is enabled for this reminder
                notification_methods = reminder.notification_methods or {}
                if not notification_methods.get('task_creation', False):
                    continue
                
                # Calculate the next occurrence date
                from app.crud.personal_reminder import _calculate_next_occurrence
                next_occurrence = _calculate_next_occurrence(reminder, today)
                if not next_occurrence:
                    continue
                
                # Create reminder task title and description
                task_title = f"Reminder: {reminder.title}"
                task_description = f"Personal reminder for {reminder.title}"
                
                if reminder.contact:
                    contact_name = f"{reminder.contact.first_name}"
                    if reminder.contact.last_name:
                        contact_name += f" {reminder.contact.last_name}"
                    if reminder.contact.family_nickname:
                        contact_name += f" ({reminder.contact.family_nickname})"
                    
                    task_description += f" - {contact_name}"
                
                if reminder.reminder_type in ['birthday', 'anniversary']:
                    years_since = next_occurrence.year - reminder.event_date.year
                    if reminder.reminder_type == 'birthday':
                        task_description += f" - Turning {years_since}"
                    else:
                        task_description += f" - {years_since} years"
                
                if reminder.description:
                    task_description += f"\n\n{reminder.description}"
                
                # Create the task
                task_data = TaskCreate(
                    title=task_title,
                    description=task_description,
                    due_date=next_occurrence,
                    priority='high' if reminder.importance_level >= 4 else 'medium',
                    contact_ids=[reminder.contact_id] if reminder.contact_id else []
                )
                
                created_task = task.create_task(
                    db=db,
                    obj_in=task_data,
                    user_id=user_id,
                    tenant_id=tenant_id
                )
                
                if created_task:
                    created_tasks += 1
                    logger.info(f"Created reminder task {created_task.id} for reminder {reminder.id}")
                
                processed_count += 1
        
        result = {
            "processed_reminders": processed_count,
            "created_tasks": created_tasks,
            "processed_date": today.isoformat()
        }
        
        logger.info(f"Personal reminders processing completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process personal reminders: {str(e)}")
        raise
    finally:
        db.close()
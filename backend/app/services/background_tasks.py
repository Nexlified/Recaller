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
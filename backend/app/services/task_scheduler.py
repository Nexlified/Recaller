"""
Task Scheduler Service for Recurring Task Generation

This service automatically generates recurring tasks based on user-defined patterns and lead times.
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import SessionLocal
from app.crud import task_recurrence as crud_task_recurrence
from app.crud import task as crud_task
from app.models.task import TaskRecurrence, Task

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler if it doesn't exist
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TaskSchedulerService:
    """
    Background service for automatically generating recurring tasks.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def generate_recurring_tasks(self):
        """
        Main generation logic that scans for tasks to generate.
        This method is called periodically by the scheduler.
        """
        try:
            logger.info("Starting recurring task generation process")
            
            db: Session = SessionLocal()
            try:
                # Get all recurring task patterns that need generation
                recurrences = self._get_recurrences_due_for_generation(db)
                
                tasks_generated = 0
                for recurrence in recurrences:
                    try:
                        if self._should_generate_task(db, recurrence):
                            generated_task = self._generate_task_instance(db, recurrence)
                            if generated_task:
                                tasks_generated += 1
                                logger.info(f"Generated task instance {generated_task.id} for recurrence {recurrence.id}")
                    except Exception as e:
                        logger.error(f"Error generating task for recurrence {recurrence.id}: {str(e)}")
                        continue
                
                logger.info(f"Recurring task generation completed. Generated {tasks_generated} tasks.")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in recurring task generation process: {str(e)}")
    
    async def cleanup_expired_recurrences(self):
        """
        Clean up recurrences that have ended and no longer need processing.
        """
        try:
            logger.info("Starting cleanup of expired recurrences")
            
            db: Session = SessionLocal()
            try:
                current_date = date.today()
                
                # Find recurrences that have ended
                expired_recurrences = db.query(TaskRecurrence).filter(
                    TaskRecurrence.end_date < current_date
                ).all()
                
                # Check if max occurrences reached
                for recurrence in expired_recurrences:
                    if recurrence.max_occurrences:
                        # Count generated instances
                        generated_count = db.query(Task).filter(
                            Task.parent_task_id == recurrence.task_id
                        ).count()
                        
                        if generated_count >= recurrence.max_occurrences:
                            logger.info(f"Recurrence {recurrence.id} reached max occurrences ({recurrence.max_occurrences})")
                
                logger.info(f"Cleanup completed. Processed {len(expired_recurrences)} expired recurrences.")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in cleanup process: {str(e)}")
    
    def _get_recurrences_due_for_generation(self, db: Session) -> List[TaskRecurrence]:
        """
        Get all recurring task patterns that are due for generation.
        """
        try:
            current_date = date.today()
            
            # Get all active recurrences
            recurrences = db.query(TaskRecurrence).join(Task).filter(
                Task.is_recurring == True,
                # Include recurrences that haven't ended or have no end date
                (TaskRecurrence.end_date.is_(None)) | (TaskRecurrence.end_date >= current_date)
            ).all()
            
            # Filter based on lead time and generation timing
            due_recurrences = []
            for recurrence in recurrences:
                if self._should_generate_task(db, recurrence):
                    due_recurrences.append(recurrence)
            
            return due_recurrences
            
        except Exception as e:
            logger.error(f"Error getting recurrences due for generation: {str(e)}")
            return []
    
    def _should_generate_task(self, db: Session, recurrence: TaskRecurrence) -> bool:
        """
        Check if a new task instance should be generated for this recurrence.
        """
        try:
            current_date = date.today()
            
            # Check if recurrence has ended
            if recurrence.end_date and current_date > recurrence.end_date:
                return False
            
            # Check if max occurrences reached
            if recurrence.max_occurrences:
                generated_count = db.query(Task).filter(
                    Task.parent_task_id == recurrence.task_id
                ).count()
                
                if generated_count >= recurrence.max_occurrences:
                    return False
            
            # Check if we need to generate based on lead time
            next_due_date = self._calculate_next_due_date(recurrence, current_date)
            if not next_due_date:
                return False
            
            # Check if we're within the lead time window
            lead_time_date = current_date + timedelta(days=recurrence.lead_time_days)
            
            # Generate if the next due date is within the lead time window
            should_generate = next_due_date <= lead_time_date
            
            # Also check if we haven't already generated for this period
            if should_generate and recurrence.last_generated_at:
                # Avoid duplicate generation by checking if we've already generated recently
                last_gen_date = recurrence.last_generated_at.date()
                if next_due_date <= last_gen_date:
                    should_generate = False
            
            return should_generate
            
        except Exception as e:
            logger.error(f"Error checking if task should be generated for recurrence {recurrence.id}: {str(e)}")
            return False
    
    def _calculate_next_due_date(self, recurrence: TaskRecurrence, from_date: date) -> Optional[date]:
        """
        Calculate the next due date based on recurrence pattern.
        Uses the existing CRUD function but adds additional logic.
        """
        try:
            # Use existing CRUD function
            next_date = crud_task_recurrence.calculate_next_due_date(recurrence, from_date)
            return next_date
            
        except Exception as e:
            logger.error(f"Error calculating next due date for recurrence {recurrence.id}: {str(e)}")
            return None
    
    def _generate_task_instance(self, db: Session, recurrence: TaskRecurrence) -> Optional[Task]:
        """
        Generate a new task instance from a recurring task.
        """
        try:
            # Get the base task
            base_task = db.query(Task).filter(Task.id == recurrence.task_id).first()
            if not base_task:
                logger.error(f"Base task not found for recurrence {recurrence.id}")
                return None
            
            # Calculate the next due date
            current_date = date.today()
            next_due_date = self._calculate_next_due_date(recurrence, current_date)
            if not next_due_date:
                logger.warning(f"Could not calculate next due date for recurrence {recurrence.id}")
                return None
            
            # Generate the task instance using existing CRUD function
            new_task = crud_task_recurrence.generate_next_task_instance(
                db=db,
                recurrence=recurrence,
                base_task=base_task,
                next_due_date=next_due_date
            )
            
            if new_task:
                # Update the task to set parent_task_id
                new_task.parent_task_id = base_task.id
                
                # Update recurrence tracking fields
                recurrence.last_generated_at = datetime.now()
                recurrence.generation_count += 1
                
                # Calculate and set next generation time
                next_next_due = self._calculate_next_due_date(recurrence, next_due_date)
                if next_next_due:
                    # Set next generation time considering lead time
                    recurrence.next_generation_at = datetime.combine(
                        next_next_due - timedelta(days=recurrence.lead_time_days),
                        datetime.min.time()
                    )
                
                db.add(recurrence)
                db.commit()
                
                logger.info(f"Successfully generated task {new_task.id} from recurrence {recurrence.id}")
                return new_task
            else:
                logger.warning(f"Failed to generate task instance for recurrence {recurrence.id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating task instance for recurrence {recurrence.id}: {str(e)}")
            db.rollback()
            return None
    
    def start(self):
        """
        Start the background scheduler.
        """
        if self.is_running:
            logger.warning("TaskSchedulerService is already running")
            return
        
        try:
            # Schedule recurring task generation every hour
            self.scheduler.add_job(
                self.generate_recurring_tasks,
                IntervalTrigger(hours=1),
                id='generate_recurring_tasks',
                name='Generate Recurring Tasks',
                replace_existing=True
            )
            
            # Schedule cleanup every 6 hours
            self.scheduler.add_job(
                self.cleanup_expired_recurrences,
                IntervalTrigger(hours=6),
                id='cleanup_expired_recurrences',
                name='Cleanup Expired Recurrences',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("TaskSchedulerService started successfully")
            
        except Exception as e:
            logger.error(f"Error starting TaskSchedulerService: {str(e)}")
            raise
    
    def stop(self):
        """
        Stop the background scheduler.
        """
        if not self.is_running:
            logger.warning("TaskSchedulerService is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("TaskSchedulerService stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping TaskSchedulerService: {str(e)}")
            raise
    
    async def manual_generate(self) -> dict:
        """
        Manually trigger task generation for testing/debugging.
        Returns statistics about the generation process.
        """
        try:
            logger.info("Manual task generation triggered")
            
            db: Session = SessionLocal()
            try:
                recurrences = self._get_recurrences_due_for_generation(db)
                
                stats = {
                    "total_recurrences_checked": len(recurrences),
                    "tasks_generated": 0,
                    "errors": 0
                }
                
                for recurrence in recurrences:
                    try:
                        if self._should_generate_task(db, recurrence):
                            generated_task = self._generate_task_instance(db, recurrence)
                            if generated_task:
                                stats["tasks_generated"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error in manual generation for recurrence {recurrence.id}: {str(e)}")
                
                logger.info(f"Manual generation completed: {stats}")
                return stats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in manual task generation: {str(e)}")
            return {"error": str(e)}


# Global instance
task_scheduler_service = TaskSchedulerService()
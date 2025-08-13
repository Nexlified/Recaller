from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, date, timedelta

from app.models.task import TaskRecurrence, Task
from app.schemas.task import TaskRecurrenceCreate, TaskRecurrenceUpdate


def get_task_recurrence(db: Session, recurrence_id: int) -> Optional[TaskRecurrence]:
    """Get a single task recurrence by ID."""
    return db.query(TaskRecurrence).filter(
        TaskRecurrence.id == recurrence_id
    ).first()


def get_by_task(db: Session, *, task_id: int) -> Optional[TaskRecurrence]:
    """Get recurrence pattern for a specific task."""
    return db.query(TaskRecurrence).filter(
        TaskRecurrence.task_id == task_id
    ).first()


def get_tasks_for_generation(db: Session, *, lead_time_days: int = 7) -> List[TaskRecurrence]:
    """Get recurring tasks that need new instances generated."""
    cutoff_date = date.today() + timedelta(days=lead_time_days)
    
    return db.query(TaskRecurrence).options(
        joinedload(TaskRecurrence.task)
    ).filter(
        or_(
            TaskRecurrence.end_date.is_(None),
            TaskRecurrence.end_date >= cutoff_date
        )
    ).all()


def get_recurring_tasks_due_for_generation(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int,
    lead_time_days: int = 7
) -> List[TaskRecurrence]:
    """Get recurring tasks for a specific user that need generation."""
    cutoff_date = date.today() + timedelta(days=lead_time_days)
    
    return db.query(TaskRecurrence).join(Task).filter(
        Task.user_id == user_id,
        Task.tenant_id == tenant_id,
        Task.is_recurring == True,
        or_(
            TaskRecurrence.end_date.is_(None),
            TaskRecurrence.end_date >= cutoff_date
        )
    ).all()


def create_task_recurrence(
    db: Session, 
    *, 
    obj_in: TaskRecurrenceCreate, 
    task_id: int
) -> TaskRecurrence:
    """Create a new task recurrence pattern."""
    db_recurrence = TaskRecurrence(
        **obj_in.model_dump(),
        task_id=task_id
    )
    db.add(db_recurrence)
    db.commit()
    db.refresh(db_recurrence)
    return db_recurrence


def update_task_recurrence(
    db: Session, 
    *, 
    db_obj: TaskRecurrence, 
    obj_in: Union[TaskRecurrenceUpdate, Dict[str, Any]]
) -> TaskRecurrence:
    """Update a task recurrence pattern."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_task_recurrence(db: Session, *, recurrence_id: int) -> Optional[TaskRecurrence]:
    """Delete a task recurrence pattern."""
    recurrence = get_task_recurrence(db, recurrence_id=recurrence_id)
    if recurrence:
        # Also update the parent task to mark as non-recurring
        task = db.query(Task).filter(Task.id == recurrence.task_id).first()
        if task:
            task.is_recurring = False
            db.add(task)
        
        db.delete(recurrence)
        db.commit()
    return recurrence


def calculate_next_due_date(recurrence: TaskRecurrence, current_date: date) -> Optional[date]:
    """Calculate the next due date based on recurrence pattern."""
    if not recurrence or not current_date:
        return None
    
    next_date = current_date
    interval = recurrence.recurrence_interval
    
    if recurrence.recurrence_type == "daily":
        next_date = current_date + timedelta(days=interval)
    
    elif recurrence.recurrence_type == "weekly":
        if recurrence.days_of_week:
            # Handle specific days of week (e.g., "1,3,5" for Mon, Wed, Fri)
            days = [int(d) for d in recurrence.days_of_week.split(',') if d.strip()]
            current_weekday = current_date.weekday()
            
            # Find next occurrence
            for i in range(1, 8):  # Check next 7 days
                check_date = current_date + timedelta(days=i)
                if check_date.weekday() in days:
                    next_date = check_date
                    break
            else:
                # If no match in next 7 days, go to next week
                next_date = current_date + timedelta(weeks=interval)
        else:
            next_date = current_date + timedelta(weeks=interval)
    
    elif recurrence.recurrence_type == "monthly":
        if recurrence.day_of_month:
            # Try to set to specific day of next month
            try:
                if current_date.month == 12:
                    next_date = current_date.replace(
                        year=current_date.year + 1, 
                        month=1, 
                        day=recurrence.day_of_month
                    )
                else:
                    next_date = current_date.replace(
                        month=current_date.month + interval, 
                        day=recurrence.day_of_month
                    )
            except ValueError:
                # Handle cases where day doesn't exist in month (e.g., Feb 30)
                # Fall back to last day of month
                import calendar
                if current_date.month == 12:
                    year = current_date.year + 1
                    month = 1
                else:
                    year = current_date.year
                    month = current_date.month + interval
                
                last_day = calendar.monthrange(year, month)[1]
                next_date = date(year, month, min(recurrence.day_of_month, last_day))
        else:
            # Same day of next month
            if current_date.month + interval > 12:
                next_date = current_date.replace(
                    year=current_date.year + 1,
                    month=(current_date.month + interval) % 12
                )
            else:
                next_date = current_date.replace(month=current_date.month + interval)
    
    elif recurrence.recurrence_type == "yearly":
        next_date = current_date.replace(year=current_date.year + interval)
    
    # Check if we've exceeded the end date
    if recurrence.end_date and next_date > recurrence.end_date:
        return None
    
    return next_date


def should_generate_next_task(
    db: Session, 
    *, 
    recurrence: TaskRecurrence, 
    current_date: date = None
) -> bool:
    """Check if a new task instance should be generated for this recurrence."""
    if not current_date:
        current_date = date.today()
    
    # Check if recurrence has ended
    if recurrence.end_date and current_date > recurrence.end_date:
        return False
    
    # Check if max occurrences reached
    if recurrence.max_occurrences:
        task_count = db.query(func.count(Task.id)).filter(
            Task.id == recurrence.task_id  # This would need to be adjusted for multiple instances
        ).scalar()
        if task_count >= recurrence.max_occurrences:
            return False
    
    # Check lead time
    next_due_date = calculate_next_due_date(recurrence, current_date)
    if not next_due_date:
        return False
    
    lead_time_date = current_date + timedelta(days=recurrence.lead_time_days)
    return next_due_date <= lead_time_date


def generate_next_task_instance(
    db: Session, 
    *, 
    recurrence: TaskRecurrence,
    base_task: Task,
    next_due_date: date
) -> Optional[Task]:
    """Generate the next task instance from a recurring task."""
    # Create new task instance
    new_task = Task(
        tenant_id=base_task.tenant_id,
        user_id=base_task.user_id,
        title=base_task.title,
        description=base_task.description,
        status=base_task.status,  # Start with same status as base
        priority=base_task.priority,
        start_date=datetime.combine(next_due_date, datetime.min.time()) if next_due_date else None,
        due_date=datetime.combine(next_due_date, datetime.min.time()) if next_due_date else None,
        is_recurring=False,  # Individual instances are not recurring
        parent_task_id=base_task.id  # Link to the parent recurring task
    )
    
    db.add(new_task)
    db.flush()
    
    # Copy category assignments
    from app.models.task import TaskCategoryAssignment
    original_categories = db.query(TaskCategoryAssignment).filter(
        TaskCategoryAssignment.task_id == base_task.id
    ).all()
    
    for cat_assignment in original_categories:
        new_assignment = TaskCategoryAssignment(
            task_id=new_task.id,
            category_id=cat_assignment.category_id
        )
        db.add(new_assignment)
    
    # Copy contact associations
    from app.models.task import TaskContact
    original_contacts = db.query(TaskContact).filter(
        TaskContact.task_id == base_task.id
    ).all()
    
    for contact_assignment in original_contacts:
        new_contact = TaskContact(
            task_id=new_task.id,
            contact_id=contact_assignment.contact_id,
            relationship_context=contact_assignment.relationship_context
        )
        db.add(new_contact)
    
    db.commit()
    db.refresh(new_task)
    return new_task


def get_recurrence_statistics(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int
) -> Dict[str, Any]:
    """Get recurrence usage statistics for a user."""
    total_recurring = db.query(Task).filter(
        Task.user_id == user_id,
        Task.tenant_id == tenant_id,
        Task.is_recurring == True
    ).count()
    
    by_type = db.query(
        TaskRecurrence.recurrence_type,
        func.count(TaskRecurrence.id).label('count')
    ).join(Task).filter(
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).group_by(TaskRecurrence.recurrence_type).all()
    
    type_counts = {rec_type: count for rec_type, count in by_type}
    
    return {
        'total_recurring_tasks': total_recurring,
        'by_type': type_counts,
        'daily': type_counts.get('daily', 0),
        'weekly': type_counts.get('weekly', 0),
        'monthly': type_counts.get('monthly', 0),
        'yearly': type_counts.get('yearly', 0),
        'custom': type_counts.get('custom', 0)
    }
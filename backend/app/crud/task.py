from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from app.models.task import Task, TaskContact, TaskRecurrence, TaskCategory, TaskCategoryAssignment
from app.models.contact import Contact
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskRecurrenceCreate, 
    TaskContactCreate, TaskCategoryAssignmentCreate,
    TaskStatusEnum, TaskPriorityEnum
)


def get_task(db: Session, task_id: int, tenant_id: int) -> Optional[Task]:
    """Get a single task by ID with tenant filtering."""
    return db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id
    ).first()


def get_task_with_relations(db: Session, task_id: int, tenant_id: int) -> Optional[Task]:
    """Get a task with all its relationships loaded."""
    return db.query(Task).options(
        joinedload(Task.task_category_assignments).joinedload(TaskCategoryAssignment.category),
        joinedload(Task.task_contacts).joinedload(TaskContact.contact),
        joinedload(Task.task_recurrence)
    ).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id
    ).first()


def get_by_user(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Task]:
    """Get all tasks for a specific user."""
    return db.query(Task).filter(
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def get_by_status(
    db: Session, 
    *, 
    status: str, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get tasks by status for a specific user."""
    return db.query(Task).filter(
        Task.status == status,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def get_by_due_date_range(
    db: Session, 
    *, 
    start_date: date, 
    end_date: date, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get tasks within a due date range."""
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    return db.query(Task).filter(
        Task.due_date >= start_datetime,
        Task.due_date <= end_datetime,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(asc(Task.due_date)).offset(skip).limit(limit).all()


def get_overdue(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get overdue tasks for a user."""
    now = datetime.utcnow()
    return db.query(Task).filter(
        Task.due_date < now,
        Task.status.in_([TaskStatusEnum.PENDING.value, TaskStatusEnum.IN_PROGRESS.value]),
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(asc(Task.due_date)).offset(skip).limit(limit).all()


def search(
    db: Session, 
    *, 
    query: str, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Search tasks by title and description."""
    search_filter = or_(
        Task.title.ilike(f"%{query}%"),
        Task.description.ilike(f"%{query}%")
    )
    
    return db.query(Task).filter(
        search_filter,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def get_by_contact(
    db: Session, 
    *, 
    contact_id: int, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get tasks associated with a specific contact."""
    return db.query(Task).join(TaskContact).filter(
        TaskContact.contact_id == contact_id,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def get_by_category(
    db: Session, 
    *, 
    category_id: int, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get tasks in a specific category."""
    return db.query(Task).join(TaskCategoryAssignment).filter(
        TaskCategoryAssignment.category_id == category_id,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def create_task(
    db: Session, 
    *, 
    obj_in: TaskCreate, 
    user_id: int, 
    tenant_id: int
) -> Task:
    """Create a new task with optional recurrence, categories, and contacts."""
    # Create the task data without relationships
    task_data = obj_in.model_dump(exclude={"category_ids", "contact_ids", "recurrence"})
    
    db_task = Task(
        **task_data,
        user_id=user_id,
        tenant_id=tenant_id,
        is_recurring=obj_in.recurrence is not None
    )
    
    db.add(db_task)
    db.flush()  # Flush to get task ID without committing
    
    # Handle recurrence
    if obj_in.recurrence:
        recurrence_data = obj_in.recurrence.model_dump()
        db_recurrence = TaskRecurrence(
            **recurrence_data,
            task_id=db_task.id
        )
        db.add(db_recurrence)
    
    # Handle category assignments
    if obj_in.category_ids:
        for category_id in obj_in.category_ids:
            assignment = TaskCategoryAssignment(
                task_id=db_task.id,
                category_id=category_id
            )
            db.add(assignment)
    
    # Handle contact associations
    if obj_in.contact_ids:
        for contact_id in obj_in.contact_ids:
            contact_assoc = TaskContact(
                task_id=db_task.id,
                contact_id=contact_id
            )
            db.add(contact_assoc)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session, 
    *, 
    db_obj: Task, 
    obj_in: Union[TaskUpdate, Dict[str, Any]]
) -> Task:
    """Update a task."""
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


def mark_completed(
    db: Session, 
    *, 
    task_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[Task]:
    """Mark a task as completed and set completion timestamp."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if task and task.user_id == user_id:
        task.status = TaskStatusEnum.COMPLETED.value
        task.completed_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)
    return task


def delete_task(db: Session, *, task_id: int, user_id: int, tenant_id: int) -> Optional[Task]:
    """Delete a task if user owns it."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if task and task.user_id == user_id:
        db.delete(task)
        db.commit()
    return task


# Contact association methods
def add_task_contact(
    db: Session, 
    *, 
    task_id: int, 
    contact_id: int, 
    user_id: int, 
    tenant_id: int,
    relationship_context: Optional[str] = None
) -> Optional[TaskContact]:
    """Add a contact to a task."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != user_id:
        return None
    
    # Check if association already exists
    existing = db.query(TaskContact).filter(
        TaskContact.task_id == task_id,
        TaskContact.contact_id == contact_id
    ).first()
    
    if existing:
        return existing
    
    task_contact = TaskContact(
        task_id=task_id,
        contact_id=contact_id,
        relationship_context=relationship_context
    )
    db.add(task_contact)
    db.commit()
    db.refresh(task_contact)
    return task_contact


def remove_task_contact(
    db: Session, 
    *, 
    task_id: int, 
    contact_id: int, 
    user_id: int, 
    tenant_id: int
) -> bool:
    """Remove a contact from a task."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != user_id:
        return False
    
    task_contact = db.query(TaskContact).filter(
        TaskContact.task_id == task_id,
        TaskContact.contact_id == contact_id
    ).first()
    
    if task_contact:
        db.delete(task_contact)
        db.commit()
        return True
    return False


# Category assignment methods
def add_task_category(
    db: Session, 
    *, 
    task_id: int, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[TaskCategoryAssignment]:
    """Add a category to a task."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != user_id:
        return None
    
    # Check if assignment already exists
    existing = db.query(TaskCategoryAssignment).filter(
        TaskCategoryAssignment.task_id == task_id,
        TaskCategoryAssignment.category_id == category_id
    ).first()
    
    if existing:
        return existing
    
    assignment = TaskCategoryAssignment(
        task_id=task_id,
        category_id=category_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def remove_task_category(
    db: Session, 
    *, 
    task_id: int, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> bool:
    """Remove a category from a task."""
    task = get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != user_id:
        return False
    
    assignment = db.query(TaskCategoryAssignment).filter(
        TaskCategoryAssignment.task_id == task_id,
        TaskCategoryAssignment.category_id == category_id
    ).first()
    
    if assignment:
        db.delete(assignment)
        db.commit()
        return True
    return False


# Bulk operations
def bulk_update_status(
    db: Session, 
    *, 
    task_ids: List[int], 
    status: str, 
    user_id: int, 
    tenant_id: int
) -> int:
    """Bulk update status for multiple tasks."""
    updated_count = db.query(Task).filter(
        Task.id.in_(task_ids),
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).update(
        {Task.status: status},
        synchronize_session=False
    )
    db.commit()
    return updated_count


def bulk_update_priority(
    db: Session, 
    *, 
    task_ids: List[int], 
    priority: str, 
    user_id: int, 
    tenant_id: int
) -> int:
    """Bulk update priority for multiple tasks."""
    updated_count = db.query(Task).filter(
        Task.id.in_(task_ids),
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).update(
        {Task.priority: priority},
        synchronize_session=False
    )
    db.commit()
    return updated_count


# Statistics and analytics
def get_task_stats(db: Session, *, user_id: int, tenant_id: int) -> Dict[str, Any]:
    """Get task statistics for a user."""
    base_query = db.query(Task).filter(
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    )
    
    stats = {
        'total': base_query.count(),
        'pending': base_query.filter(Task.status == TaskStatusEnum.PENDING.value).count(),
        'in_progress': base_query.filter(Task.status == TaskStatusEnum.IN_PROGRESS.value).count(),
        'completed': base_query.filter(Task.status == TaskStatusEnum.COMPLETED.value).count(),
        'cancelled': base_query.filter(Task.status == TaskStatusEnum.CANCELLED.value).count(),
        'overdue': base_query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status.in_([TaskStatusEnum.PENDING.value, TaskStatusEnum.IN_PROGRESS.value])
        ).count(),
        'high_priority': base_query.filter(Task.priority == TaskPriorityEnum.HIGH.value).count(),
        'recurring': base_query.filter(Task.is_recurring == True).count()
    }
    
    return stats
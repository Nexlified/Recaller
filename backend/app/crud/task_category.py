from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.task import TaskCategory, TaskCategoryAssignment
from app.schemas.task import TaskCategoryCreate, TaskCategoryUpdate


def get_task_category(db: Session, category_id: int, tenant_id: int) -> Optional[TaskCategory]:
    """Get a single task category by ID with tenant filtering."""
    return db.query(TaskCategory).filter(
        TaskCategory.id == category_id,
        TaskCategory.tenant_id == tenant_id
    ).first()


def get_by_user(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[TaskCategory]:
    """Get all task categories for a specific user."""
    return db.query(TaskCategory).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).order_by(TaskCategory.name).offset(skip).limit(limit).all()


def get_by_name(
    db: Session, 
    *, 
    name: str, 
    user_id: int, 
    tenant_id: int
) -> Optional[TaskCategory]:
    """Get a task category by name for a specific user."""
    return db.query(TaskCategory).filter(
        TaskCategory.name == name,
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).first()


def search_categories(
    db: Session,
    *,
    query: str,
    user_id: int,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[TaskCategory]:
    """Search task categories by name and description."""
    search_filter = or_(
        TaskCategory.name.ilike(f"%{query}%"),
        TaskCategory.description.ilike(f"%{query}%")
    )
    
    return db.query(TaskCategory).filter(
        search_filter,
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).order_by(TaskCategory.name).offset(skip).limit(limit).all()


def create_task_category(
    db: Session, 
    *, 
    obj_in: TaskCategoryCreate, 
    user_id: int, 
    tenant_id: int
) -> TaskCategory:
    """Create a new task category."""
    db_category = TaskCategory(
        **obj_in.model_dump(),
        user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_task_category(
    db: Session, 
    *, 
    db_obj: TaskCategory, 
    obj_in: Union[TaskCategoryUpdate, Dict[str, Any]]
) -> TaskCategory:
    """Update a task category."""
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


def delete_task_category(
    db: Session, 
    *, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> Optional[TaskCategory]:
    """Delete a task category if user owns it."""
    category = get_task_category(db, category_id=category_id, tenant_id=tenant_id)
    if category and category.user_id == user_id:
        db.delete(category)
        db.commit()
    return category


def get_category_task_count(
    db: Session, 
    *, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> int:
    """Get the number of tasks associated with a category."""
    from app.models.task import Task
    
    return db.query(func.count(TaskCategoryAssignment.id)).join(Task).filter(
        TaskCategoryAssignment.category_id == category_id,
        Task.user_id == user_id,
        Task.tenant_id == tenant_id
    ).scalar()


def get_categories_with_task_counts(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get task categories with their task counts."""
    from app.models.task import Task
    
    categories_with_counts = db.query(
        TaskCategory,
        func.count(TaskCategoryAssignment.id).label('task_count')
    ).outerjoin(TaskCategoryAssignment).outerjoin(Task).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).group_by(TaskCategory.id).order_by(TaskCategory.name).offset(skip).limit(limit).all()
    
    result = []
    for category, task_count in categories_with_counts:
        category_dict = {
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'description': category.description,
            'tenant_id': category.tenant_id,
            'user_id': category.user_id,
            'created_at': category.created_at,
            'task_count': task_count or 0
        }
        result.append(category_dict)
    
    return result


def get_popular_categories(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get most popular categories (by task count) for a user."""
    from app.models.task import Task
    
    popular_categories = db.query(
        TaskCategory,
        func.count(TaskCategoryAssignment.id).label('task_count')
    ).outerjoin(TaskCategoryAssignment).outerjoin(Task).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).group_by(TaskCategory.id).order_by(
        desc(func.count(TaskCategoryAssignment.id))
    ).limit(limit).all()
    
    result = []
    for category, task_count in popular_categories:
        if task_count > 0:  # Only include categories with tasks
            category_dict = {
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'description': category.description,
                'task_count': task_count
            }
            result.append(category_dict)
    
    return result


def validate_category_ownership(
    db: Session, 
    *, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> bool:
    """Validate that a user owns a specific category."""
    category = get_task_category(db, category_id=category_id, tenant_id=tenant_id)
    return category is not None and category.user_id == user_id


def can_delete_category(
    db: Session, 
    *, 
    category_id: int, 
    user_id: int, 
    tenant_id: int
) -> bool:
    """Check if a category can be safely deleted (has no associated tasks)."""
    task_count = get_category_task_count(
        db, 
        category_id=category_id, 
        user_id=user_id, 
        tenant_id=tenant_id
    )
    return task_count == 0


def get_category_statistics(
    db: Session, 
    *, 
    user_id: int, 
    tenant_id: int
) -> Dict[str, Any]:
    """Get category usage statistics for a user."""
    from app.models.task import Task
    
    total_categories = db.query(TaskCategory).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).count()
    
    used_categories = db.query(TaskCategory).join(TaskCategoryAssignment).join(Task).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).distinct().count()
    
    avg_tasks_per_category = db.query(
        func.avg(func.count(TaskCategoryAssignment.id))
    ).select_from(TaskCategory).outerjoin(TaskCategoryAssignment).outerjoin(Task).filter(
        TaskCategory.user_id == user_id,
        TaskCategory.tenant_id == tenant_id
    ).group_by(TaskCategory.id).scalar() or 0
    
    return {
        'total_categories': total_categories,
        'used_categories': used_categories,
        'unused_categories': total_categories - used_categories,
        'avg_tasks_per_category': float(avg_tasks_per_category)
    }
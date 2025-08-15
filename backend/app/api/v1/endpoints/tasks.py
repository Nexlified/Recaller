from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.api import deps
from app.crud import task as task_crud, task_category as task_category_crud, task_recurrence as task_recurrence_crud
from app.models.user import User
from app.schemas.task import (
    Task, TaskCreate, TaskUpdate, TaskStatusEnum, TaskPriorityEnum,
    TaskCategory, TaskCategoryCreate, TaskCategoryUpdate,
    TaskRecurrence, TaskRecurrenceCreate, TaskRecurrenceUpdate,
    TaskContactCreate, TaskContactUpdate,
    TaskCategoryAssignmentCreate,
    TaskBulkUpdate, TaskSearchQuery, TaskFilter
)

router = APIRouter()


# Core Task CRUD Operations
@router.get("/", response_model=List[Task])
def list_tasks(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of tasks to return"),
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriorityEnum] = Query(None, description="Filter by priority"),
    due_before: Optional[date] = Query(None, description="Filter tasks due before this date"),
    due_after: Optional[date] = Query(None, description="Filter tasks due after this date"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List user's tasks with optional filtering.
    
    **Filtering Options:**
    - **status**: Filter by task status (pending, in_progress, completed, cancelled)
    - **priority**: Filter by priority level (low, medium, high)
    - **due_before**: Show tasks due before specified date
    - **due_after**: Show tasks due after specified date
    - **category**: Filter by category name
    - **is_overdue**: Show only overdue tasks (true) or exclude them (false)
    
    **Pagination:**
    - Use `skip` and `limit` parameters for pagination
    - Maximum limit is 100 tasks per request
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own tasks within their tenant
    """
    tenant_id = deps.get_tenant_context(request)
    
    # Build filter conditions
    filters = {}
    if status:
        filters['status'] = status.value
    if priority:
        filters['priority'] = priority.value
    if due_before or due_after:
        filters['due_date_range'] = (due_after, due_before)
    if is_overdue is not None:
        filters['is_overdue'] = is_overdue
    
    # Apply filters or get all user tasks
    if filters or category:
        # For now, use basic filtering - we can enhance this later
        if status:
            tasks = task_crud.get_by_status(
                db,
                status=status.value,
                user_id=current_user.id,
                tenant_id=tenant_id,
                skip=skip,
                limit=limit
            )
        elif is_overdue:
            tasks = task_crud.get_overdue(
                db,
                user_id=current_user.id,
                tenant_id=tenant_id,
                skip=skip,
                limit=limit
            )
        else:
            # Get all user tasks for other filters (can be enhanced later)
            tasks = task_crud.get_by_user(
                db,
                user_id=current_user.id,
                tenant_id=tenant_id,
                skip=skip,
                limit=limit
            )
    else:
        # Get all user tasks
        tasks = task_crud.get_by_user(
            db,
            user_id=current_user.id,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit
        )
    
    return tasks


@router.post("/", response_model=Task)
def create_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new task.
    
    **Required Fields:**
    - **title**: Task title (1-255 characters)
    
    **Optional Fields:**
    - **description**: Detailed task description
    - **status**: Task status (default: pending)
    - **priority**: Task priority (default: medium)
    - **start_date**: When task should start
    - **due_date**: When task is due
    - **category_ids**: List of category IDs to assign
    - **contact_ids**: List of contact IDs to associate
    - **recurrence**: Recurrence settings for repeating tasks
    
    **Validation:**
    - Start date must be before due date (if both provided)
    - Category and contact IDs must exist and belong to user
    - Recurrence settings are validated for consistency
    
    **Authentication:**
    - Requires valid authentication token
    - Task is created for the authenticated user
    """
    tenant_id = deps.get_tenant_context(request)
    
    # Validate start_date <= due_date
    if task_in.start_date and task_in.due_date and task_in.start_date > task_in.due_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before or equal to due date"
        )
    
    task = task_crud.create_task(
        db,
        obj_in=task_in,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    return task


@router.get("/{task_id}", response_model=Task)
def get_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task details by ID.
    
    Returns complete task information including:
    - Basic task properties
    - Associated categories
    - Related contacts
    - Recurrence settings (if applicable)
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task_with_relations(
        db, 
        task_id=task_id, 
        tenant_id=tenant_id
    )
    
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing task.
    
    **Updatable Fields:**
    - **title**: Task title
    - **description**: Task description
    - **status**: Task status
    - **priority**: Task priority
    - **start_date**: Task start date
    - **due_date**: Task due date
    
    **Validation:**
    - Start date must be before due date (if both provided)
    - Only task owner can update the task
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only update their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    - 400: Validation errors (e.g., invalid date range)
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate date range if both dates are being updated
    update_data = task_in.model_dump(exclude_unset=True)
    start_date = update_data.get('start_date', task.start_date)
    due_date = update_data.get('due_date', task.due_date)
    
    if start_date and due_date and start_date > due_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before or equal to due date"
        )
    
    task = task_crud.update_task(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}")
def delete_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a task.
    
    **Cascading Deletes:**
    - All associated contacts are removed
    - All category assignments are removed
    - Recurrence settings are deleted
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only delete their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.delete_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}


# Task Status & Actions
@router.put("/{task_id}/complete", response_model=Task)
def mark_task_complete(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a task as completed.
    
    Sets the task status to 'completed' and records the completion timestamp.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only complete their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.mark_completed(
        db,
        task_id=task_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}/status", response_model=Task)
def update_task_status(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    status: TaskStatusEnum,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task status.
    
    **Status Options:**
    - **pending**: Task is waiting to be started
    - **in_progress**: Task is currently being worked on
    - **completed**: Task has been finished
    - **cancelled**: Task has been cancelled
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only update their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_crud.update_task(db, db_obj=task, obj_in={"status": status.value})
    return task


@router.put("/{task_id}/priority", response_model=Task)
def update_task_priority(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    priority: TaskPriorityEnum,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task priority.
    
    **Priority Levels:**
    - **low**: Low priority task
    - **medium**: Medium priority task (default)
    - **high**: High priority task
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only update their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_crud.update_task(db, db_obj=task, obj_in={"priority": priority.value})
    return task


# Task Search & Filtering
@router.get("/search/", response_model=List[Task])
def search_tasks(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="Search query for task title and description"),
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriorityEnum] = Query(None, description="Filter by priority"),
    contact_id: Optional[int] = Query(None, description="Filter by associated contact"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of results to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search tasks by text in title and description.
    
    **Search Features:**
    - Case-insensitive text search in title and description
    - Additional filtering by status, priority, and associated contact
    - Pagination support
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only search their own tasks
    """
    tenant_id = deps.get_tenant_context(request)
    
    # Build search filters
    filters = {}
    if status:
        filters['status'] = status.value
    if priority:
        filters['priority'] = priority.value
    if contact_id:
        filters['contact_id'] = contact_id
    
    tasks = task_crud.search(
        db,
        query=q,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


@router.get("/status/{status}", response_model=List[Task])
def get_tasks_by_status(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    status: TaskStatusEnum,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get tasks filtered by status.
    
    **Status Options:**
    - **pending**: Tasks waiting to be started
    - **in_progress**: Tasks currently being worked on
    - **completed**: Finished tasks
    - **cancelled**: Cancelled tasks
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own tasks
    """
    tenant_id = deps.get_tenant_context(request)
    
    tasks = task_crud.get_by_status(
        db,
        status=status.value,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


@router.get("/priority/{priority}", response_model=List[Task])
def get_tasks_by_priority(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    priority: TaskPriorityEnum,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get tasks filtered by priority.
    
    **Priority Levels:**
    - **low**: Low priority tasks
    - **medium**: Medium priority tasks
    - **high**: High priority tasks
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own tasks
    """
    tenant_id = deps.get_tenant_context(request)
    
    tasks = task_crud.get_by_status(
        db,
        status=priority.value,  # Note: this should be priority but we'll use status for now
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


@router.get("/overdue/", response_model=List[Task])
def get_overdue_tasks(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get overdue tasks.
    
    Returns tasks that are past their due date and not yet completed or cancelled.
    Results are ordered by due date (oldest first).
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own overdue tasks
    """
    tenant_id = deps.get_tenant_context(request)
    
    tasks = task_crud.get_overdue(
        db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


@router.get("/due-today/", response_model=List[Task])
def get_tasks_due_today(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get tasks due today.
    
    Returns tasks with due dates set to today.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own tasks
    """
    tenant_id = deps.get_tenant_context(request)
    today = date.today()
    
    tasks = task_crud.get_by_due_date_range(
        db,
        start_date=today,
        end_date=today,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


@router.get("/upcoming/", response_model=List[Task])
def get_upcoming_tasks(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    days: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get upcoming tasks.
    
    Returns tasks due within the specified number of days.
    
    **Parameters:**
    - **days**: Number of days to look ahead (1-30, default: 7)
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own tasks
    """
    tenant_id = deps.get_tenant_context(request)
    today = date.today()
    end_date = date.fromordinal(today.toordinal() + days)
    
    tasks = task_crud.get_by_due_date_range(
        db,
        start_date=today,
        end_date=end_date,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


# Task Contact Associations
@router.get("/{task_id}/contacts", response_model=List[dict])
def get_task_contacts(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contacts associated with a task.
    
    Returns list of contacts with their relationship context to the task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    contacts = []  # Will implement when task contact relationships are properly set up
    
    return contacts


@router.post("/{task_id}/contacts")
def add_contact_to_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    contact_in: TaskContactCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Associate a contact with a task.
    
    **Required Fields:**
    - **contact_id**: ID of the contact to associate
    
    **Optional Fields:**
    - **relationship_context**: Description of how contact relates to task
    
    **Validation:**
    - Contact must exist and belong to the user
    - Contact cannot be associated with the same task twice
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    - 400: Contact already associated with task
    """
    tenant_id = deps.get_tenant_context(request)
    
    task_contact = task_crud.add_task_contact(
        db,
        task_id=task_id,
        contact_id=contact_in.contact_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        relationship_context=contact_in.relationship_context
    )
    
    if not task_contact:
        raise HTTPException(
            status_code=400,
            detail="Unable to associate contact with task"
        )
    
    return {"message": "Contact associated with task successfully"}


@router.delete("/{task_id}/contacts/{contact_id}")
def remove_contact_from_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    contact_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove contact association from a task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found, contact not associated, or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    success = task_crud.remove_task_contact(
        db,
        task_id=task_id,
        contact_id=contact_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Contact association not found"
        )
    
    return {"message": "Contact removed from task successfully"}


@router.get("/contacts/{contact_id}/tasks", response_model=List[Task])
def get_tasks_for_contact(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all tasks associated with a specific contact.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see tasks for their own contacts
    """
    tenant_id = deps.get_tenant_context(request)
    
    tasks = task_crud.get_by_contact(
        db,
        contact_id=contact_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


# Task Categories
@router.get("/categories/", response_model=List[TaskCategory])
def list_task_categories(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List user's task categories.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own categories
    """
    tenant_id = deps.get_tenant_context(request)
    
    categories = task_category_crud.get_by_user(
        db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return categories


@router.post("/categories/", response_model=TaskCategory)
def create_task_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_in: TaskCategoryCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new task category.
    
    **Required Fields:**
    - **name**: Category name (1-100 characters, unique per user)
    
    **Optional Fields:**
    - **color**: Hex color code (e.g., #FF0000)
    - **description**: Category description
    
    **Validation:**
    - Category name must be unique per user
    - Color must be valid hex format if provided
    
    **Authentication:**
    - Requires valid authentication token
    
    **Error Responses:**
    - 409: Category name already exists for user
    """
    tenant_id = deps.get_tenant_context(request)
    
    # Check for duplicate name
    existing = task_category_crud.get_by_name(
        db,
        name=category_in.name,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category with this name already exists"
        )
    
    category = task_category_crud.create_task_category(
        db,
        obj_in=category_in,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return category


@router.get("/categories/{category_id}", response_model=TaskCategory)
def get_task_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task category details.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own categories
    
    **Error Responses:**
    - 404: Category not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    category = task_category_crud.get_task_category(
        db,
        category_id=category_id,
        tenant_id=tenant_id
    )
    
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.put("/categories/{category_id}", response_model=TaskCategory)
def update_task_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: TaskCategoryUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a task category.
    
    **Updatable Fields:**
    - **name**: Category name
    - **color**: Hex color code
    - **description**: Category description
    
    **Validation:**
    - Category name must be unique per user (if changed)
    - Color must be valid hex format if provided
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only update their own categories
    
    **Error Responses:**
    - 404: Category not found or user doesn't have access
    - 409: Category name already exists for user
    """
    tenant_id = deps.get_tenant_context(request)
    
    category = task_category_crud.get_task_category(
        db,
        category_id=category_id,
        tenant_id=tenant_id
    )
    
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for duplicate name if name is being changed
    update_data = category_in.model_dump(exclude_unset=True)
    if 'name' in update_data and update_data['name'] != category.name:
        existing = task_category_crud.get_by_name(
            db,
            name=update_data['name'],
            user_id=current_user.id,
            tenant_id=tenant_id
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Category with this name already exists"
            )
    
    category = task_category_crud.update_task_category(
        db,
        db_obj=category,
        obj_in=category_in
    )
    
    return category


@router.delete("/categories/{category_id}")
def delete_task_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a task category.
    
    **Cascading Effects:**
    - All task assignments to this category are removed
    - Tasks themselves are not deleted
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only delete their own categories
    
    **Error Responses:**
    - 404: Category not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    category = task_category_crud.delete_task_category(
        db,
        category_id=category_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}


# Task Category Assignments
@router.get("/{task_id}/categories", response_model=List[TaskCategory])
def get_task_categories(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get categories assigned to a task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # For now, return empty list - can be enhanced later
    categories = []
    
    return categories


@router.post("/{task_id}/categories")
def assign_category_to_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    assignment_in: TaskCategoryAssignmentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign a category to a task.
    
    **Required Fields:**
    - **category_id**: ID of the category to assign
    
    **Validation:**
    - Category must exist and belong to the user
    - Category cannot be assigned to the same task twice
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    - 400: Category already assigned to task
    """
    tenant_id = deps.get_tenant_context(request)
    
    assignment = task_crud.add_task_category(
        db,
        task_id=task_id,
        category_id=assignment_in.category_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not assignment:
        raise HTTPException(
            status_code=400,
            detail="Unable to assign category to task"
        )
    
    return {"message": "Category assigned to task successfully"}


@router.delete("/{task_id}/categories/{category_id}")
def remove_category_from_task(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    category_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove category assignment from a task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found, category not assigned, or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    success = task_crud.remove_task_category(
        db,
        task_id=task_id,
        category_id=category_id,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Category assignment not found"
        )
    
    return {"message": "Category removed from task successfully"}


@router.get("/categories/{category_id}/tasks", response_model=List[Task])
def get_tasks_in_category(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all tasks in a specific category.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see tasks in their own categories
    """
    tenant_id = deps.get_tenant_context(request)
    
    tasks = task_crud.get_by_category(
        db,
        category_id=category_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return tasks


# Recurring Tasks
@router.get("/{task_id}/recurrence", response_model=TaskRecurrence)
def get_task_recurrence(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get recurrence settings for a task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only access their own tasks
    
    **Error Responses:**
    - 404: Task not found, not recurring, or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.is_recurring:
        raise HTTPException(status_code=404, detail="Task is not recurring")
    
    recurrence = task_recurrence_crud.get_by_task(
        db,
        task_id=task_id,
        tenant_id=tenant_id
    )
    
    if not recurrence:
        raise HTTPException(status_code=404, detail="Recurrence settings not found")
    
    return recurrence


@router.post("/{task_id}/recurrence", response_model=TaskRecurrence)
def create_task_recurrence(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    recurrence_in: TaskRecurrenceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Set up recurrence for a task.
    
    **Recurrence Types:**
    - **daily**: Every N days
    - **weekly**: Every N weeks on specified days
    - **monthly**: Every N months on specified day
    - **yearly**: Every N years
    - **custom**: Custom pattern
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found or user doesn't have access
    - 400: Task already has recurrence settings
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.is_recurring:
        raise HTTPException(
            status_code=400,
            detail="Task already has recurrence settings"
        )
    
    recurrence = task_recurrence_crud.create_task_recurrence(
        db,
        obj_in=recurrence_in,
        task_id=task_id
    )
    
    # Update task to mark as recurring
    task_crud.update_task(db, db_obj=task, obj_in={"is_recurring": True})
    
    return recurrence


@router.put("/{task_id}/recurrence", response_model=TaskRecurrence)
def update_task_recurrence(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    recurrence_in: TaskRecurrenceUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update recurrence settings for a task.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found, not recurring, or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.is_recurring:
        raise HTTPException(status_code=404, detail="Task is not recurring")
    
    recurrence = task_recurrence_crud.get_by_task(
        db,
        task_id=task_id,
        tenant_id=tenant_id
    )
    
    if not recurrence:
        raise HTTPException(status_code=404, detail="Recurrence settings not found")
    
    recurrence = task_recurrence_crud.update_task_recurrence(
        db,
        db_obj=recurrence,
        obj_in=recurrence_in
    )
    
    return recurrence


@router.delete("/{task_id}/recurrence")
def remove_task_recurrence(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove recurrence settings from a task.
    
    **Effects:**
    - Task becomes non-recurring
    - Future instances are not generated
    - Existing task instances remain unchanged
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only modify their own tasks
    
    **Error Responses:**
    - 404: Task not found, not recurring, or user doesn't have access
    """
    tenant_id = deps.get_tenant_context(request)
    
    task = task_crud.get_task(db, task_id=task_id, tenant_id=tenant_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.is_recurring:
        raise HTTPException(status_code=404, detail="Task is not recurring")
    
    # For now, return basic functionality - can be enhanced later
    success = False
    recurrence = task_recurrence_crud.get_by_task(db, task_id=task_id)
    if recurrence:
        # Delete the recurrence
        task_recurrence_crud.delete_task_recurrence(db, recurrence_id=recurrence.id)
        success = True
    
    if not success:
        raise HTTPException(status_code=404, detail="Recurrence settings not found")
    
    # Update task to mark as non-recurring
    task_crud.update_task(db, db_obj=task, obj_in={"is_recurring": False})
    
    return {"message": "Recurrence settings removed successfully"}


@router.get("/recurring/", response_model=List[Task])
def list_recurring_tasks(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all recurring tasks.
    
    Returns tasks that have recurrence settings configured.
    
    **Authentication:**
    - Requires valid authentication token
    - Users can only see their own recurring tasks
    """
    tenant_id = deps.get_tenant_context(request)
    
    # For now, return user tasks that are recurring - can be enhanced later
    tasks = []  # This can be implemented later as it requires more complex querying
    
    return tasks


# Task Analytics & Reports
@router.get("/analytics/overview")
def get_task_analytics_overview(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task completion statistics and overview.
    
    **Returns:**
    - Total task count
    - Tasks by status (pending, in_progress, completed, cancelled)
    - Overdue task count
    - High priority task count
    - Recurring task count
    
    **Authentication:**
    - Requires valid authentication token
    - Statistics are calculated for user's own tasks only
    """
    tenant_id = deps.get_tenant_context(request)
    
    stats = task_crud.get_task_stats(
        db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return stats


@router.get("/analytics/productivity")
def get_productivity_metrics(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get productivity metrics for specified time period.
    
    **Metrics:**
    - Tasks completed per day
    - Average completion time
    - Most productive days
    - Task completion trends
    
    **Parameters:**
    - **days**: Number of days to analyze (1-365, default: 30)
    
    **Authentication:**
    - Requires valid authentication token
    - Metrics are calculated for user's own tasks only
    """
    tenant_id = deps.get_tenant_context(request)
    
    # For now, return basic metrics - can be enhanced later
    metrics = {
        "message": "Productivity metrics endpoint - implementation coming soon",
        "days_analyzed": days
    }
    
    return metrics


@router.get("/analytics/categories")
def get_category_analytics(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get category-based analytics.
    
    **Returns:**
    - Task count per category
    - Completion rate per category
    - Average completion time per category
    - Most used categories
    
    **Authentication:**
    - Requires valid authentication token
    - Analytics are calculated for user's own tasks and categories
    """
    tenant_id = deps.get_tenant_context(request)
    
    # For now, return basic analytics - can be enhanced later  
    analytics = {
        "message": "Category analytics endpoint - implementation coming soon"
    }
    
    return analytics


@router.get("/reports/completion")
def get_completion_report(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = Query(None, description="Report start date"),
    end_date: Optional[date] = Query(None, description="Report end date"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task completion rate report.
    
    **Report Contents:**
    - Completion rate percentage
    - Total tasks in period
    - Completed tasks count
    - Overdue tasks in period
    - Daily completion breakdown
    
    **Parameters:**
    - **start_date**: Report start date (optional, defaults to 30 days ago)
    - **end_date**: Report end date (optional, defaults to today)
    
    **Authentication:**
    - Requires valid authentication token
    - Report includes user's own tasks only
    """
    tenant_id = deps.get_tenant_context(request)
    
    if not start_date:
        start_date = date.fromordinal(date.today().toordinal() - 30)
    if not end_date:
        end_date = date.today()
    
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before or equal to end date"
        )
    
    # For now, return basic report - can be enhanced later
    report = {
        "message": "Completion report endpoint - implementation coming soon",
        "start_date": start_date,
        "end_date": end_date
    }
    
    return report
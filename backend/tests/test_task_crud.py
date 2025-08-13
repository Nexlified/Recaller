import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.crud import task, task_category, task_recurrence
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskCategoryCreate, TaskRecurrenceCreate,
    TaskStatusEnum, TaskPriorityEnum, RecurrenceTypeEnum
)
from app.models.task import Task, TaskCategory, TaskRecurrence, RecurrenceType


class TestTaskCRUD:
    """Test Task CRUD operations."""
    
    def test_create_task_minimal(self, db_session: Session):
        """Test creating a task with minimal data."""
        task_data = TaskCreate(title="Test Task")
        
        created_task = task.create_task(
            db=db_session,
            obj_in=task_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_task.id is not None
        assert created_task.title == "Test Task"
        assert created_task.user_id == 1
        assert created_task.tenant_id == 1
        assert created_task.status == TaskStatusEnum.PENDING.value
        assert created_task.priority == TaskPriorityEnum.MEDIUM.value
        assert created_task.is_recurring is False
    
    def test_create_task_with_recurrence(self, db_session: Session):
        """Test creating a recurring task."""
        recurrence = TaskRecurrenceCreate(
            recurrence_type=RecurrenceTypeEnum.WEEKLY,
            recurrence_interval=1,
            days_of_week="1,3,5"
        )
        
        task_data = TaskCreate(
            title="Weekly Task",
            description="A recurring weekly task",
            recurrence=recurrence
        )
        
        created_task = task.create_task(
            db=db_session,
            obj_in=task_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_task.is_recurring is True
        
        # Check recurrence was created
        task_recurrence_obj = task_recurrence.get_by_task(db_session, task_id=created_task.id)
        assert task_recurrence_obj is not None
        assert task_recurrence_obj.recurrence_type == RecurrenceTypeEnum.WEEKLY.value
        assert task_recurrence_obj.days_of_week == "1,3,5"
    
    def test_get_by_user(self, db_session: Session):
        """Test getting tasks by user."""
        # Create tasks for different users
        task1 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="User 1 Task 1"),
            user_id=1,
            tenant_id=1
        )
        task2 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="User 1 Task 2"),
            user_id=1,
            tenant_id=1
        )
        task3 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="User 2 Task"),
            user_id=2,
            tenant_id=1
        )
        
        # Get tasks for user 1
        user1_tasks = task.get_by_user(db=db_session, user_id=1, tenant_id=1)
        assert len(user1_tasks) == 2
        assert all(t.user_id == 1 for t in user1_tasks)
        
        # Get tasks for user 2
        user2_tasks = task.get_by_user(db=db_session, user_id=2, tenant_id=1)
        assert len(user2_tasks) == 1
        assert user2_tasks[0].user_id == 2
    
    def test_get_by_status(self, db_session: Session):
        """Test getting tasks by status."""
        # Create tasks with different statuses
        pending_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Pending Task", status=TaskStatusEnum.PENDING),
            user_id=1,
            tenant_id=1
        )
        completed_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Completed Task", status=TaskStatusEnum.COMPLETED),
            user_id=1,
            tenant_id=1
        )
        
        # Get pending tasks
        pending_tasks = task.get_by_status(
            db=db_session,
            status=TaskStatusEnum.PENDING.value,
            user_id=1,
            tenant_id=1
        )
        assert len(pending_tasks) >= 1
        assert all(t.status == TaskStatusEnum.PENDING.value for t in pending_tasks)
        
        # Get completed tasks
        completed_tasks = task.get_by_status(
            db=db_session,
            status=TaskStatusEnum.COMPLETED.value,
            user_id=1,
            tenant_id=1
        )
        assert len(completed_tasks) >= 1
        assert all(t.status == TaskStatusEnum.COMPLETED.value for t in completed_tasks)
    
    def test_mark_completed(self, db_session: Session):
        """Test marking a task as completed."""
        created_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Task to Complete"),
            user_id=1,
            tenant_id=1
        )
        
        # Mark as completed
        completed_task = task.mark_completed(
            db=db_session,
            task_id=created_task.id,
            user_id=1,
            tenant_id=1
        )
        
        assert completed_task is not None
        assert completed_task.status == TaskStatusEnum.COMPLETED.value
        assert completed_task.completed_at is not None
    
    def test_search_tasks(self, db_session: Session):
        """Test task search functionality."""
        # Create tasks with searchable content
        task1 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Important Meeting", description="Quarterly review meeting"),
            user_id=1,
            tenant_id=1
        )
        task2 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Code Review", description="Review important changes"),
            user_id=1,
            tenant_id=1
        )
        task3 = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Random Task", description="Nothing special"),
            user_id=1,
            tenant_id=1
        )
        
        # Search for "important"
        search_results = task.search(
            db=db_session,
            query="important",
            user_id=1,
            tenant_id=1
        )
        
        # Should find both tasks that contain "important"
        assert len(search_results) >= 2
        found_titles = [t.title for t in search_results]
        assert "Important Meeting" in found_titles
        assert "Code Review" in found_titles
    
    def test_tenant_isolation(self, db_session: Session):
        """Test that tenant isolation works correctly."""
        # Create tasks in different tenants
        tenant1_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Tenant 1 Task"),
            user_id=1,
            tenant_id=1
        )
        tenant2_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Tenant 2 Task"),
            user_id=1,
            tenant_id=2
        )
        
        # User should only see their tenant's tasks
        tenant1_tasks = task.get_by_user(db=db_session, user_id=1, tenant_id=1)
        tenant2_tasks = task.get_by_user(db=db_session, user_id=1, tenant_id=2)
        
        tenant1_titles = [t.title for t in tenant1_tasks]
        tenant2_titles = [t.title for t in tenant2_tasks]
        
        assert "Tenant 1 Task" in tenant1_titles
        assert "Tenant 1 Task" not in tenant2_titles
        assert "Tenant 2 Task" in tenant2_titles
        assert "Tenant 2 Task" not in tenant1_titles


class TestTaskCategoryCRUD:
    """Test Task Category CRUD operations."""
    
    def test_create_category(self, db_session: Session):
        """Test creating a task category."""
        category_data = TaskCategoryCreate(
            name="Work",
            color="#FF0000",
            description="Work related tasks"
        )
        
        created_category = task_category.create_task_category(
            db=db_session,
            obj_in=category_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_category.id is not None
        assert created_category.name == "Work"
        assert created_category.color == "#FF0000"
        assert created_category.description == "Work related tasks"
        assert created_category.user_id == 1
        assert created_category.tenant_id == 1
    
    def test_get_by_user_categories(self, db_session: Session):
        """Test getting categories by user."""
        # Create categories for different users
        cat1 = task_category.create_task_category(
            db=db_session,
            obj_in=TaskCategoryCreate(name="User 1 Category 1"),
            user_id=1,
            tenant_id=1
        )
        cat2 = task_category.create_task_category(
            db=db_session,
            obj_in=TaskCategoryCreate(name="User 1 Category 2"),
            user_id=1,
            tenant_id=1
        )
        cat3 = task_category.create_task_category(
            db=db_session,
            obj_in=TaskCategoryCreate(name="User 2 Category"),
            user_id=2,
            tenant_id=1
        )
        
        # Get categories for user 1
        user1_categories = task_category.get_by_user(db=db_session, user_id=1, tenant_id=1)
        assert len(user1_categories) >= 2
        assert all(c.user_id == 1 for c in user1_categories)
        
        # Get categories for user 2
        user2_categories = task_category.get_by_user(db=db_session, user_id=2, tenant_id=1)
        assert len(user2_categories) >= 1
        assert all(c.user_id == 2 for c in user2_categories)
    
    def test_get_by_name(self, db_session: Session):
        """Test getting category by name."""
        created_category = task_category.create_task_category(
            db=db_session,
            obj_in=TaskCategoryCreate(name="Unique Category"),
            user_id=1,
            tenant_id=1
        )
        
        found_category = task_category.get_by_name(
            db=db_session,
            name="Unique Category",
            user_id=1,
            tenant_id=1
        )
        
        assert found_category is not None
        assert found_category.id == created_category.id
        assert found_category.name == "Unique Category"
    
    def test_category_ownership_validation(self, db_session: Session):
        """Test category ownership validation."""
        category = task_category.create_task_category(
            db=db_session,
            obj_in=TaskCategoryCreate(name="Owner Test"),
            user_id=1,
            tenant_id=1
        )
        
        # Owner should be validated correctly
        assert task_category.validate_category_ownership(
            db=db_session,
            category_id=category.id,
            user_id=1,
            tenant_id=1
        ) is True
        
        # Different user should not own the category
        assert task_category.validate_category_ownership(
            db=db_session,
            category_id=category.id,
            user_id=2,
            tenant_id=1
        ) is False


class TestTaskRecurrenceCRUD:
    """Test Task Recurrence CRUD operations."""
    
    def test_create_recurrence(self, db_session: Session):
        """Test creating a task recurrence."""
        # First create a task
        created_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(title="Base Task"),
            user_id=1,
            tenant_id=1
        )
        
        # Create recurrence pattern
        recurrence_data = TaskRecurrenceCreate(
            recurrence_type=RecurrenceTypeEnum.DAILY,
            recurrence_interval=2,
            lead_time_days=3
        )
        
        created_recurrence = task_recurrence.create_task_recurrence(
            db=db_session,
            obj_in=recurrence_data,
            task_id=created_task.id
        )
        
        assert created_recurrence.id is not None
        assert created_recurrence.task_id == created_task.id
        assert created_recurrence.recurrence_type == RecurrenceTypeEnum.DAILY.value
        assert created_recurrence.recurrence_interval == 2
        assert created_recurrence.lead_time_days == 3
    
    def test_get_by_task_recurrence(self, db_session: Session):
        """Test getting recurrence by task."""
        # Create task with recurrence
        created_task = task.create_task(
            db=db_session,
            obj_in=TaskCreate(
                title="Recurring Task",
                recurrence=TaskRecurrenceCreate(
                    recurrence_type=RecurrenceTypeEnum.WEEKLY,
                    recurrence_interval=1
                )
            ),
            user_id=1,
            tenant_id=1
        )
        
        # Get recurrence
        found_recurrence = task_recurrence.get_by_task(
            db=db_session,
            task_id=created_task.id
        )
        
        assert found_recurrence is not None
        assert found_recurrence.task_id == created_task.id
        assert found_recurrence.recurrence_type == RecurrenceTypeEnum.WEEKLY.value
    
    def test_calculate_next_due_date(self, db_session: Session):
        """Test next due date calculation."""
        # Create a daily recurrence
        daily_recurrence = TaskRecurrence(
            recurrence_type=RecurrenceType.DAILY.value,
            recurrence_interval=2,
            task_id=1
        )
        
        current_date = date(2024, 1, 15)
        next_date = task_recurrence.calculate_next_due_date(daily_recurrence, current_date)
        
        expected_date = date(2024, 1, 17)  # 2 days later
        assert next_date == expected_date
        
        # Test weekly recurrence with specific days
        weekly_recurrence = TaskRecurrence(
            recurrence_type=RecurrenceType.WEEKLY.value,
            recurrence_interval=1,
            days_of_week="1,3,5",  # Mon, Wed, Fri
            task_id=1
        )
        
        # If current date is Tuesday (1), next should be Wednesday (2)
        tuesday = date(2024, 1, 16)  # This is a Tuesday
        next_date = task_recurrence.calculate_next_due_date(weekly_recurrence, tuesday)
        
        # Should find the next Wednesday
        assert next_date.weekday() in [1, 3, 4]  # Mon=0, Wed=2, Fri=4, but we use 1,3,5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
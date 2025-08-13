import pytest
from datetime import datetime, date
from app.schemas.task import (
    TaskCreate, TaskUpdate, Task,
    TaskCategoryCreate, TaskCategory,
    TaskRecurrenceCreate, TaskRecurrence,
    TaskStatusEnum, TaskPriorityEnum, RecurrenceTypeEnum
)


class TestTaskSchemas:
    """Test task schema validation and functionality."""
    
    def test_task_create_minimal(self):
        """Test creating a task with minimal data."""
        task_data = {
            "title": "Test Task"
        }
        task = TaskCreate(**task_data)
        assert task.title == "Test Task"
        assert task.status == TaskStatusEnum.PENDING
        assert task.priority == TaskPriorityEnum.MEDIUM
        assert task.category_ids == []
        assert task.contact_ids == []
    
    def test_task_create_with_all_fields(self):
        """Test creating a task with all fields."""
        task_data = {
            "title": "Complete Project",
            "description": "Finish the important project",
            "status": TaskStatusEnum.IN_PROGRESS,
            "priority": TaskPriorityEnum.HIGH,
            "start_date": datetime(2024, 1, 1),
            "due_date": datetime(2024, 1, 31),
            "category_ids": [1, 2],
            "contact_ids": [3, 4]
        }
        task = TaskCreate(**task_data)
        assert task.title == "Complete Project"
        assert task.status == TaskStatusEnum.IN_PROGRESS
        assert task.priority == TaskPriorityEnum.HIGH
        assert len(task.category_ids) == 2
        assert len(task.contact_ids) == 2
    
    def test_task_status_enum_validation(self):
        """Test that task status is properly validated."""
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        for status in valid_statuses:
            task = TaskCreate(title="Test", status=status)
            assert task.status == status
    
    def test_task_priority_enum_validation(self):
        """Test that task priority is properly validated."""
        valid_priorities = ["low", "medium", "high"]
        for priority in valid_priorities:
            task = TaskCreate(title="Test", priority=priority)
            assert task.priority == priority
    
    def test_task_update_partial(self):
        """Test updating task with partial data."""
        update_data = {
            "title": "Updated Title",
            "status": TaskStatusEnum.COMPLETED
        }
        task_update = TaskUpdate(**update_data)
        assert task_update.title == "Updated Title"
        assert task_update.status == TaskStatusEnum.COMPLETED
        assert task_update.description is None  # Not updated


class TestTaskCategorySchemas:
    """Test task category schema validation."""
    
    def test_category_create_minimal(self):
        """Test creating a category with minimal data."""
        category_data = {"name": "Work"}
        category = TaskCategoryCreate(**category_data)
        assert category.name == "Work"
        assert category.color is None
        assert category.description is None
    
    def test_category_create_with_color(self):
        """Test creating a category with valid color."""
        category_data = {
            "name": "Personal",
            "color": "#FF0000",
            "description": "Personal tasks"
        }
        category = TaskCategoryCreate(**category_data)
        assert category.name == "Personal"
        assert category.color == "#FF0000"
        assert category.description == "Personal tasks"
    
    def test_category_color_validation(self):
        """Test that invalid color formats are rejected."""
        with pytest.raises(ValueError):
            TaskCategoryCreate(name="Test", color="invalid-color")
        
        with pytest.raises(ValueError):
            TaskCategoryCreate(name="Test", color="#GGG")
    
    def test_category_name_validation(self):
        """Test category name validation."""
        with pytest.raises(ValueError):
            TaskCategoryCreate(name="")  # Empty name
        
        with pytest.raises(ValueError):
            TaskCategoryCreate(name="a" * 101)  # Too long


class TestTaskRecurrenceSchemas:
    """Test task recurrence schema validation."""
    
    def test_recurrence_create_daily(self):
        """Test creating daily recurrence."""
        recurrence_data = {
            "recurrence_type": RecurrenceTypeEnum.DAILY,
            "recurrence_interval": 2
        }
        recurrence = TaskRecurrenceCreate(**recurrence_data)
        assert recurrence.recurrence_type == RecurrenceTypeEnum.DAILY
        assert recurrence.recurrence_interval == 2
        assert recurrence.lead_time_days == 0
    
    def test_recurrence_create_weekly(self):
        """Test creating weekly recurrence with specific days."""
        recurrence_data = {
            "recurrence_type": RecurrenceTypeEnum.WEEKLY,
            "recurrence_interval": 1,
            "days_of_week": "1,3,5",  # Mon, Wed, Fri
            "lead_time_days": 3
        }
        recurrence = TaskRecurrenceCreate(**recurrence_data)
        assert recurrence.recurrence_type == RecurrenceTypeEnum.WEEKLY
        assert recurrence.days_of_week == "1,3,5"
        assert recurrence.lead_time_days == 3
    
    def test_recurrence_create_monthly(self):
        """Test creating monthly recurrence."""
        recurrence_data = {
            "recurrence_type": RecurrenceTypeEnum.MONTHLY,
            "recurrence_interval": 1,
            "day_of_month": 15,
            "end_date": date(2024, 12, 31)
        }
        recurrence = TaskRecurrenceCreate(**recurrence_data)
        assert recurrence.recurrence_type == RecurrenceTypeEnum.MONTHLY
        assert recurrence.day_of_month == 15
        assert recurrence.end_date == date(2024, 12, 31)
    
    def test_recurrence_interval_validation(self):
        """Test that recurrence interval is properly validated."""
        with pytest.raises(ValueError):
            TaskRecurrenceCreate(
                recurrence_type=RecurrenceTypeEnum.DAILY,
                recurrence_interval=0  # Must be >= 1
            )
    
    def test_day_of_month_validation(self):
        """Test day of month validation."""
        with pytest.raises(ValueError):
            TaskRecurrenceCreate(
                recurrence_type=RecurrenceTypeEnum.MONTHLY,
                day_of_month=0  # Must be >= 1
            )
        
        with pytest.raises(ValueError):
            TaskRecurrenceCreate(
                recurrence_type=RecurrenceTypeEnum.MONTHLY,
                day_of_month=32  # Must be <= 31
            )


class TestTaskSchemaIntegration:
    """Test integration between different task schemas."""
    
    def test_task_with_recurrence(self):
        """Test creating a task with recurrence pattern."""
        recurrence = TaskRecurrenceCreate(
            recurrence_type=RecurrenceTypeEnum.WEEKLY,
            recurrence_interval=1,
            days_of_week="1,3,5"
        )
        
        task_data = {
            "title": "Weekly Meeting",
            "description": "Team standup meeting",
            "recurrence": recurrence
        }
        
        task = TaskCreate(**task_data)
        assert task.title == "Weekly Meeting"
        assert task.recurrence is not None
        assert task.recurrence.recurrence_type == RecurrenceTypeEnum.WEEKLY
    
    def test_task_full_model_schema(self):
        """Test the full Task schema with all relationships."""
        # This would typically be populated by the ORM
        task_data = {
            "id": 1,
            "tenant_id": 1,
            "user_id": 1,
            "title": "Test Task",
            "description": "A test task",
            "status": TaskStatusEnum.PENDING,
            "priority": TaskPriorityEnum.MEDIUM,
            "is_recurring": False,
            "created_at": datetime.now(),
            "categories": [],
            "contacts": []
        }
        
        task = Task(**task_data)
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.is_recurring is False
        assert isinstance(task.categories, list)
        assert isinstance(task.contacts, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
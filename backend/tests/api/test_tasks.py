import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token

client = TestClient(app)

class TestTaskAPIEndpoints:
    """Test Task API endpoints with comprehensive coverage."""
    
    def test_create_task_success(self, db_session: Session, auth_headers):
        """Test successful task creation."""
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium",
            "due_date": "2024-12-31T23:59:59"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert response.status_code == 201
        content = response.json()
        assert content["title"] == task_data["title"]
        assert content["description"] == task_data["description"]
        assert content["priority"] == task_data["priority"]
        assert "id" in content
        assert "created_at" in content
    
    def test_create_task_minimal_data(self, db_session: Session, auth_headers):
        """Test task creation with minimal required data."""
        task_data = {
            "title": "Minimal Task"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert response.status_code == 201
        content = response.json()
        assert content["title"] == task_data["title"]
        assert content["status"] == "pending"
        assert content["priority"] == "medium"
        assert content["is_recurring"] is False
    
    def test_create_task_invalid_data(self, auth_headers):
        """Test task creation with invalid data."""
        task_data = {
            "title": "",  # Empty title should fail
            "priority": "invalid_priority"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert response.status_code == 422
    
    def test_get_tasks_with_filters(self, db_session: Session, auth_headers):
        """Test getting tasks with various filters."""
        # First create some test tasks
        tasks_data = [
            {"title": "High Priority Task", "priority": "high", "status": "pending"},
            {"title": "Low Priority Task", "priority": "low", "status": "completed"},
            {"title": "Medium Priority Task", "priority": "medium", "status": "in_progress"}
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
            created_tasks.append(response.json())
        
        # Test status filter
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"status": "pending"}
        )
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert all(task["status"] == "pending" for task in tasks)
        
        # Test priority filter
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"priority": "high"}
        )
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert all(task["priority"] == "high" for task in tasks)
    
    def test_get_task_by_id(self, db_session: Session, auth_headers):
        """Test getting a specific task by ID."""
        # Create a task first
        task_data = {"title": "Specific Task", "description": "For ID testing"}
        create_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Get the task by ID
        response = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
    
    def test_get_task_not_found(self, auth_headers):
        """Test getting a non-existent task."""
        response = client.get(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_task(self, db_session: Session, auth_headers):
        """Test updating a task."""
        # Create a task first
        task_data = {"title": "Original Task", "priority": "low"}
        create_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Update the task
        update_data = {"title": "Updated Task", "priority": "high", "status": "in_progress"}
        response = client.put(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["priority"] == update_data["priority"]
        assert updated_task["status"] == update_data["status"]
        assert updated_task["id"] == task_id
    
    def test_update_task_not_found(self, auth_headers):
        """Test updating a non-existent task."""
        update_data = {"title": "Non-existent Task"}
        response = client.put(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 404
    
    def test_delete_task(self, db_session: Session, auth_headers):
        """Test deleting a task."""
        # Create a task first
        task_data = {"title": "Task to Delete"}
        create_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Delete the task
        response = client.delete(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_mark_task_complete(self, db_session: Session, auth_headers):
        """Test marking a task as complete."""
        # Create a task first
        task_data = {"title": "Task to Complete", "status": "pending"}
        create_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Mark as complete
        response = client.put(
            f"{settings.API_V1_STR}/tasks/{task_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        completed_task = response.json()
        assert completed_task["status"] == "completed"
        assert completed_task["completed_at"] is not None
    
    def test_unauthorized_access(self):
        """Test accessing endpoints without authentication."""
        # Test without headers
        response = client.get(f"{settings.API_V1_STR}/tasks/")
        assert response.status_code == 401
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            json={"title": "Unauthorized Task"}
        )
        assert response.status_code == 401
    
    def test_invalid_auth_token(self):
        """Test accessing endpoints with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=invalid_headers
        )
        assert response.status_code == 401
    
    def test_pagination(self, db_session: Session, auth_headers):
        """Test task list pagination."""
        # Create multiple tasks
        for i in range(15):
            task_data = {"title": f"Task {i+1}"}
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
        
        # Test first page
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 10
        
        # Test second page
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"skip": 10, "limit": 10}
        )
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 5  # At least the remaining tasks
    
    def test_task_search(self, db_session: Session, auth_headers):
        """Test task search functionality."""
        # Create tasks with different titles
        search_tasks = [
            {"title": "Important meeting with client"},
            {"title": "Buy groceries for the week"},
            {"title": "Review quarterly reports"},
            {"title": "Schedule doctor appointment"},
        ]
        
        for task_data in search_tasks:
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
        
        # Search for tasks containing "meeting"
        response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"search": "meeting"}
        )
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert any("meeting" in task["title"].lower() for task in tasks)


class TestTaskCategoryAPIEndpoints:
    """Test Task Category API endpoints."""
    
    def test_create_category(self, auth_headers):
        """Test creating a task category."""
        category_data = {
            "name": "Work",
            "color": "#FF5722",
            "description": "Work related tasks"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers,
            json=category_data
        )
        
        assert response.status_code == 201
        content = response.json()
        assert content["name"] == category_data["name"]
        assert content["color"] == category_data["color"]
        assert content["description"] == category_data["description"]
        assert "id" in content
    
    def test_get_categories(self, db_session: Session, auth_headers):
        """Test getting user's categories."""
        # Create a category first
        category_data = {"name": "Personal", "color": "#4CAF50"}
        create_response = client.post(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers,
            json=category_data
        )
        assert create_response.status_code == 201
        
        # Get categories
        response = client.get(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) >= 1
        assert any(cat["name"] == "Personal" for cat in categories)
    
    def test_update_category(self, db_session: Session, auth_headers):
        """Test updating a category."""
        # Create a category first
        category_data = {"name": "Original", "color": "#000000"}
        create_response = client.post(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers,
            json=category_data
        )
        assert create_response.status_code == 201
        category = create_response.json()
        
        # Update the category
        update_data = {"name": "Updated", "color": "#FFFFFF"}
        response = client.put(
            f"{settings.API_V1_STR}/task-categories/{category['id']}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        updated_category = response.json()
        assert updated_category["name"] == update_data["name"]
        assert updated_category["color"] == update_data["color"]
    
    def test_delete_category(self, db_session: Session, auth_headers):
        """Test deleting a category."""
        # Create a category first
        category_data = {"name": "To Delete"}
        create_response = client.post(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers,
            json=category_data
        )
        assert create_response.status_code == 201
        category = create_response.json()
        
        # Delete the category
        response = client.delete(
            f"{settings.API_V1_STR}/task-categories/{category['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 204


class TestTaskRecurrenceAPIEndpoints:
    """Test Task Recurrence API endpoints."""
    
    def test_create_recurring_task(self, auth_headers):
        """Test creating a task with recurrence."""
        task_data = {
            "title": "Weekly Meeting",
            "description": "Team standup",
            "recurrence": {
                "recurrence_type": "weekly",
                "recurrence_interval": 1,
                "days_of_week": "1,3,5",  # Mon, Wed, Fri
                "lead_time_days": 0
            }
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        
        assert response.status_code == 201
        task = response.json()
        assert task["is_recurring"] is True
        assert task["recurrence"] is not None
        assert task["recurrence"]["recurrence_type"] == "weekly"
    
    def test_update_task_recurrence(self, db_session: Session, auth_headers):
        """Test updating task recurrence settings."""
        # Create a recurring task first
        task_data = {
            "title": "Monthly Report",
            "recurrence": {
                "recurrence_type": "monthly",
                "recurrence_interval": 1,
                "day_of_month": 1
            }
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        assert create_response.status_code == 201
        task = create_response.json()
        
        # Update recurrence
        update_data = {
            "recurrence": {
                "recurrence_type": "monthly",
                "recurrence_interval": 2,  # Every 2 months
                "day_of_month": 15
            }
        }
        
        response = client.put(
            f"{settings.API_V1_STR}/tasks/{task['id']}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["recurrence"]["recurrence_interval"] == 2
        assert updated_task["recurrence"]["day_of_month"] == 15
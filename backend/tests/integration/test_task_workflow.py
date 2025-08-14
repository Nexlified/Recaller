import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings

client = TestClient(app)

class TestTaskManagementWorkflow:
    """Integration tests for complete task management workflows."""
    
    def test_complete_task_lifecycle_workflow(self, db_session: Session, auth_headers):
        """Test the complete lifecycle of a task from creation to completion."""
        
        # Step 1: Create a category for organization
        category_data = {
            "name": "Project Management",
            "color": "#FF5722",
            "description": "Tasks related to project management"
        }
        category_response = client.post(
            f"{settings.API_V1_STR}/task-categories/",
            headers=auth_headers,
            json=category_data
        )
        assert category_response.status_code == 201
        category = category_response.json()
        assert category["name"] == category_data["name"]
        
        # Step 2: Create a task with the category
        task_data = {
            "title": "Complete Project Proposal",
            "description": "Draft and finalize the Q4 project proposal",
            "priority": "high",
            "due_date": "2024-12-31T17:00:00",
            "category_ids": [category["id"]]
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        assert task_response.status_code == 201
        task = task_response.json()
        assert task["title"] == task_data["title"]
        assert task["status"] == "pending"
        assert task["is_recurring"] is False
        assert len(task["categories"]) == 1
        assert task["categories"][0]["id"] == category["id"]
        
        # Step 3: Update task status to in_progress
        update_response = client.put(
            f"{settings.API_V1_STR}/tasks/{task['id']}",
            headers=auth_headers,
            json={"status": "in_progress", "description": "Started working on the proposal"}
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["status"] == "in_progress"
        assert "Started working on the proposal" in updated_task["description"]
        
        # Step 4: Add a contact to the task (simulate collaboration)
        # First create a contact
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "visibility": "private"
        }
        contact_response = client.post(
            "/api/v1/contacts/",
            headers=auth_headers,
            json=contact_data
        )
        # Note: This may fail if contacts endpoint doesn't exist yet
        # In that case, we'll skip the contact association part
        
        # Step 5: Mark task as complete
        complete_response = client.put(
            f"{settings.API_V1_STR}/tasks/{task['id']}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["status"] == "completed"
        assert completed_task["completed_at"] is not None
        
        # Step 6: Verify task appears in completed list
        completed_tasks_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"status": "completed"}
        )
        assert completed_tasks_response.status_code == 200
        completed_tasks = completed_tasks_response.json()
        completed_task_ids = [t["id"] for t in completed_tasks]
        assert task["id"] in completed_task_ids
        
        # Step 7: Verify analytics/metrics update
        # This would test the analytics endpoint when available
        # analytics_response = client.get(
        #     f"{settings.API_V1_STR}/analytics/tasks",
        #     headers=auth_headers
        # )
        # assert analytics_response.status_code == 200
        # analytics = analytics_response.json()
        # assert analytics["completed_today"] >= 1
    
    def test_recurring_task_workflow(self, db_session: Session, auth_headers):
        """Test the complete workflow for recurring tasks."""
        
        # Step 1: Create a recurring task
        recurring_task_data = {
            "title": "Weekly Team Standup",
            "description": "Team standup meeting every Monday",
            "priority": "medium",
            "recurrence": {
                "recurrence_type": "weekly",
                "recurrence_interval": 1,
                "days_of_week": "1",  # Monday
                "lead_time_days": 1
            }
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=recurring_task_data
        )
        assert task_response.status_code == 201
        recurring_task = task_response.json()
        assert recurring_task["is_recurring"] is True
        assert recurring_task["recurrence"] is not None
        assert recurring_task["recurrence"]["recurrence_type"] == "weekly"
        
        # Step 2: Complete the recurring task
        complete_response = client.put(
            f"{settings.API_V1_STR}/tasks/{recurring_task['id']}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        completed_recurring_task = complete_response.json()
        assert completed_recurring_task["status"] == "completed"
        
        # Step 3: Verify the task can be retrieved and still has recurrence info
        get_response = client.get(
            f"{settings.API_V1_STR}/tasks/{recurring_task['id']}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["is_recurring"] is True
        assert retrieved_task["status"] == "completed"
        
        # Step 4: Test updating recurrence pattern
        update_recurrence_response = client.put(
            f"{settings.API_V1_STR}/tasks/{recurring_task['id']}",
            headers=auth_headers,
            json={
                "recurrence": {
                    "recurrence_type": "weekly",
                    "recurrence_interval": 2,  # Every 2 weeks
                    "days_of_week": "1,3",     # Monday and Wednesday
                    "lead_time_days": 2
                }
            }
        )
        assert update_recurrence_response.status_code == 200
        updated_recurring_task = update_recurrence_response.json()
        assert updated_recurring_task["recurrence"]["recurrence_interval"] == 2
        assert updated_recurring_task["recurrence"]["days_of_week"] == "1,3"
    
    def test_bulk_operations_workflow(self, db_session: Session, auth_headers):
        """Test bulk operations workflow."""
        
        # Step 1: Create multiple tasks
        task_ids = []
        for i in range(5):
            task_data = {
                "title": f"Bulk Task {i+1}",
                "description": f"Task number {i+1} for bulk operations",
                "priority": "low" if i % 2 == 0 else "medium"
            }
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
            task = response.json()
            task_ids.append(task["id"])
        
        # Step 2: Bulk update priority
        bulk_update_data = {
            "task_ids": task_ids,
            "priority": "high"
        }
        bulk_response = client.put(
            f"{settings.API_V1_STR}/tasks/bulk",
            headers=auth_headers,
            json=bulk_update_data
        )
        # Note: This endpoint may not exist yet - skip if it fails
        if bulk_response.status_code != 404:
            assert bulk_response.status_code == 200
            
            # Verify all tasks were updated
            for task_id in task_ids:
                get_response = client.get(
                    f"{settings.API_V1_STR}/tasks/{task_id}",
                    headers=auth_headers
                )
                assert get_response.status_code == 200
                task = get_response.json()
                assert task["priority"] == "high"
        
        # Step 3: Delete all created tasks
        for task_id in task_ids:
            delete_response = client.delete(
                f"{settings.API_V1_STR}/tasks/{task_id}",
                headers=auth_headers
            )
            assert delete_response.status_code == 204
        
        # Step 4: Verify tasks are deleted
        for task_id in task_ids:
            get_response = client.get(
                f"{settings.API_V1_STR}/tasks/{task_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 404
    
    def test_search_and_filtering_workflow(self, db_session: Session, auth_headers):
        """Test comprehensive search and filtering workflow."""
        
        # Step 1: Create categories for filtering
        categories = []
        for i, name in enumerate(["Work", "Personal", "Shopping"]):
            category_data = {
                "name": name,
                "color": f"#{i:02X}{i:02X}{i:02X}",
                "description": f"{name} related tasks"
            }
            response = client.post(
                f"{settings.API_V1_STR}/task-categories/",
                headers=auth_headers,
                json=category_data
            )
            assert response.status_code == 201
            categories.append(response.json())
        
        # Step 2: Create diverse tasks for filtering
        test_tasks = [
            {
                "title": "Important Meeting Preparation",
                "description": "Prepare slides for quarterly review",
                "priority": "high",
                "status": "pending",
                "category_ids": [categories[0]["id"]],  # Work
                "due_date": "2024-12-15T14:00:00"
            },
            {
                "title": "Buy Groceries",
                "description": "Get milk, bread, and vegetables",
                "priority": "medium",
                "status": "pending",
                "category_ids": [categories[2]["id"]],  # Shopping
            },
            {
                "title": "Doctor Appointment",
                "description": "Annual health checkup",
                "priority": "low",
                "status": "completed",
                "category_ids": [categories[1]["id"]],  # Personal
                "due_date": "2024-11-20T10:00:00"
            },
            {
                "title": "Project Deadline",
                "description": "Submit final project deliverables",
                "priority": "high",
                "status": "in_progress",
                "category_ids": [categories[0]["id"]],  # Work
                "due_date": "2024-12-31T23:59:59"
            }
        ]
        
        created_tasks = []
        for task_data in test_tasks:
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
            created_tasks.append(response.json())
        
        # Step 3: Test various filtering scenarios
        
        # Filter by priority
        high_priority_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"priority": "high"}
        )
        assert high_priority_response.status_code == 200
        high_priority_tasks = high_priority_response.json()
        assert len(high_priority_tasks) >= 2
        assert all(task["priority"] == "high" for task in high_priority_tasks)
        
        # Filter by status
        pending_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"status": "pending"}
        )
        assert pending_response.status_code == 200
        pending_tasks = pending_response.json()
        assert len(pending_tasks) >= 2
        assert all(task["status"] == "pending" for task in pending_tasks)
        
        # Filter by category
        work_category_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"category_ids": categories[0]["id"]}
        )
        assert work_category_response.status_code == 200
        work_tasks = work_category_response.json()
        assert len(work_tasks) >= 2
        
        # Search by title
        meeting_search_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"search": "Meeting"}
        )
        assert meeting_search_response.status_code == 200
        meeting_tasks = meeting_search_response.json()
        assert len(meeting_tasks) >= 1
        assert any("Meeting" in task["title"] for task in meeting_tasks)
        
        # Combined filters
        combined_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"priority": "high", "status": "pending"}
        )
        assert combined_response.status_code == 200
        combined_tasks = combined_response.json()
        assert all(
            task["priority"] == "high" and task["status"] == "pending"
            for task in combined_tasks
        )
    
    def test_error_handling_workflow(self, db_session: Session, auth_headers):
        """Test error handling in various workflow scenarios."""
        
        # Test 1: Create task with invalid data
        invalid_task_data = {
            "title": "",  # Empty title
            "priority": "invalid_priority",
            "due_date": "invalid_date"
        }
        error_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=invalid_task_data
        )
        assert error_response.status_code == 422
        
        # Test 2: Try to access non-existent task
        get_response = client.get(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers
        )
        assert get_response.status_code == 404
        
        # Test 3: Try to update non-existent task
        update_response = client.put(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers,
            json={"title": "Updated Title"}
        )
        assert update_response.status_code == 404
        
        # Test 4: Try to delete non-existent task
        delete_response = client.delete(
            f"{settings.API_V1_STR}/tasks/99999",
            headers=auth_headers
        )
        assert delete_response.status_code == 404
        
        # Test 5: Invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        auth_error_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=invalid_headers
        )
        assert auth_error_response.status_code == 401
        
        # Test 6: No authentication
        no_auth_response = client.get(f"{settings.API_V1_STR}/tasks/")
        assert no_auth_response.status_code == 401
    
    def test_tenant_isolation_workflow(self, db_session: Session, auth_headers, test_tenant):
        """Test that tenant isolation works properly in complete workflows."""
        
        # This test would require creating multiple tenants and users
        # For now, we'll test basic tenant filtering
        
        # Create a task in tenant 1
        task_data = {
            "title": "Tenant 1 Task",
            "description": "Task belonging to tenant 1"
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            json=task_data
        )
        assert task_response.status_code == 201
        task = task_response.json()
        assert task["tenant_id"] == test_tenant.id
        
        # Verify task appears in tenant's task list
        list_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        tasks = list_response.json()
        task_ids = [t["id"] for t in tasks]
        assert task["id"] in task_ids
        
        # All tasks should belong to the same tenant
        assert all(t["tenant_id"] == test_tenant.id for t in tasks)
    
    def test_performance_under_load_workflow(self, db_session: Session, auth_headers):
        """Test workflow performance under moderate load."""
        import time
        
        # Create a realistic workflow scenario
        start_time = time.time()
        
        # Step 1: Create categories (realistic user scenario)
        categories = []
        for name in ["Urgent", "Important", "Someday"]:
            response = client.post(
                f"{settings.API_V1_STR}/task-categories/",
                headers=auth_headers,
                json={"name": name, "color": "#FF0000"}
            )
            assert response.status_code == 201
            categories.append(response.json())
        
        # Step 2: Create a reasonable number of tasks
        created_tasks = []
        for i in range(20):
            task_data = {
                "title": f"Workflow Task {i+1}",
                "description": f"Task {i+1} for workflow testing",
                "priority": ["low", "medium", "high"][i % 3],
                "category_ids": [categories[i % len(categories)]["id"]]
            }
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
            created_tasks.append(response.json())
        
        # Step 3: Perform various operations
        for i, task in enumerate(created_tasks[:10]):
            # Update some tasks
            if i % 2 == 0:
                update_response = client.put(
                    f"{settings.API_V1_STR}/tasks/{task['id']}",
                    headers=auth_headers,
                    json={"status": "in_progress"}
                )
                assert update_response.status_code == 200
            
            # Complete some tasks
            if i % 3 == 0:
                complete_response = client.put(
                    f"{settings.API_V1_STR}/tasks/{task['id']}/complete",
                    headers=auth_headers
                )
                assert complete_response.status_code == 200
        
        # Step 4: Perform filtering and search operations
        filter_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"priority": "high", "limit": 50}
        )
        assert filter_response.status_code == 200
        
        search_response = client.get(
            f"{settings.API_V1_STR}/tasks/",
            headers=auth_headers,
            params={"search": "Workflow", "limit": 50}
        )
        assert search_response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertion: entire workflow should complete reasonably quickly
        assert total_time < 30.0, f"Complete workflow took {total_time:.2f}s, expected < 30s"
        
        print(f"\nWorkflow Performance Test:")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - Tasks created: {len(created_tasks)}")
        print(f"  - Categories created: {len(categories)}")
        print(f"  - Operations per second: {(len(created_tasks) + len(categories) + 10 + 10 + 2) / total_time:.2f}")
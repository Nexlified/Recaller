import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.mark.performance
class TestTaskPerformance:
    """Performance tests for task management operations."""
    
    def test_bulk_task_creation_performance(self, db_session: Session, auth_headers):
        """Test performance of creating multiple tasks concurrently."""
        def create_task(i):
            return client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json={
                    "title": f"Performance Task {i}",
                    "description": f"Task {i} for performance testing",
                    "priority": "medium"
                }
            )
        
        # Measure time for creating 100 tasks concurrently
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_task, i) for i in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify that most tasks were created successfully
        success_count = sum(1 for result in results if result.status_code == 201)
        assert success_count >= 95, f"Only {success_count}/100 tasks created successfully"
        
        # Performance assertion: should complete within reasonable time
        assert total_time < 30.0, f"Bulk task creation took {total_time:.2f}s, expected < 30s"
        
        # Log performance metrics
        print(f"\nBulk Task Creation Performance:")
        print(f"  - Tasks created: {success_count}/100")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - Average time per task: {total_time/100:.3f}s")
        print(f"  - Tasks per second: {success_count/total_time:.2f}")
    
    def test_task_list_performance_with_large_dataset(self, db_session: Session, auth_headers):
        """Test performance of task listing with large dataset."""
        # First create a large number of tasks
        print("\nCreating test dataset...")
        for i in range(1000):
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json={
                    "title": f"Dataset Task {i}",
                    "priority": ["low", "medium", "high"][i % 3],
                    "status": ["pending", "in_progress", "completed"][i % 3],
                }
            )
            if i % 100 == 0:
                print(f"  Created {i+1}/1000 tasks...")
        
        print("Testing list performance...")
        
        # Test various list operations and measure performance
        test_cases = [
            {"params": {"limit": 50}, "description": "List first 50 tasks"},
            {"params": {"limit": 100}, "description": "List first 100 tasks"},
            {"params": {"limit": 50, "status": "pending"}, "description": "List 50 pending tasks"},
            {"params": {"limit": 50, "priority": "high"}, "description": "List 50 high priority tasks"},
            {"params": {"limit": 50, "search": "Dataset"}, "description": "Search for 'Dataset' in 50 tasks"},
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params=test_case["params"]
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            tasks = response.json()
            
            # Performance assertion: should respond within reasonable time
            assert response_time < 5.0, f"{test_case['description']} took {response_time:.3f}s, expected < 5s"
            
            print(f"  - {test_case['description']}: {response_time:.3f}s ({len(tasks)} results)")
    
    def test_concurrent_task_operations_performance(self, db_session: Session, auth_headers):
        """Test performance of concurrent read/write operations."""
        # Create initial tasks
        initial_tasks = []
        for i in range(50):
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json={"title": f"Concurrent Task {i}"}
            )
            assert response.status_code == 201
            initial_tasks.append(response.json())
        
        def read_operation():
            """Simulate read operations."""
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params={"limit": 20}
            )
            return response.status_code == 200
        
        def write_operation(task_id, iteration):
            """Simulate write operations."""
            response = client.put(
                f"{settings.API_V1_STR}/tasks/{task_id}",
                headers=auth_headers,
                json={"title": f"Updated Task {task_id} - {iteration}"}
            )
            return response.status_code == 200
        
        def create_operation(iteration):
            """Simulate create operations."""
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json={"title": f"Concurrent New Task {iteration}"}
            )
            return response.status_code == 201
        
        # Run concurrent operations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            # Submit various operations concurrently
            futures = []
            
            # Read operations (simulating multiple users viewing tasks)
            for _ in range(30):
                futures.append(executor.submit(read_operation))
            
            # Update operations (simulating task updates)
            for i, task in enumerate(initial_tasks[:20]):
                futures.append(executor.submit(write_operation, task['id'], i))
            
            # Create operations (simulating new task creation)
            for i in range(10):
                futures.append(executor.submit(create_operation, i))
            
            # Wait for all operations to complete
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify that most operations completed successfully
        success_count = sum(results)
        total_operations = len(results)
        success_rate = success_count / total_operations
        
        assert success_rate >= 0.95, f"Only {success_rate:.1%} operations succeeded"
        assert total_time < 20.0, f"Concurrent operations took {total_time:.2f}s, expected < 20s"
        
        print(f"\nConcurrent Operations Performance:")
        print(f"  - Total operations: {total_operations}")
        print(f"  - Successful operations: {success_count} ({success_rate:.1%})")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - Operations per second: {total_operations/total_time:.2f}")
    
    def test_task_filtering_performance(self, db_session: Session, auth_headers):
        """Test performance of complex filtering operations."""
        # Create tasks with various attributes for filtering
        categories = []
        for i in range(5):
            response = client.post(
                f"{settings.API_V1_STR}/task-categories/",
                headers=auth_headers,
                json={"name": f"Category {i}", "color": f"#00{i}{i}{i}{i}00"}
            )
            assert response.status_code == 201
            categories.append(response.json())
        
        # Create tasks with various combinations of attributes
        print("Creating tasks for filtering performance test...")
        for i in range(500):
            task_data = {
                "title": f"Filter Test Task {i}",
                "priority": ["low", "medium", "high"][i % 3],
                "status": ["pending", "in_progress", "completed"][i % 3],
                "category_ids": [categories[i % len(categories)]["id"]],
            }
            
            if i % 3 == 0:  # Add due dates to some tasks
                import datetime
                due_date = datetime.datetime.now() + datetime.timedelta(days=i % 30)
                task_data["due_date"] = due_date.isoformat()
            
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json=task_data
            )
            assert response.status_code == 201
            
            if i % 100 == 0:
                print(f"  Created {i+1}/500 tasks...")
        
        # Test various filtering combinations
        filter_tests = [
            {"priority": "high", "description": "Filter by high priority"},
            {"status": "pending", "description": "Filter by pending status"},
            {"priority": "high", "status": "pending", "description": "Filter by priority and status"},
            {"category_ids": str(categories[0]["id"]), "description": "Filter by category"},
            {"search": "Filter Test", "description": "Search by title"},
            {"has_due_date": "true", "description": "Filter tasks with due dates"},
        ]
        
        print("\nTesting filter performance...")
        for filter_test in filter_tests:
            params = {k: v for k, v in filter_test.items() if k != "description"}
            
            start_time = time.time()
            
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params=params
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            tasks = response.json()
            
            # Performance assertion
            assert response_time < 3.0, f"{filter_test['description']} took {response_time:.3f}s, expected < 3s"
            
            print(f"  - {filter_test['description']}: {response_time:.3f}s ({len(tasks)} results)")
    
    def test_task_pagination_performance(self, db_session: Session, auth_headers):
        """Test performance of pagination with large datasets."""
        # Use existing dataset or create if needed
        print("Testing pagination performance...")
        
        page_sizes = [10, 25, 50, 100]
        
        for page_size in page_sizes:
            # Test first page
            start_time = time.time()
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params={"limit": page_size, "skip": 0}
            )
            end_time = time.time()
            
            assert response.status_code == 200
            first_page_time = end_time - start_time
            
            # Test middle page
            start_time = time.time()
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params={"limit": page_size, "skip": page_size * 5}  # Page 6
            )
            end_time = time.time()
            
            assert response.status_code == 200
            middle_page_time = end_time - start_time
            
            # Performance assertions
            assert first_page_time < 2.0, f"First page (size {page_size}) took {first_page_time:.3f}s"
            assert middle_page_time < 2.0, f"Middle page (size {page_size}) took {middle_page_time:.3f}s"
            
            print(f"  - Page size {page_size:3d}: First={first_page_time:.3f}s, Middle={middle_page_time:.3f}s")
    
    def test_database_connection_pool_performance(self, db_session: Session, auth_headers):
        """Test database connection pool under load."""
        def make_request():
            response = client.get(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                params={"limit": 10}
            )
            return response.status_code == 200
        
        # Test with many concurrent requests to stress the connection pool
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success_count = sum(results)
        success_rate = success_count / len(results)
        
        assert success_rate >= 0.98, f"Connection pool stress test: {success_rate:.1%} success rate"
        assert total_time < 15.0, f"Connection pool stress test took {total_time:.2f}s"
        
        print(f"\nDatabase Connection Pool Performance:")
        print(f"  - Requests: {len(results)}")
        print(f"  - Success rate: {success_rate:.1%}")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - Requests per second: {len(results)/total_time:.2f}")


@pytest.mark.performance
class TestTaskCategoryPerformance:
    """Performance tests for task category operations."""
    
    def test_category_creation_and_assignment_performance(self, db_session: Session, auth_headers):
        """Test performance of creating categories and assigning tasks to them."""
        # Create categories
        start_time = time.time()
        
        categories = []
        for i in range(50):
            response = client.post(
                f"{settings.API_V1_STR}/task-categories/",
                headers=auth_headers,
                json={
                    "name": f"Performance Category {i}",
                    "color": f"#{i:02X}{i:02X}{i:02X}",
                    "description": f"Category {i} for performance testing"
                }
            )
            assert response.status_code == 201
            categories.append(response.json())
        
        category_creation_time = time.time() - start_time
        
        # Create tasks with category assignments
        start_time = time.time()
        
        for i in range(200):
            response = client.post(
                f"{settings.API_V1_STR}/tasks/",
                headers=auth_headers,
                json={
                    "title": f"Categorized Task {i}",
                    "category_ids": [categories[i % len(categories)]["id"]]
                }
            )
            assert response.status_code == 201
        
        task_creation_time = time.time() - start_time
        total_time = category_creation_time + task_creation_time
        
        assert total_time < 30.0, f"Category creation and assignment took {total_time:.2f}s"
        
        print(f"\nCategory Performance:")
        print(f"  - Category creation time: {category_creation_time:.2f}s")
        print(f"  - Task creation with categories: {task_creation_time:.2f}s")
        print(f"  - Total time: {total_time:.2f}s")
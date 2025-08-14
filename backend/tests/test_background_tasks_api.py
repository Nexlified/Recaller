import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.api.v1.endpoints.background_tasks import router
from app.models.user import User


class TestBackgroundTasksAPI:
    """Test Background Tasks API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = Mock(spec=User)
        user.id = 123
        user.email = "test@example.com"
        user.is_active = True
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def mock_superuser(self):
        """Create mock superuser."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "admin@example.com"
        user.is_active = True
        user.is_superuser = True
        return user
    
    @pytest.fixture
    def mock_tenant(self):
        """Create mock tenant."""
        tenant = Mock()
        tenant.id = 456
        return tenant
    
    @patch('app.api.v1.endpoints.background_tasks.process_user_recurring_transactions')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_trigger_recurring_transaction_processing(
        self, 
        mock_get_db, 
        mock_get_user, 
        mock_process_task,
        client, 
        mock_user
    ):
        """Test triggering recurring transaction processing."""
        # Mock dependencies
        mock_get_db.return_value = Mock()
        mock_get_user.return_value = mock_user
        
        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "task-123"
        mock_process_task.delay.return_value = mock_task
        
        # Mock request state
        with patch('app.api.v1.endpoints.background_tasks.Request') as mock_request_class:
            mock_request = Mock()
            mock_request.state.tenant.id = 456
            
            # Make the request
            response = client.post(
                "/api/v1/background-tasks/recurring-transactions/process",
                params={"dry_run": False}
            )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-123"
        assert "Processing recurring transactions" in data["message"]
        assert data["user_id"] == 123
        
        # Verify task was called correctly
        mock_process_task.delay.assert_called_once_with(
            user_id=123,
            tenant_id=456,
            dry_run=False
        )
    
    @patch('app.api.v1.endpoints.background_tasks.process_user_recurring_transactions')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_trigger_recurring_transaction_processing_dry_run(
        self, 
        mock_get_db, 
        mock_get_user, 
        mock_process_task,
        client, 
        mock_user
    ):
        """Test triggering dry run processing."""
        # Mock dependencies
        mock_get_db.return_value = Mock()
        mock_get_user.return_value = mock_user
        
        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "task-456"
        mock_process_task.delay.return_value = mock_task
        
        # Mock request state
        with patch('app.api.v1.endpoints.background_tasks.Request') as mock_request_class:
            mock_request = Mock()
            mock_request.state.tenant.id = 456
            
            # Make the request with dry_run=True
            response = client.post(
                "/api/v1/background-tasks/recurring-transactions/process",
                params={"dry_run": True}
            )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-456"
        assert "Dry run" in data["message"]
        
        # Verify task was called with dry_run=True
        mock_process_task.delay.assert_called_once_with(
            user_id=123,
            tenant_id=456,
            dry_run=True
        )
    
    @patch('app.api.v1.endpoints.background_tasks.send_recurring_transaction_reminders')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_trigger_recurring_transaction_reminders(
        self, 
        mock_get_db, 
        mock_get_user, 
        mock_reminder_task,
        client, 
        mock_user
    ):
        """Test triggering recurring transaction reminders."""
        # Mock dependencies
        mock_get_db.return_value = Mock()
        mock_get_user.return_value = mock_user
        
        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "reminder-task-789"
        mock_reminder_task.delay.return_value = mock_task
        
        # Mock request state
        with patch('app.api.v1.endpoints.background_tasks.Request') as mock_request_class:
            mock_request = Mock()
            mock_request.state.tenant.id = 456
            
            # Make the request
            response = client.post(
                "/api/v1/background-tasks/recurring-transactions/send-reminders"
            )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "reminder-task-789"
        assert "Sending recurring transaction reminders" in data["message"]
        assert data["user_id"] == 123
        
        # Verify task was called correctly
        mock_reminder_task.delay.assert_called_once_with(
            user_id=123,
            tenant_id=456
        )
    
    @patch('app.api.v1.endpoints.background_tasks.get_task_status')
    @patch('app.api.deps.get_current_active_user')
    def test_get_background_task_status_success(
        self, 
        mock_get_user, 
        mock_get_status,
        client, 
        mock_user
    ):
        """Test getting background task status successfully."""
        # Mock dependencies
        mock_get_user.return_value = mock_user
        
        # Mock task status response
        mock_status_task = Mock()
        mock_status_task.get.return_value = {
            "task_id": "test-task-123",
            "status": "SUCCESS",
            "result": {"processed": 5, "failed": 0},
            "traceback": None
        }
        mock_get_status.delay.return_value = mock_status_task
        
        # Make the request
        response = client.get("/api/v1/background-tasks/tasks/test-task-123/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-123"
        assert data["status"] == "SUCCESS"
        assert data["result"]["processed"] == 5
        
        # Verify task status was requested
        mock_get_status.delay.assert_called_once_with("test-task-123")
        mock_status_task.get.assert_called_once_with(timeout=5)
    
    @patch('app.api.v1.endpoints.background_tasks.get_task_status')
    @patch('app.api.deps.get_current_active_user')
    def test_get_background_task_status_timeout(
        self, 
        mock_get_user, 
        mock_get_status,
        client, 
        mock_user
    ):
        """Test getting background task status with timeout."""
        # Mock dependencies
        mock_get_user.return_value = mock_user
        
        # Mock task status that times out
        mock_status_task = Mock()
        mock_status_task.get.side_effect = Exception("Timeout")
        mock_get_status.delay.return_value = mock_status_task
        
        # Make the request
        response = client.get("/api/v1/background-tasks/tasks/timeout-task/status")
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "Failed to get task status" in data["detail"]
    
    @patch('app.api.v1.endpoints.background_tasks.process_all_recurring_transactions')
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.api.deps.get_db')
    def test_admin_trigger_all_recurring_processing(
        self, 
        mock_get_db, 
        mock_get_superuser, 
        mock_process_all,
        client, 
        mock_superuser
    ):
        """Test admin endpoint for processing all recurring transactions."""
        # Mock dependencies
        mock_get_db.return_value = Mock()
        mock_get_superuser.return_value = mock_superuser
        
        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "admin-task-999"
        mock_process_all.delay.return_value = mock_task
        
        # Make the request
        response = client.post(
            "/api/v1/background-tasks/admin/recurring-transactions/process-all",
            params={"dry_run": False}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "admin-task-999"
        assert "Processing all recurring transactions" in data["message"]
        
        # Verify task was called correctly
        mock_process_all.delay.assert_called_once_with(dry_run=False)
    
    @patch('app.api.v1.endpoints.background_tasks.send_recurring_transaction_reminders')
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.api.deps.get_db')
    def test_admin_trigger_all_reminders(
        self, 
        mock_get_db, 
        mock_get_superuser, 
        mock_send_all,
        client, 
        mock_superuser
    ):
        """Test admin endpoint for sending all reminders."""
        # Mock dependencies
        mock_get_db.return_value = Mock()
        mock_get_superuser.return_value = mock_superuser
        
        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "admin-reminder-task-111"
        mock_send_all.delay.return_value = mock_task
        
        # Make the request
        response = client.post(
            "/api/v1/background-tasks/admin/send-all-reminders"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "admin-reminder-task-111"
        assert "Sending all recurring transaction reminders" in data["message"]
        
        # Verify task was called correctly
        mock_send_all.delay.assert_called_once()
    
    @patch('app.api.deps.get_current_active_user')
    def test_unauthorized_access_to_admin_endpoints(
        self, 
        mock_get_user,
        client, 
        mock_user
    ):
        """Test that regular users cannot access admin endpoints."""
        # Mock regular user (not superuser)
        mock_get_user.return_value = mock_user
        
        # Try to access admin endpoint
        response = client.post(
            "/api/v1/background-tasks/admin/recurring-transactions/process-all"
        )
        
        # Should get permission error
        assert response.status_code == 400
        data = response.json()
        assert "doesn't have enough privileges" in data["detail"]
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated users cannot access endpoints."""
        # Try to access endpoint without authentication
        response = client.post(
            "/api/v1/background-tasks/recurring-transactions/process"
        )
        
        # Should get authentication error
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
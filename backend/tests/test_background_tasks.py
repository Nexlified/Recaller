import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.background_tasks import (
    process_all_recurring_transactions,
    process_user_recurring_transactions,
    send_recurring_transaction_reminders,
    health_check,
    get_task_status
)


class TestBackgroundTasks:
    """Test background task functionality."""
    
    @patch('app.services.background_tasks.SessionLocal')
    @patch('app.services.background_tasks.RecurringTransactionService')
    def test_process_all_recurring_transactions_success(
        self, 
        mock_service_class, 
        mock_session_local
    ):
        """Test successful processing of all recurring transactions."""
        # Mock database session
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock service and its response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.process_due_recurring_transactions.return_value = {
            "processed": 5,
            "failed": 0,
            "skipped": 2,
            "total_due": 7,
            "details": [],
            "errors": [],
            "skipped_details": []
        }
        
        # Execute the task
        result = process_all_recurring_transactions(dry_run=False)
        
        # Verify the result
        assert result["processed"] == 5
        assert result["failed"] == 0
        assert result["skipped"] == 2
        
        # Verify service was called correctly
        mock_service.process_due_recurring_transactions.assert_called_once_with(dry_run=False)
        
        # Verify database session was closed
        mock_db.close.assert_called_once()
    
    @patch('app.services.background_tasks.SessionLocal')
    @patch('app.services.background_tasks.RecurringTransactionService')
    def test_process_all_recurring_transactions_with_exception(
        self, 
        mock_service_class, 
        mock_session_local
    ):
        """Test handling of exceptions in recurring transaction processing."""
        # Mock database session
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock service that raises an exception
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.process_due_recurring_transactions.side_effect = Exception("Database error")
        
        # Execute the task and expect it to raise an exception
        with pytest.raises(Exception, match="Database error"):
            process_all_recurring_transactions(dry_run=False)
        
        # Verify database session was still closed
        mock_db.close.assert_called_once()
    
    @patch('app.services.background_tasks.SessionLocal')
    @patch('app.services.background_tasks.RecurringTransactionService')
    def test_process_user_recurring_transactions_success(
        self, 
        mock_service_class, 
        mock_session_local
    ):
        """Test successful processing of user-specific recurring transactions."""
        # Mock database session
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock service and its response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.process_due_recurring_transactions.return_value = {
            "processed": 2,
            "failed": 0,
            "skipped": 1,
            "total_due": 3,
            "details": [
                {"recurring_id": 1, "transaction_id": 101, "amount": "1500.00"},
                {"recurring_id": 2, "transaction_id": 102, "amount": "2000.00"}
            ],
            "errors": [],
            "skipped_details": [{"recurring_id": 3, "reason": "Already processed today"}]
        }
        
        # Execute the task
        result = process_user_recurring_transactions(
            user_id=123, 
            tenant_id=456, 
            dry_run=False
        )
        
        # Verify the result
        assert result["processed"] == 2
        assert result["failed"] == 0
        assert result["skipped"] == 1
        assert len(result["details"]) == 2
        
        # Verify service was called with correct parameters
        mock_service.process_due_recurring_transactions.assert_called_once_with(
            user_id=123, 
            tenant_id=456, 
            dry_run=False
        )
        
        # Verify database session was closed
        mock_db.close.assert_called_once()
    
    @patch('app.services.background_tasks.SessionLocal')
    @patch('app.services.background_tasks.NotificationService')
    def test_send_recurring_transaction_reminders_success(
        self, 
        mock_service_class, 
        mock_session_local
    ):
        """Test successful sending of recurring transaction reminders."""
        # Mock database session
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock service and its response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.send_recurring_transaction_reminders.return_value = {
            "notifications_sent": 3,
            "failed_notifications": 1,
            "details": [
                {"user_id": 1, "email": "user1@example.com", "reminder_count": 2},
                {"user_id": 2, "email": "user2@example.com", "reminder_count": 1},
                {"user_id": 3, "email": "user3@example.com", "reminder_count": 3}
            ],
            "errors": [
                {"user_id": 4, "email": "user4@example.com", "error": "SMTP error"}
            ]
        }
        
        # Execute the task
        result = send_recurring_transaction_reminders(user_id=None, tenant_id=None)
        
        # Verify the result
        assert result["notifications_sent"] == 3
        assert result["failed_notifications"] == 1
        assert len(result["details"]) == 3
        assert len(result["errors"]) == 1
        
        # Verify service was called correctly
        mock_service.send_recurring_transaction_reminders.assert_called_once_with(
            user_id=None, 
            tenant_id=None
        )
        
        # Verify database session was closed
        mock_db.close.assert_called_once()
    
    @patch('app.services.background_tasks.SessionLocal')
    @patch('app.services.background_tasks.NotificationService')
    def test_send_recurring_transaction_reminders_for_specific_user(
        self, 
        mock_service_class, 
        mock_session_local
    ):
        """Test sending reminders for a specific user."""
        # Mock database session
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock service and its response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.send_recurring_transaction_reminders.return_value = {
            "notifications_sent": 1,
            "failed_notifications": 0,
            "details": [
                {"user_id": 123, "email": "specific@example.com", "reminder_count": 2}
            ],
            "errors": []
        }
        
        # Execute the task for specific user
        result = send_recurring_transaction_reminders(user_id=123, tenant_id=456)
        
        # Verify the result
        assert result["notifications_sent"] == 1
        assert result["failed_notifications"] == 0
        
        # Verify service was called with correct parameters
        mock_service.send_recurring_transaction_reminders.assert_called_once_with(
            user_id=123, 
            tenant_id=456
        )
        
        # Verify database session was closed
        mock_db.close.assert_called_once()
    
    def test_health_check(self):
        """Test health check task."""
        result = health_check()
        
        assert result["status"] == "healthy"
        assert result["message"] == "Background tasks are running"
        assert "timestamp" in result
        
        # Verify timestamp is a valid ISO format
        timestamp = result["timestamp"]
        parsed_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed_timestamp, datetime)
    
    @patch('app.services.background_tasks.celery_app.AsyncResult')
    def test_get_task_status_success(self, mock_async_result):
        """Test getting task status successfully."""
        # Mock AsyncResult
        mock_result = Mock()
        mock_result.status = "SUCCESS"
        mock_result.result = {"completed": True}
        mock_result.traceback = None
        mock_async_result.return_value = mock_result
        
        # Execute the task
        result = get_task_status("test-task-id")
        
        # Verify the result
        assert result["task_id"] == "test-task-id"
        assert result["status"] == "SUCCESS"
        assert result["result"] == {"completed": True}
        assert result["traceback"] is None
        
        # Verify AsyncResult was called correctly
        mock_async_result.assert_called_once_with("test-task-id")
    
    @patch('app.services.background_tasks.celery_app.AsyncResult')
    def test_get_task_status_failed(self, mock_async_result):
        """Test getting status of failed task."""
        # Mock AsyncResult for failed task
        mock_result = Mock()
        mock_result.status = "FAILURE"
        mock_result.result = Exception("Task failed")
        mock_result.traceback = "Traceback (most recent call last):\n  File..."
        mock_async_result.return_value = mock_result
        
        # Execute the task
        result = get_task_status("failed-task-id")
        
        # Verify the result
        assert result["task_id"] == "failed-task-id"
        assert result["status"] == "FAILURE"
        assert result["traceback"] is not None
        
        # Verify AsyncResult was called correctly
        mock_async_result.assert_called_once_with("failed-task-id")
    
    @patch('app.services.background_tasks.celery_app.AsyncResult')
    def test_get_task_status_pending(self, mock_async_result):
        """Test getting status of pending task."""
        # Mock AsyncResult for pending task
        mock_result = Mock()
        mock_result.status = "PENDING"
        mock_result.result = None
        mock_result.traceback = None
        mock_async_result.return_value = mock_result
        
        # Execute the task
        result = get_task_status("pending-task-id")
        
        # Verify the result
        assert result["task_id"] == "pending-task-id"
        assert result["status"] == "PENDING"
        assert result["result"] is None
        assert result["traceback"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
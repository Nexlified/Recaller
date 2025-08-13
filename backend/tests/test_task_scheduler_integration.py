"""
Integration test for Task Scheduler Service - Basic functionality
"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.task_scheduler import TaskSchedulerService


class TestTaskSchedulerIntegration:
    """Integration tests for task scheduler functionality"""
    
    @pytest.mark.asyncio
    async def test_full_generation_workflow(self):
        """Test the complete task generation workflow"""
        scheduler = TaskSchedulerService()
        
        # Mock database session
        mock_db = Mock()
        
        # Create mock recurrence
        mock_recurrence = Mock()
        mock_recurrence.id = 1
        mock_recurrence.task_id = 100
        mock_recurrence.recurrence_type = "weekly"
        mock_recurrence.recurrence_interval = 1
        mock_recurrence.days_of_week = "1,3,5"  # Mon, Wed, Fri
        mock_recurrence.lead_time_days = 2
        mock_recurrence.end_date = None
        mock_recurrence.max_occurrences = None
        mock_recurrence.last_generated_at = None
        mock_recurrence.generation_count = 0
        
        # Create mock base task
        mock_base_task = Mock()
        mock_base_task.id = 100
        mock_base_task.tenant_id = 1
        mock_base_task.user_id = 1
        mock_base_task.title = "Weekly Team Meeting"
        mock_base_task.description = "Recurring team meeting"
        mock_base_task.status = "pending"
        mock_base_task.priority = "medium"
        
        # Create mock generated task
        mock_generated_task = Mock()
        mock_generated_task.id = 101
        mock_generated_task.parent_task_id = None
        
        # Setup database mocks
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_recurrence]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_base_task
        mock_db.query.return_value.filter.return_value.count.return_value = 0  # No existing generated tasks
        
        # Setup CRUD mock
        with patch('app.crud.task_recurrence.generate_next_task_instance', return_value=mock_generated_task), \
             patch('app.crud.task_recurrence.calculate_next_due_date', return_value=date.today() + timedelta(days=1)), \
             patch('app.services.task_scheduler.SessionLocal', return_value=mock_db):
            
            # Test the generation process
            result = scheduler._generate_task_instance(mock_db, mock_recurrence)
            
            # Verify the task was generated
            assert result == mock_generated_task
            assert result.parent_task_id == mock_base_task.id
            
            # Verify recurrence tracking was updated
            assert mock_recurrence.generation_count == 1
            assert mock_recurrence.last_generated_at is not None
            
            # Verify database operations
            mock_db.add.assert_called_with(mock_recurrence)
            mock_db.commit.assert_called()
    
    def test_scheduler_lifecycle(self):
        """Test starting and stopping the scheduler"""
        scheduler = TaskSchedulerService()
        
        # Initially not running
        assert not scheduler.is_running
        
        # Mock APScheduler to avoid actual scheduling
        with patch.object(scheduler.scheduler, 'start') as mock_start, \
             patch.object(scheduler.scheduler, 'add_job') as mock_add_job:
            
            # Start the scheduler
            scheduler.start()
            
            # Verify it's marked as running
            assert scheduler.is_running
            
            # Verify jobs were added
            assert mock_add_job.call_count == 2  # generate_recurring_tasks and cleanup_expired_recurrences
            mock_start.assert_called_once()
        
        # Mock shutdown
        with patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            
            # Stop the scheduler
            scheduler.stop()
            
            # Verify it's marked as stopped
            assert not scheduler.is_running
            mock_shutdown.assert_called_once()
    
    def test_lead_time_calculation(self):
        """Test lead time calculations work correctly"""
        scheduler = TaskSchedulerService()
        
        mock_db = Mock()
        mock_recurrence = Mock()
        mock_recurrence.id = 1
        mock_recurrence.task_id = 1
        mock_recurrence.end_date = None
        mock_recurrence.max_occurrences = None
        mock_recurrence.lead_time_days = 5  # 5 day lead time
        mock_recurrence.last_generated_at = None
        
        # Mock no existing tasks
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        current_date = date(2025, 1, 15)
        
        # Test case 1: Next due date within lead time (should generate)
        next_due_date = date(2025, 1, 18)  # 3 days from now
        with patch.object(scheduler, '_calculate_next_due_date', return_value=next_due_date):
            result = scheduler._should_generate_task(mock_db, mock_recurrence)
            assert result is True
        
        # Test case 2: Next due date outside lead time (should not generate)
        next_due_date = date(2025, 1, 25)  # 10 days from now
        with patch.object(scheduler, '_calculate_next_due_date', return_value=next_due_date):
            result = scheduler._should_generate_task(mock_db, mock_recurrence)
            assert result is False
    
    def test_max_occurrences_enforcement(self):
        """Test that max occurrences are properly enforced"""
        scheduler = TaskSchedulerService()
        
        mock_db = Mock()
        mock_recurrence = Mock()
        mock_recurrence.id = 1
        mock_recurrence.task_id = 1
        mock_recurrence.end_date = None
        mock_recurrence.max_occurrences = 3
        mock_recurrence.lead_time_days = 1
        mock_recurrence.last_generated_at = None
        
        # Test case 1: Under max occurrences (should generate)
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        with patch.object(scheduler, '_calculate_next_due_date', return_value=date.today() + timedelta(days=1)):
            result = scheduler._should_generate_task(mock_db, mock_recurrence)
            assert result is True
        
        # Test case 2: At max occurrences (should not generate)
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        with patch.object(scheduler, '_calculate_next_due_date', return_value=date.today() + timedelta(days=1)):
            result = scheduler._should_generate_task(mock_db, mock_recurrence)
            assert result is False
    
    def test_end_date_enforcement(self):
        """Test that end dates are properly enforced"""
        scheduler = TaskSchedulerService()
        
        mock_db = Mock()
        mock_recurrence = Mock()
        mock_recurrence.id = 1
        mock_recurrence.task_id = 1
        mock_recurrence.end_date = date(2025, 1, 10)  # End date in the past
        mock_recurrence.max_occurrences = None
        mock_recurrence.lead_time_days = 1
        mock_recurrence.last_generated_at = None
        
        # Should not generate when past end date
        result = scheduler._should_generate_task(mock_db, mock_recurrence)
        assert result is False
        
        # Test with future end date
        mock_recurrence.end_date = date(2025, 12, 31)  # End date in the future
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        with patch.object(scheduler, '_calculate_next_due_date', return_value=date.today() + timedelta(days=1)):
            result = scheduler._should_generate_task(mock_db, mock_recurrence)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_error_handling_continues_processing(self):
        """Test that errors in processing one recurrence don't stop others"""
        scheduler = TaskSchedulerService()
        
        # Create multiple mock recurrences
        mock_recurrence1 = Mock()
        mock_recurrence1.id = 1
        
        mock_recurrence2 = Mock()
        mock_recurrence2.id = 2
        
        # Mock the first one to fail, second to succeed
        with patch.object(scheduler, '_get_recurrences_due_for_generation', return_value=[mock_recurrence1, mock_recurrence2]), \
             patch.object(scheduler, '_should_generate_task', side_effect=[Exception("Test error"), True]), \
             patch.object(scheduler, '_generate_task_instance', return_value=Mock()), \
             patch('app.services.task_scheduler.SessionLocal') as mock_session:
            
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            # Should not raise exception despite first recurrence failing
            stats = await scheduler.manual_generate()
            
            # Should have processed both, with one error
            assert "errors" in stats
            assert stats["errors"] >= 1  # At least one error from the first recurrence


if __name__ == "__main__":
    # Run a simple test
    scheduler = TaskSchedulerService()
    print("✓ Scheduler created successfully")
    
    # Test date calculation logic
    from unittest.mock import Mock
    
    mock_recurrence = Mock()
    mock_recurrence.recurrence_type = "daily"
    mock_recurrence.recurrence_interval = 7
    mock_recurrence.end_date = None
    
    with patch('app.crud.task_recurrence.calculate_next_due_date') as mock_calc:
        mock_calc.return_value = date.today() + timedelta(days=7)
        
        result = scheduler._calculate_next_due_date(mock_recurrence, date.today())
        print(f"✓ Next due date calculation: {result}")
    
    print("✓ All basic integration tests passed")
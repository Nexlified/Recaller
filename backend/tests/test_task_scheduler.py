"""
Tests for Task Scheduler Service
"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.task_scheduler import TaskSchedulerService
from app.models.task import Task, TaskRecurrence


class TestTaskSchedulerService:
    """Test the TaskSchedulerService functionality"""
    
    def test_scheduler_initialization(self):
        """Test that the scheduler initializes correctly"""
        scheduler = TaskSchedulerService()
        assert scheduler is not None
        assert not scheduler.is_running
        assert scheduler.scheduler is not None
    
    def test_calculate_next_due_date_daily(self):
        """Test next due date calculation for daily recurrence"""
        scheduler = TaskSchedulerService()
        
        # Create a mock recurrence for daily pattern
        recurrence = Mock()
        recurrence.recurrence_type = "daily"
        recurrence.recurrence_interval = 3
        recurrence.end_date = None
        
        current_date = date(2025, 1, 15)
        
        with patch('app.crud.task_recurrence.calculate_next_due_date') as mock_calc:
            mock_calc.return_value = current_date + timedelta(days=3)
            
            next_date = scheduler._calculate_next_due_date(recurrence, current_date)
            
            assert next_date == date(2025, 1, 18)
            mock_calc.assert_called_once_with(recurrence, current_date)
    
    def test_should_generate_task_within_lead_time(self):
        """Test that tasks are generated when within lead time window"""
        scheduler = TaskSchedulerService()
        
        # Mock database and recurrence
        mock_db = Mock(spec=Session)
        
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 1
        recurrence.end_date = None
        recurrence.max_occurrences = None
        recurrence.lead_time_days = 3
        recurrence.last_generated_at = None
        
        # Mock query to return no existing generated tasks
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        current_date = date(2025, 1, 15)
        next_due_date = date(2025, 1, 17)  # Within lead time of 3 days
        
        with patch.object(scheduler, '_calculate_next_due_date', return_value=next_due_date):
            result = scheduler._should_generate_task(mock_db, recurrence)
            
            assert result is True
    
    def test_should_not_generate_task_outside_lead_time(self):
        """Test that tasks are not generated when outside lead time window"""
        scheduler = TaskSchedulerService()
        
        # Mock database and recurrence
        mock_db = Mock(spec=Session)
        
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 1
        recurrence.end_date = None
        recurrence.max_occurrences = None
        recurrence.lead_time_days = 3
        recurrence.last_generated_at = None
        
        current_date = date(2025, 1, 15)
        next_due_date = date(2025, 1, 25)  # Outside lead time of 3 days
        
        with patch.object(scheduler, '_calculate_next_due_date', return_value=next_due_date):
            result = scheduler._should_generate_task(mock_db, recurrence)
            
            assert result is False
    
    def test_should_not_generate_task_max_occurrences_reached(self):
        """Test that tasks are not generated when max occurrences reached"""
        scheduler = TaskSchedulerService()
        
        # Mock database and recurrence
        mock_db = Mock(spec=Session)
        
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 1
        recurrence.end_date = None
        recurrence.max_occurrences = 5
        recurrence.lead_time_days = 3
        recurrence.last_generated_at = None
        
        # Mock query to return 5 existing generated tasks (max reached)
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        result = scheduler._should_generate_task(mock_db, recurrence)
        
        assert result is False
    
    def test_should_not_generate_task_past_end_date(self):
        """Test that tasks are not generated past the end date"""
        scheduler = TaskSchedulerService()
        
        # Mock database and recurrence
        mock_db = Mock(spec=Session)
        
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 1
        recurrence.end_date = date(2025, 1, 10)  # Past end date
        recurrence.max_occurrences = None
        recurrence.lead_time_days = 3
        recurrence.last_generated_at = None
        
        current_date = date(2025, 1, 15)  # After end date
        
        result = scheduler._should_generate_task(mock_db, recurrence)
        
        assert result is False
    
    @patch('app.services.task_scheduler.SessionLocal')
    def test_get_recurrences_due_for_generation(self, mock_session_local):
        """Test getting recurrences due for generation"""
        scheduler = TaskSchedulerService()
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        # Mock recurrence data
        mock_recurrence = Mock()
        mock_recurrence.id = 1
        mock_recurrence.task_id = 1
        
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_recurrence]
        
        with patch.object(scheduler, '_should_generate_task', return_value=True):
            recurrences = scheduler._get_recurrences_due_for_generation(mock_db)
            
            assert len(recurrences) == 1
            assert recurrences[0] == mock_recurrence
    
    def test_generate_task_instance_success(self):
        """Test successful task instance generation"""
        scheduler = TaskSchedulerService()
        
        # Mock database
        mock_db = Mock(spec=Session)
        
        # Mock base task
        base_task = Mock()
        base_task.id = 1
        base_task.tenant_id = 1
        base_task.user_id = 1
        base_task.title = "Test Recurring Task"
        
        # Mock recurrence
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 1
        recurrence.lead_time_days = 3
        
        # Mock the CRUD function
        mock_new_task = Mock()
        mock_new_task.id = 2
        
        next_due_date = date(2025, 1, 20)
        
        with patch('app.crud.task_recurrence.generate_next_task_instance', return_value=mock_new_task), \
             patch.object(scheduler, '_calculate_next_due_date', return_value=next_due_date):
            
            result = scheduler._generate_task_instance(mock_db, recurrence)
            
            assert result == mock_new_task
            assert mock_new_task.parent_task_id == base_task.id
            mock_db.add.assert_called_with(recurrence)
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_manual_generate_returns_stats(self):
        """Test that manual generation returns proper statistics"""
        scheduler = TaskSchedulerService()
        
        with patch.object(scheduler, '_get_recurrences_due_for_generation', return_value=[]), \
             patch('app.services.task_scheduler.SessionLocal') as mock_session_local:
            
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            
            stats = await scheduler.manual_generate()
            
            assert isinstance(stats, dict)
            assert "total_recurrences_checked" in stats
            assert "tasks_generated" in stats
            assert "errors" in stats
            assert stats["total_recurrences_checked"] == 0
            assert stats["tasks_generated"] == 0
            assert stats["errors"] == 0


class TestTaskSchedulerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_calculate_next_due_date_handles_none_recurrence(self):
        """Test handling of None recurrence in date calculation"""
        scheduler = TaskSchedulerService()
        
        with patch('app.crud.task_recurrence.calculate_next_due_date', return_value=None):
            result = scheduler._calculate_next_due_date(None, date.today())
            assert result is None
    
    def test_generate_task_instance_handles_missing_base_task(self):
        """Test handling when base task is not found"""
        scheduler = TaskSchedulerService()
        
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        recurrence = Mock()
        recurrence.id = 1
        recurrence.task_id = 999  # Non-existent task
        
        result = scheduler._generate_task_instance(mock_db, recurrence)
        
        assert result is None
    
    def test_should_generate_task_handles_calculation_error(self):
        """Test error handling in should_generate_task"""
        scheduler = TaskSchedulerService()
        
        mock_db = Mock(spec=Session)
        recurrence = Mock()
        recurrence.id = 1
        
        with patch.object(scheduler, '_calculate_next_due_date', side_effect=Exception("Test error")):
            result = scheduler._should_generate_task(mock_db, recurrence)
            
            assert result is False
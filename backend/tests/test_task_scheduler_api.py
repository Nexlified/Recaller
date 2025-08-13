"""
Tests for Task Scheduler API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.services.task_scheduler import task_scheduler_service


client = TestClient(app)


class TestTaskSchedulerAPI:
    """Test the Task Scheduler API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock authentication for all tests
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.is_active = True
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_get_scheduler_status_running(self, mock_get_db, mock_get_user):
        """Test getting scheduler status when running"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        # Mock scheduler as running
        with patch.object(task_scheduler_service, 'is_running', True), \
             patch.object(task_scheduler_service.scheduler, 'get_jobs', return_value=[]):
            
            response = client.get("/api/v1/task-scheduler/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_running"] is True
            assert data["scheduler_state"] == "running"
            assert "jobs" in data
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_get_scheduler_status_stopped(self, mock_get_db, mock_get_user):
        """Test getting scheduler status when stopped"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        # Mock scheduler as stopped
        with patch.object(task_scheduler_service, 'is_running', False):
            
            response = client.get("/api/v1/task-scheduler/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_running"] is False
            assert data["scheduler_state"] == "stopped"
            assert data["jobs"] == []
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_manual_generate_success(self, mock_get_db, mock_get_user):
        """Test successful manual task generation"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        expected_stats = {
            "total_recurrences_checked": 5,
            "tasks_generated": 3,
            "errors": 0
        }
        
        with patch.object(task_scheduler_service, 'manual_generate', return_value=expected_stats):
            
            response = client.post("/api/v1/task-scheduler/generate")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Manual task generation completed"
            assert data["stats"] == expected_stats
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_manual_generate_error(self, mock_get_db, mock_get_user):
        """Test manual generation with error"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'manual_generate', side_effect=Exception("Test error")):
            
            response = client.post("/api/v1/task-scheduler/generate")
            
            assert response.status_code == 500
            assert "Error during manual generation" in response.json()["detail"]
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_start_scheduler_success(self, mock_get_db, mock_get_user):
        """Test successful scheduler start"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', False), \
             patch.object(task_scheduler_service, 'start') as mock_start:
            
            response = client.post("/api/v1/task-scheduler/start")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task scheduler started successfully"
            mock_start.assert_called_once()
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_start_scheduler_already_running(self, mock_get_db, mock_get_user):
        """Test starting scheduler when already running"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', True):
            
            response = client.post("/api/v1/task-scheduler/start")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task scheduler is already running"
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_stop_scheduler_success(self, mock_get_db, mock_get_user):
        """Test successful scheduler stop"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', True), \
             patch.object(task_scheduler_service, 'stop') as mock_stop:
            
            response = client.post("/api/v1/task-scheduler/stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task scheduler stopped successfully"
            mock_stop.assert_called_once()
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_stop_scheduler_not_running(self, mock_get_db, mock_get_user):
        """Test stopping scheduler when not running"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', False):
            
            response = client.post("/api/v1/task-scheduler/stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task scheduler is not running"
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_start_scheduler_error(self, mock_get_db, mock_get_user):
        """Test scheduler start with error"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', False), \
             patch.object(task_scheduler_service, 'start', side_effect=Exception("Start error")):
            
            response = client.post("/api/v1/task-scheduler/start")
            
            assert response.status_code == 500
            assert "Error starting scheduler" in response.json()["detail"]
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_stop_scheduler_error(self, mock_get_db, mock_get_user):
        """Test scheduler stop with error"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = Mock()
        
        with patch.object(task_scheduler_service, 'is_running', True), \
             patch.object(task_scheduler_service, 'stop', side_effect=Exception("Stop error")):
            
            response = client.post("/api/v1/task-scheduler/stop")
            
            assert response.status_code == 500
            assert "Error stopping scheduler" in response.json()["detail"]
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        # Test without authentication headers
        response = client.get("/api/v1/task-scheduler/status")
        assert response.status_code == 401
        
        response = client.post("/api/v1/task-scheduler/generate")
        assert response.status_code == 401
        
        response = client.post("/api/v1/task-scheduler/start")
        assert response.status_code == 401
        
        response = client.post("/api/v1/task-scheduler/stop")
        assert response.status_code == 401
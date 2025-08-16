import pytest
import tempfile
import os
import time
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.services.hot_reload_service import HotReloadService, ConfigFileHandler

class TestConfigFileHandler:
    """Test ConfigFileHandler functionality"""
    
    def test_file_handler_initialization(self):
        """Test file handler can be initialized"""
        callback = MagicMock()
        handler = ConfigFileHandler(callback)
        
        assert handler.reload_callback == callback
        assert handler.debounce_seconds == 2
        assert isinstance(handler.last_reload, dict)
    
    def test_yaml_file_detection(self):
        """Test that handler only responds to YAML files"""
        callback = MagicMock()
        handler = ConfigFileHandler(callback)
        
        # Mock event objects
        yaml_event = MagicMock()
        yaml_event.is_directory = False
        yaml_event.src_path = "/test/config.yml"
        
        other_event = MagicMock()
        other_event.is_directory = False
        other_event.src_path = "/test/config.txt"
        
        dir_event = MagicMock()
        dir_event.is_directory = True
        dir_event.src_path = "/test/directory"
        
        with patch.object(handler, '_handle_file_change') as mock_handle:
            # Should trigger for YAML files
            handler.on_modified(yaml_event)
            mock_handle.assert_called_once_with("/test/config.yml")
            
            mock_handle.reset_mock()
            
            # Should not trigger for non-YAML files
            handler.on_modified(other_event)
            mock_handle.assert_not_called()
            
            # Should not trigger for directories
            handler.on_modified(dir_event)
            mock_handle.assert_not_called()
    
    def test_debouncing_functionality(self):
        """Test that file changes are debounced"""
        callback = MagicMock()
        handler = ConfigFileHandler(callback)
        handler.debounce_seconds = 1  # Shorter for testing
        
        file_path = "/test/config.yml"
        
        # First call should trigger callback
        handler._handle_file_change(file_path)
        callback.assert_called_once_with(file_path)
        
        callback.reset_mock()
        
        # Immediate second call should be debounced
        handler._handle_file_change(file_path)
        callback.assert_not_called()
        
        # After debounce period, should trigger again
        handler.last_reload[file_path] = time.time() - 2  # Simulate time passing
        handler._handle_file_change(file_path)
        callback.assert_called_once_with(file_path)

class TestHotReloadService:
    """Test HotReloadService functionality"""
    
    def test_service_initialization(self):
        """Test service can be initialized"""
        service = HotReloadService()
        
        assert service.observer is None
        assert service.is_running is False
        assert isinstance(service.watched_paths, set)
        assert isinstance(service.reload_callbacks, list)
        assert service.config_root.name == "config"
        assert service.env_config_path.name == "environment"
    
    def test_service_start_stop_cycle(self):
        """Test service start/stop functionality"""
        service = HotReloadService()
        
        # Mock settings to enable hot reload
        with patch('app.services.hot_reload_service.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.ENABLE_HOT_RELOAD = True
            mock_get_settings.return_value = mock_settings
            
            with patch('app.services.hot_reload_service.Observer') as mock_observer_class:
                mock_observer = MagicMock()
                mock_observer_class.return_value = mock_observer
                
                with patch('pathlib.Path.exists', return_value=True):
                    # Test start
                    service.start()
                    
                    assert service.is_running is True
                    assert service.observer == mock_observer
                    mock_observer.start.assert_called_once()
                    
                    # Test stop
                    service.stop()
                    
                    assert service.is_running is False
                    mock_observer.stop.assert_called_once()
                    mock_observer.join.assert_called_once()
    
    def test_service_disabled_when_hot_reload_off(self):
        """Test service doesn't start when hot reload is disabled"""
        service = HotReloadService()
        
        with patch('app.services.hot_reload_service.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.ENABLE_HOT_RELOAD = False
            mock_get_settings.return_value = mock_settings
            
            service.start()
            
            # Should not start observer
            assert service.observer is None
            assert service.is_running is False
    
    def test_config_change_handling(self):
        """Test configuration change handling"""
        service = HotReloadService()
        
        # Mock methods
        with patch.object(service, '_reload_environment_config') as mock_env_reload:
            with patch.object(service, '_reload_yaml_config') as mock_yaml_reload:
                # Test environment config change
                service._on_config_change("/path/to/environment/dev.yml")
                mock_env_reload.assert_called_once()
                mock_yaml_reload.assert_not_called()
                
                mock_env_reload.reset_mock()
                mock_yaml_reload.reset_mock()
                
                # Test regular config change
                service._on_config_change("/path/to/activity_types.yml")
                mock_env_reload.assert_not_called()
                mock_yaml_reload.assert_called_once_with("activity_types")
    
    def test_callback_management(self):
        """Test reload callback management"""
        service = HotReloadService()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        # Test adding callbacks
        service.add_reload_callback(callback1)
        service.add_reload_callback(callback2)
        
        assert callback1 in service.reload_callbacks
        assert callback2 in service.reload_callbacks
        
        # Test removing callback
        service.remove_reload_callback(callback1)
        
        assert callback1 not in service.reload_callbacks
        assert callback2 in service.reload_callbacks
    
    def test_environment_config_reload(self):
        """Test environment configuration reload"""
        service = HotReloadService()
        
        with patch('app.services.hot_reload_service.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.ENVIRONMENT = "test"
            mock_get_settings.return_value = mock_settings
            
            service._reload_environment_config()
            
            # Should call get_settings with reload=True
            mock_get_settings.assert_called_with(reload=True)
    
    def test_yaml_config_reload(self):
        """Test YAML configuration reload"""
        service = HotReloadService()
        
        with patch('app.services.hot_reload_service.config_manager') as mock_config_manager:
            mock_config_manager.get_config.return_value = {"test": "data"}
            
            service._reload_yaml_config("test_config")
            
            mock_config_manager.clear_cache.assert_called_once()
            mock_config_manager.get_config.assert_called_once_with("test_config")
    
    def test_callback_execution_during_reload(self):
        """Test that callbacks are executed during configuration reload"""
        service = HotReloadService()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        failing_callback = MagicMock(side_effect=Exception("Test error"))
        
        service.add_reload_callback(callback1)
        service.add_reload_callback(failing_callback)
        service.add_reload_callback(callback2)
        
        with patch.object(service, '_reload_environment_config'):
            # Should execute all callbacks, including handling exceptions
            service._on_config_change("/path/to/environment/dev.yml")
            
            callback1.assert_called_once_with("/path/to/environment/dev.yml")
            failing_callback.assert_called_once_with("/path/to/environment/dev.yml")
            callback2.assert_called_once_with("/path/to/environment/dev.yml")

class TestHotReloadIntegration:
    """Test hot reload integration functionality"""
    
    def test_global_service_instance(self):
        """Test that global service instance exists"""
        from app.services.hot_reload_service import hot_reload_service
        
        assert isinstance(hot_reload_service, HotReloadService)
        assert hot_reload_service.is_running is False
    
    def test_service_integration_with_settings(self):
        """Test service integrates properly with settings"""
        from app.services.hot_reload_service import hot_reload_service
        
        # Test that service respects settings
        with patch('app.services.hot_reload_service.get_settings') as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.ENABLE_HOT_RELOAD = False
            mock_get_settings.return_value = mock_settings
            
            hot_reload_service.start()
            assert hot_reload_service.is_running is False
            
            mock_settings.ENABLE_HOT_RELOAD = True
            mock_get_settings.return_value = mock_settings
            
            with patch('app.services.hot_reload_service.Observer'):
                with patch('pathlib.Path.exists', return_value=True):
                    hot_reload_service.start()
                    # Should start when enabled
                    assert hot_reload_service.is_running is True
                    
                    hot_reload_service.stop()

if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.configuration_manager import ConfigMetadata

class TestConfigManagerAPI:
    
    def setup_method(self):
        self.client = TestClient(app)
        # Mock authentication for testing
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.list_available_configs')
    def test_list_configurations_endpoint(self, mock_list_configs, mock_get_user):
        """Test the list configurations endpoint"""
        mock_get_user.return_value = self.mock_user
        mock_list_configs.return_value = [
            {
                'name': 'test_config',
                'path': '/path/to/test_config.yml',
                'source': 'main',
                'metadata': None
            }
        ]
        
        response = self.client.get("/api/v1/config-manager/configs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'test_config'
        assert data[0]['source'] == 'main'
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.get_config')
    def test_get_configuration_endpoint(self, mock_get_config, mock_get_user):
        """Test the get configuration endpoint"""
        mock_get_user.return_value = self.mock_user
        mock_get_config.return_value = {'test': 'data', 'version': '1.0.0'}
        
        response = self.client.get("/api/v1/config-manager/configs/test_config")
        
        assert response.status_code == 200
        data = response.json()
        assert data['test'] == 'data'
        assert data['version'] == '1.0.0'
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.get_config')
    def test_get_configuration_not_found(self, mock_get_config, mock_get_user):
        """Test the get configuration endpoint with non-existent config"""
        mock_get_user.return_value = self.mock_user
        mock_get_config.side_effect = FileNotFoundError("Config not found")
        
        response = self.client.get("/api/v1/config-manager/configs/nonexistent")
        
        assert response.status_code == 404
        assert "Configuration 'nonexistent' not found" in response.json()['detail']
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.get_config_metadata')
    def test_get_configuration_metadata_endpoint(self, mock_get_metadata, mock_get_user):
        """Test the get configuration metadata endpoint"""
        mock_get_user.return_value = self.mock_user
        mock_metadata = ConfigMetadata(
            version="1.0.0",
            category="test",
            type="test_config",
            name="Test Configuration",
            description="A test configuration"
        )
        mock_get_metadata.return_value = mock_metadata
        
        response = self.client.get("/api/v1/config-manager/configs/test_config/metadata")
        
        assert response.status_code == 200
        data = response.json()
        assert data['version'] == '1.0.0'
        assert data['category'] == 'test'
        assert data['name'] == 'Test Configuration'
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.get_config_metadata')
    def test_get_configuration_metadata_not_found(self, mock_get_metadata, mock_get_user):
        """Test the get configuration metadata endpoint with non-existent config"""
        mock_get_user.return_value = self.mock_user
        mock_get_metadata.return_value = None
        
        response = self.client.get("/api/v1/config-manager/configs/nonexistent/metadata")
        
        assert response.status_code == 404
        assert "Configuration 'nonexistent' not found" in response.json()['detail']
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.clear_cache')
    def test_reload_configurations_endpoint(self, mock_clear_cache, mock_get_user):
        """Test the reload configurations endpoint"""
        mock_get_user.return_value = self.mock_user
        
        response = self.client.post("/api/v1/config-manager/configs/reload")
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Configuration cache cleared successfully'
        mock_clear_cache.assert_called_once()
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.configuration_manager.config_manager.get_config')
    @patch('app.core.configuration_manager.config_manager.validate_config_structure')
    @patch('app.core.configuration_manager.config_manager.get_config_metadata')
    def test_validate_configuration_endpoint(self, mock_get_metadata, mock_validate, mock_get_config, mock_get_user):
        """Test the validate configuration endpoint"""
        mock_get_user.return_value = self.mock_user
        mock_get_config.return_value = {'test': 'data'}
        mock_validate.return_value = True
        mock_metadata = ConfigMetadata(
            version="1.0.0",
            category="test",
            type="test_config",
            name="Test Configuration",
            description="A test configuration"
        )
        mock_get_metadata.return_value = mock_metadata
        
        response = self.client.get("/api/v1/config-manager/configs/test_config/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data['config_type'] == 'test_config'
        assert data['valid'] is True
        assert data['metadata']['version'] == '1.0.0'
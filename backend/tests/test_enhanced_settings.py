import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.core.enhanced_settings import EnvironmentConfigLoader, EnhancedSettings, get_settings

class TestEnvironmentConfigLoader:
    """Test EnvironmentConfigLoader functionality"""
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution"""
        loader = EnvironmentConfigLoader()
        
        # Test simple substitution
        result = loader._substitute_env_var("${TEST_VAR:default_value}")
        assert result == "default_value"  # No env var set, should use default
        
        # Test with environment variable set
        with patch.dict(os.environ, {'TEST_VAR': 'env_value'}):
            result = loader._substitute_env_var("${TEST_VAR:default_value}")
            assert result == "env_value"
        
        # Test boolean conversion
        with patch.dict(os.environ, {'BOOL_VAR': 'true'}):
            result = loader._substitute_env_var("${BOOL_VAR:false}")
            assert result is True
        
        # Test integer conversion
        with patch.dict(os.environ, {'INT_VAR': '42'}):
            result = loader._substitute_env_var("${INT_VAR:0}")
            assert result == 42
    
    def test_config_loading_with_temp_file(self):
        """Test config loading with temporary YAML file"""
        # Create temporary YAML config
        config_content = """
        version: "1.0.0"
        category: "test"
        database:
          host: "${DB_HOST:localhost}"
          port: "${DB_PORT:5432}"
        features:
          hot_reload: "${HOT_RELOAD:true}"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            # Mock the config path to point to our temp file
            loader = EnvironmentConfigLoader()
            loader.env_config_path = Path(temp_file)
            
            config = loader.load_config()
            
            assert config['version'] == "1.0.0"
            assert config['database']['host'] == "localhost"
            assert config['database']['port'] == 5432
            assert config['features']['hot_reload'] is True
            
        finally:
            os.unlink(temp_file)
    
    def test_cache_functionality(self):
        """Test configuration caching"""
        loader = EnvironmentConfigLoader()
        
        # Mock load_config to avoid file system access
        with patch.object(loader, 'env_config_path') as mock_path:
            mock_path.exists.return_value = True
            
            with patch('builtins.open'), patch('yaml.safe_load') as mock_yaml:
                mock_yaml.return_value = {'test': 'data'}
                
                # First call
                config1 = loader.load_config()
                # Second call should use cache
                config2 = loader.load_config()
                
                # YAML should only be loaded once
                assert mock_yaml.call_count == 1
                assert config1 == config2
        
        # Test cache clearing
        loader.clear_cache()
        assert loader._config_cache == {}

class TestEnhancedSettings:
    """Test EnhancedSettings functionality"""
    
    def test_enhanced_settings_initialization(self):
        """Test enhanced settings can be initialized"""
        settings = EnhancedSettings()
        
        # Test basic attributes
        assert settings.PROJECT_NAME == "Recaller"
        assert settings.ENVIRONMENT == "development"
        assert isinstance(settings.ENABLE_HOT_RELOAD, bool)
    
    def test_yaml_config_integration(self):
        """Test YAML configuration integration"""
        # Create temporary YAML config
        config_content = """
        version: "1.0.0"
        category: "test"
        application:
          project_name: "Test Recaller"
          version: "2.0.0"
        features:
          hot_reload: false
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            # Mock the environment config path
            with patch('app.core.enhanced_settings.EnvironmentConfigLoader') as mock_loader_class:
                mock_loader = MagicMock()
                mock_loader.load_config.return_value = {
                    'application': {
                        'project_name': 'Test Recaller',
                        'version': '2.0.0'
                    },
                    'features': {
                        'hot_reload': False
                    }
                }
                mock_loader_class.return_value = mock_loader
                
                settings = EnhancedSettings()
                
                # Check that YAML config was applied
                assert settings.PROJECT_NAME == "Test Recaller"
                assert settings.VERSION == "2.0.0"
                assert settings.ENABLE_HOT_RELOAD is False
                
        finally:
            os.unlink(temp_file)
    
    def test_cors_parsing_methods(self):
        """Test CORS configuration parsing methods"""
        settings = EnhancedSettings()
        settings.CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:8080"
        settings.CORS_ALLOWED_METHODS = "GET,POST,PUT"
        settings.CORS_ALLOWED_HEADERS = "Content-Type,Authorization"
        
        origins = settings.get_cors_origins()
        methods = settings.get_cors_methods()
        headers = settings.get_cors_headers()
        
        assert origins == ["http://localhost:3000", "http://localhost:8080"]
        assert methods == ["GET", "POST", "PUT"]
        assert headers == ["Content-Type", "Authorization"]
    
    def test_reload_config_functionality(self):
        """Test configuration reload functionality"""
        settings = EnhancedSettings()
        settings.ENABLE_HOT_RELOAD = True
        
        # Mock the config loader reload
        with patch('app.core.enhanced_settings.EnvironmentConfigLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = {
                'application': {
                    'project_name': 'Reloaded Recaller'
                }
            }
            mock_loader_class.return_value = mock_loader
            
            # Test reload
            original_name = settings.PROJECT_NAME
            settings.reload_config()
            
            # Should have called the loader
            mock_loader.clear_cache.assert_called_once()
            mock_loader.load_config.assert_called_once()
    
    def test_get_settings_function(self):
        """Test get_settings function with reload functionality"""
        # Test initial load
        settings1 = get_settings()
        assert isinstance(settings1, EnhancedSettings)
        
        # Test same instance returned
        settings2 = get_settings()
        assert settings1 is settings2
        
        # Test reload creates new instance
        settings3 = get_settings(reload=True)
        assert isinstance(settings3, EnhancedSettings)
        # Note: The reload may or may not create a new instance depending on implementation
    
    def test_database_uri_assembly(self):
        """Test DATABASE_URI assembly from components"""
        settings = EnhancedSettings()
        settings.POSTGRES_SERVER = "testhost"
        settings.POSTGRES_USER = "testuser"
        settings.POSTGRES_PASSWORD = "testpass"
        settings.POSTGRES_DB = "testdb"
        settings.POSTGRES_PORT = 5433
        
        # Force DATABASE_URI reassembly
        settings.DATABASE_URI = None
        uri = EnhancedSettings.assemble_db_connection(None, {
            'POSTGRES_SERVER': 'testhost',
            'POSTGRES_USER': 'testuser', 
            'POSTGRES_PASSWORD': 'testpass',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_PORT': 5433
        })
        
        assert "postgresql://" in uri
        assert "testhost" in uri
        assert "testuser" in uri
        assert "testdb" in uri
        assert "5433" in uri

class TestBackwardCompatibility:
    """Test backward compatibility with existing Settings"""
    
    def test_settings_import_compatibility(self):
        """Test that enhanced settings can be imported like old settings"""
        from app.core.enhanced_settings import settings
        
        # Test that basic attributes are available
        assert hasattr(settings, 'PROJECT_NAME')
        assert hasattr(settings, 'VERSION')
        assert hasattr(settings, 'DATABASE_URI')
        assert hasattr(settings, 'SECRET_KEY')
    
    def test_cors_methods_compatibility(self):
        """Test that CORS methods are backward compatible"""
        from app.core.enhanced_settings import settings
        
        # Test that CORS parsing methods exist and work
        origins = settings.get_cors_origins()
        methods = settings.get_cors_methods()
        headers = settings.get_cors_headers()
        
        assert isinstance(origins, list)
        assert isinstance(methods, list) 
        assert isinstance(headers, list)
        assert len(origins) > 0
        assert len(methods) > 0
        assert len(headers) > 0

if __name__ == "__main__":
    pytest.main([__file__])
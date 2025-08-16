import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.core.configuration_manager import ConfigurationManager, ConfigMetadata

class TestConfigurationManager:
    
    def test_config_metadata_validation(self):
        """Test ConfigMetadata validation"""
        # Valid metadata
        metadata = ConfigMetadata(
            version="1.0.0",
            category="test",
            type="test_config",
            name="Test Configuration",
            description="A test configuration"
        )
        assert metadata.version == "1.0.0"
        assert metadata.author == "Recaller Team"  # Default value
        assert metadata.deprecated is False  # Default value
        
        # Test with optional fields
        metadata_with_optionals = ConfigMetadata(
            version="2.0.0",
            category="test",
            type="test_config",
            name="Test Configuration",
            description="A test configuration",
            author="Test Author",
            last_updated="2025-01-15",
            deprecated=True
        )
        assert metadata_with_optionals.author == "Test Author"
        assert metadata_with_optionals.deprecated is True
    
    def test_configuration_manager_initialization(self):
        """Test ConfigurationManager initialization"""
        manager = ConfigurationManager()
        
        # Check paths are set correctly
        assert manager.config_root.name == "config"
        assert manager.shared_config_root.name == "config"
        assert str(manager.shared_config_root).endswith("shared/config")
        
        # Check caches are initialized
        assert manager._cache == {}
        assert manager._metadata_cache == {}
    
    @patch('builtins.open')
    @patch('yaml.safe_load')
    @patch.object(Path, 'exists')
    def test_load_yaml_config_success(self, mock_exists, mock_yaml_load, mock_open):
        """Test successful YAML config loading"""
        manager = ConfigurationManager()
        
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock YAML content
        mock_config_data = {
            'version': '1.0.0',
            'category': 'test',
            'type': 'test_config', 
            'name': 'Test Config',
            'description': 'Test configuration',
            'test_data': 'test_value'
        }
        mock_yaml_load.return_value = mock_config_data
        
        # Mock file context manager
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test loading
        result = manager.load_yaml_config('test_config')
        
        assert result == mock_config_data
        assert 'test_config' in manager._metadata_cache
        
        # Verify metadata was extracted
        metadata = manager._metadata_cache['test_config']
        assert metadata.version == '1.0.0'
        assert metadata.category == 'test'
        assert metadata.type == 'test_config'
    
    @patch.object(Path, 'exists')
    def test_load_yaml_config_file_not_found(self, mock_exists):
        """Test FileNotFoundError when config file doesn't exist"""
        manager = ConfigurationManager()
        
        # Mock both main and shared paths don't exist
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Configuration file not found: nonexistent_config"):
            manager.load_yaml_config('nonexistent_config')
    
    @patch('builtins.open')
    @patch('yaml.safe_load')
    @patch.object(Path, 'exists')
    def test_load_yaml_config_invalid_yaml(self, mock_exists, mock_yaml_load, mock_open):
        """Test handling of invalid YAML"""
        manager = ConfigurationManager()
        
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock YAML error
        import yaml
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        
        # Mock file context manager
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with pytest.raises(ValueError, match="Invalid YAML in test_config: Invalid YAML"):
            manager.load_yaml_config('test_config')
    
    def test_get_config_with_fallback(self):
        """Test get_config method with fallback"""
        manager = ConfigurationManager()
        
        # Mock load_yaml_config to succeed
        test_config = {'test': 'data'}
        with patch.object(manager, 'load_yaml_config', return_value=test_config):
            result = manager.get_config('test_config')
            assert result == test_config
        
        # Mock load_yaml_config to fail, fallback to DB
        with patch.object(manager, 'load_yaml_config', side_effect=FileNotFoundError):
            with patch.object(manager, '_get_db_config', return_value={'db': 'data'}):
                result = manager.get_config('test_config', fallback_db=True)
                assert result == {'db': 'data'}
        
        # Mock load_yaml_config to fail, no fallback
        with patch.object(manager, 'load_yaml_config', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                manager.get_config('test_config', fallback_db=False)
    
    def test_get_config_metadata(self):
        """Test get_config_metadata method"""
        manager = ConfigurationManager()
        
        # Test with metadata in cache
        test_metadata = ConfigMetadata(
            version="1.0.0",
            category="test",
            type="test_config",
            name="Test Config",
            description="Test configuration"
        )
        manager._metadata_cache['test_config'] = test_metadata
        
        result = manager.get_config_metadata('test_config')
        assert result == test_metadata
        
        # Test with metadata not in cache, loads config
        del manager._metadata_cache['test_config']
        with patch.object(manager, 'load_yaml_config', return_value={'test': 'data'}):
            result = manager.get_config_metadata('test_config')
            # Should return None since load_yaml_config doesn't set metadata
            assert result is None
        
        # Test with config that doesn't exist
        with patch.object(manager, 'load_yaml_config', side_effect=FileNotFoundError):
            result = manager.get_config_metadata('nonexistent')
            assert result is None
    
    @patch.object(Path, 'glob')
    @patch.object(Path, 'rglob')
    def test_list_available_configs(self, mock_rglob, mock_glob):
        """Test list_available_configs method"""
        manager = ConfigurationManager()
        
        # Mock main config files
        main_file = MagicMock()
        main_file.stem = 'main_config'
        main_file.__str__ = MagicMock(return_value='/path/to/main_config.yml')
        mock_glob.return_value = [main_file]
        
        # Mock shared config files
        shared_file = MagicMock()
        shared_file.relative_to.return_value = Path('shared_config.yml')
        shared_file.with_suffix.return_value = Path('shared_config')
        shared_file.__str__ = MagicMock(return_value='/path/to/shared/shared_config.yml')
        mock_rglob.return_value = [shared_file]
        
        # Mock get_config_metadata
        with patch.object(manager, 'get_config_metadata', return_value=None):
            configs = manager.list_available_configs()
        
        assert len(configs) == 2
        
        # Check main config
        main_config = configs[0]
        assert main_config['name'] == 'main_config'
        assert main_config['source'] == 'main'
        assert main_config['metadata'] is None
        
        # Check shared config
        shared_config = configs[1]
        assert shared_config['name'] == 'shared_config'
        assert shared_config['source'] == 'shared'
        assert shared_config['metadata'] is None
    
    def test_validate_config_structure(self):
        """Test validate_config_structure method"""
        manager = ConfigurationManager()
        
        # Currently just returns True (placeholder)
        result = manager.validate_config_structure({})
        assert result is True
        
        result = manager.validate_config_structure({'any': 'data'})
        assert result is True
    
    def test_clear_cache(self):
        """Test clear_cache method"""
        manager = ConfigurationManager()
        
        # Add some data to caches
        manager._cache['test'] = 'data'
        manager._metadata_cache['test'] = 'metadata'
        
        # Mock the functools.lru_cache wrapper's cache_clear method
        with patch.object(manager, 'load_yaml_config') as mock_load:
            mock_load.cache_clear = MagicMock()
            manager.clear_cache()
            
            # Verify caches are cleared
            assert manager._cache == {}
            assert manager._metadata_cache == {}
            mock_load.cache_clear.assert_called_once()
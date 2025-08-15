"""
Test configuration loading and management functionality.
"""

import pytest
import os
import json
import tempfile
from unittest.mock import AsyncMock, patch
import sys

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.config_loader import ConfigurationLoader
from config.settings import MCPServerSettings


class TestConfigurationLoader:
    """Test cases for configuration loading functionality."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "version": "1.0.0",
            "name": "Test Configuration",
            "description": "Test model configuration",
            "models": [
                {
                    "name": "Test Llama",
                    "backend_type": "ollama",
                    "config": {
                        "base_url": "http://localhost:11434",
                        "model_name": "llama3.2:3b"
                    },
                    "description": "Test Llama model",
                    "capabilities": ["completion", "chat"]
                },
                {
                    "name": "Test BERT",
                    "backend_type": "huggingface",
                    "config": {
                        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                        "device": "cpu"
                    },
                    "description": "Test BERT model",
                    "capabilities": ["embedding"]
                }
            ],
            "backend_configs": {
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "timeout": 120
                },
                "huggingface": {
                    "cache_dir": "/tmp/models",
                    "device": "cpu"
                }
            }
        }

    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create a temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f, indent=2)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_load_configuration_from_file(self, temp_config_file, sample_config):
        """Test loading configuration from a file."""
        # Mock settings to use our temp file
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            config = await loader.load_configuration()
            
            assert config["name"] == sample_config["name"]
            assert len(config["models"]) == 2
            assert config["models"][0]["name"] == "Test Llama"
            assert config["models"][1]["name"] == "Test BERT"

    @pytest.mark.asyncio
    async def test_load_configuration_with_env_overrides(self, temp_config_file):
        """Test configuration loading with environment variable overrides."""
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = "http://custom-ollama:11434"
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = "/custom/cache"
            mock_settings.DEFAULT_OPENAI_API_URL = "http://custom-openai:8080/v1"
            
            loader = ConfigurationLoader()
            config = await loader.load_configuration()
            
            # Check that environment overrides were applied
            assert config["backend_configs"]["ollama"]["base_url"] == "http://custom-ollama:11434"
            assert config["backend_configs"]["huggingface"]["cache_dir"] == "/custom/cache"
            assert config["backend_configs"]["openai_compatible"]["base_url"] == "http://custom-openai:8080/v1"

    @pytest.mark.asyncio
    async def test_get_model_requests(self, temp_config_file):
        """Test converting configuration to model registration requests."""
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            requests = await loader.get_model_requests()
            
            assert len(requests) == 2
            assert requests[0].name == "Test Llama"
            assert requests[0].backend_type == "ollama"
            assert requests[1].name == "Test BERT"
            assert requests[1].backend_type == "huggingface"

    @pytest.mark.asyncio
    async def test_configuration_validation_invalid_backend(self, temp_config_file):
        """Test configuration validation with invalid backend type."""
        invalid_config = {
            "models": [
                {
                    "name": "Invalid Model",
                    "backend_type": "invalid_backend",
                    "config": {}
                }
            ]
        }
        
        # Write invalid configuration
        with open(temp_config_file, 'w') as f:
            json.dump(invalid_config, f)
        
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            
            with pytest.raises(ValueError, match="invalid backend_type"):
                await loader.load_configuration()

    @pytest.mark.asyncio
    async def test_configuration_validation_missing_fields(self, temp_config_file):
        """Test configuration validation with missing required fields."""
        invalid_config = {
            "models": [
                {
                    "backend_type": "ollama",
                    "config": {}
                    # Missing "name" field
                }
            ]
        }
        
        # Write invalid configuration
        with open(temp_config_file, 'w') as f:
            json.dump(invalid_config, f)
        
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            
            with pytest.raises(ValueError, match="missing required field"):
                await loader.load_configuration()

    @pytest.mark.asyncio
    async def test_load_configuration_file_not_found(self):
        """Test handling when configuration file doesn't exist."""
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = "/nonexistent/file.json"
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            config = await loader.load_configuration()
            
            # Should create default configuration
            assert "models" in config
            assert config["models"] == []
            assert "version" in config

    @pytest.mark.asyncio
    async def test_reload_configuration(self, temp_config_file, sample_config):
        """Test configuration reloading functionality."""
        with patch('services.config_loader.mcp_settings') as mock_settings:
            mock_settings.MODEL_CONFIG_PATH = temp_config_file
            mock_settings.MODEL_CONFIG_WATCH = False
            mock_settings.DEFAULT_OLLAMA_URL = None
            mock_settings.DEFAULT_HUGGINGFACE_CACHE = None
            mock_settings.DEFAULT_OPENAI_API_URL = None
            
            loader = ConfigurationLoader()
            
            # Initial load
            await loader.load_configuration()
            
            # Modify the file
            modified_config = sample_config.copy()
            modified_config["name"] = "Modified Configuration"
            
            with open(temp_config_file, 'w') as f:
                json.dump(modified_config, f, indent=2)
            
            # Reload should detect changes
            reloaded = await loader.reload_configuration()
            assert reloaded is True
            
            # Second reload without changes should return False
            reloaded = await loader.reload_configuration()
            assert reloaded is False


if __name__ == "__main__":
    pytest.main([__file__])
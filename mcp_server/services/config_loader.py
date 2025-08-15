"""
Configuration loader service for dynamic model management.

This module provides configuration loading and validation for models,
supporting JSON/YAML files and environment variable overrides.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
from datetime import datetime

try:
    from ..schemas.mcp_schemas import ModelRegistrationRequest
    from ..config.settings import mcp_settings
except ImportError:
    from schemas.mcp_schemas import ModelRegistrationRequest
    from config.settings import mcp_settings


logger = logging.getLogger(__name__)


class ConfigurationLoader:
    """
    Configuration loader for dynamic model management.
    
    Supports loading model configurations from files and environment variables,
    with optional file watching for dynamic updates.
    """
    
    def __init__(self):
        self._config_path = mcp_settings.MODEL_CONFIG_PATH
        self._watch_enabled = mcp_settings.MODEL_CONFIG_WATCH
        self._file_watcher_task = None
        self._last_modified = None
        self._config_cache = None
        
    async def initialize(self) -> None:
        """Initialize the configuration loader."""
        logger.info("Initializing configuration loader")
        
        # Load initial configuration
        await self.load_configuration()
        
        # Start file watcher if enabled
        if self._watch_enabled:
            await self._start_file_watcher()
    
    async def load_configuration(self) -> Dict[str, Any]:
        """
        Load configuration from file with environment variable overrides.
        
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # Load from file if it exists
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    config = json.load(f)
                
                # Update last modified time
                stat = os.stat(self._config_path)
                self._last_modified = stat.st_mtime
                
                logger.info(f"Loaded configuration from {self._config_path}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in configuration file {self._config_path}: {e}")
                raise ValueError(f"Configuration file contains invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {self._config_path}: {e}")
                raise
        else:
            logger.warning(f"Configuration file {self._config_path} not found, using defaults")
            # Create default configuration structure
            config = {
                "version": "1.0.0",
                "name": "Recaller MCP Server Configuration",
                "description": "Dynamic model configuration",
                "models": [],
                "backend_configs": {}
            }
        
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
        
        # Validate configuration
        self._validate_configuration(config)
        
        # Cache the configuration
        self._config_cache = config
        
        return config
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        
        # Initialize backend_configs if not present
        if "backend_configs" not in config:
            config["backend_configs"] = {}
        
        # Override default backend URLs from environment
        if mcp_settings.DEFAULT_OLLAMA_URL:
            if "ollama" not in config["backend_configs"]:
                config["backend_configs"]["ollama"] = {}
            config["backend_configs"]["ollama"]["base_url"] = mcp_settings.DEFAULT_OLLAMA_URL
        
        if mcp_settings.DEFAULT_HUGGINGFACE_CACHE:
            if "huggingface" not in config["backend_configs"]:
                config["backend_configs"]["huggingface"] = {}
            config["backend_configs"]["huggingface"]["cache_dir"] = mcp_settings.DEFAULT_HUGGINGFACE_CACHE
        
        if mcp_settings.DEFAULT_OPENAI_API_URL:
            if "openai_compatible" not in config["backend_configs"]:
                config["backend_configs"]["openai_compatible"] = {}
            config["backend_configs"]["openai_compatible"]["base_url"] = mcp_settings.DEFAULT_OPENAI_API_URL
        
        return config
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure and content.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check required top-level keys
        required_keys = ["models"]
        for key in required_keys:
            if key not in config:
                logger.warning(f"Configuration missing required key: {key}, adding default")
                config[key] = []
        
        # Validate models
        if not isinstance(config["models"], list):
            raise ValueError("Configuration 'models' must be a list")
        
        for i, model in enumerate(config["models"]):
            try:
                self._validate_model_config(model, i)
            except ValueError as e:
                raise ValueError(f"Invalid model configuration at index {i}: {e}")
        
        # Validate backend configs
        if "backend_configs" in config:
            if not isinstance(config["backend_configs"], dict):
                raise ValueError("Configuration 'backend_configs' must be a dictionary")
    
    def _validate_model_config(self, model: Dict[str, Any], index: int) -> None:
        """
        Validate individual model configuration.
        
        Args:
            model: Model configuration dictionary
            index: Model index for error reporting
        """
        required_fields = ["name", "backend_type"]
        for field in required_fields:
            if field not in model:
                raise ValueError(f"Model {index} missing required field: {field}")
        
        # Validate backend type
        valid_backends = ["ollama", "huggingface", "openai_compatible", "local_transformers"]
        if model["backend_type"] not in valid_backends:
            raise ValueError(f"Model {index} has invalid backend_type: {model['backend_type']}. "
                           f"Valid types: {valid_backends}")
        
        # Validate capabilities if present
        if "capabilities" in model:
            if not isinstance(model["capabilities"], list):
                raise ValueError(f"Model {index} capabilities must be a list")
            
            valid_capabilities = ["completion", "chat", "embedding", "classification"]
            for cap in model["capabilities"]:
                if cap not in valid_capabilities:
                    logger.warning(f"Model {index} has unknown capability: {cap}")
    
    async def get_model_requests(self) -> List[ModelRegistrationRequest]:
        """
        Convert configuration to model registration requests.
        
        Returns:
            List of model registration requests
        """
        if not self._config_cache:
            await self.load_configuration()
        
        requests = []
        
        for model_config in self._config_cache.get("models", []):
            try:
                # Create registration request from config
                request = ModelRegistrationRequest(
                    name=model_config["name"],
                    backend_type=model_config["backend_type"],
                    config=model_config.get("config", {}),
                    description=model_config.get("description"),
                    capabilities=model_config.get("capabilities", [])
                )
                requests.append(request)
                
            except Exception as e:
                logger.error(f"Failed to create registration request for model {model_config.get('name', 'unknown')}: {e}")
        
        return requests
    
    async def reload_configuration(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            True if configuration was reloaded, False if no changes detected
        """
        if not os.path.exists(self._config_path):
            logger.warning(f"Configuration file {self._config_path} not found for reload")
            return False
        
        # Check if file was modified
        stat = os.stat(self._config_path)
        if self._last_modified and stat.st_mtime <= self._last_modified:
            return False  # No changes
        
        logger.info("Configuration file changed, reloading...")
        
        try:
            await self.load_configuration()
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            raise
    
    async def _start_file_watcher(self) -> None:
        """Start file watcher for configuration changes."""
        if not os.path.exists(self._config_path):
            logger.info("Configuration file doesn't exist, file watcher will start when file is created")
            return
        
        self._file_watcher_task = asyncio.create_task(self._file_watcher_loop())
        logger.info(f"Started file watcher for {self._config_path}")
    
    async def _file_watcher_loop(self) -> None:
        """File watcher loop for configuration changes."""
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                if await self.reload_configuration():
                    logger.info("Configuration automatically reloaded due to file changes")
                    
            except Exception as e:
                logger.error(f"Error in file watcher: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._file_watcher_task:
            self._file_watcher_task.cancel()
            try:
                await self._file_watcher_task
            except asyncio.CancelledError:
                pass
            logger.info("File watcher stopped")


# Global configuration loader instance
config_loader = ConfigurationLoader()
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from functools import lru_cache
from datetime import datetime
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from app.models.configuration import ConfigurationCategory, ConfigurationType, ConfigurationValue
from app.core.config import settings

class ConfigMetadata(BaseModel):
    """Configuration file metadata structure"""
    version: str
    category: str
    type: str
    name: str
    description: str
    author: Optional[str] = "Recaller Team"
    last_updated: Optional[str] = None
    deprecated: bool = False

class ConfigurationManager:
    """Centralized configuration management service"""
    
    def __init__(self):
        self.config_root = Path(__file__).parent.parent.parent.parent / "config"
        self.shared_config_root = Path(__file__).parent.parent.parent.parent / "shared" / "config"
        self._cache = {}
        self._metadata_cache = {}
    
    @lru_cache(maxsize=50)
    def load_yaml_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file with caching"""
        full_path = self.config_root / f"{config_path}.yml"
        
        # Try shared config if not found in main config
        if not full_path.exists():
            full_path = self.shared_config_root / f"{config_path}.yml"
            
        if not full_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                
            # Validate metadata if present
            if 'metadata' in config_data or any(key in config_data for key in ['version', 'category', 'type']):
                self._validate_metadata(config_data, config_path)
                
            return config_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {e}")
    
    def _validate_metadata(self, config_data: Dict[str, Any], config_path: str):
        """Validate configuration metadata"""
        try:
            # Extract metadata from either 'metadata' key or root level
            metadata_dict = config_data.get('metadata', {})
            if not metadata_dict:
                # Try extracting from root level
                metadata_dict = {
                    'version': config_data.get('version'),
                    'category': config_data.get('category'),
                    'type': config_data.get('type'),
                    'name': config_data.get('name'),
                    'description': config_data.get('description'),
                    'author': config_data.get('author'),
                    'last_updated': config_data.get('last_updated'),
                    'deprecated': config_data.get('deprecated', False)
                }
            
            metadata = ConfigMetadata(**metadata_dict)
            self._metadata_cache[config_path] = metadata
            
        except Exception as e:
            print(f"Warning: Invalid metadata in {config_path}: {e}")
    
    def get_config(self, config_type: str, fallback_db: bool = True) -> Dict[str, Any]:
        """Get configuration with fallback to database"""
        try:
            # First try YAML
            return self.load_yaml_config(config_type)
        except FileNotFoundError:
            if fallback_db:
                # Fallback to database (Phase 2 implementation)
                return self._get_db_config(config_type)
            raise
    
    def _get_db_config(self, config_type: str) -> Dict[str, Any]:
        """Get configuration from database (Phase 2 placeholder)"""
        # This will be implemented in Phase 2
        return {}
    
    def get_config_with_db_fallback(
        self, 
        config_type: str, 
        db: Session = None, 
        tenant_id: int = None
    ) -> Dict[str, Any]:
        """Get configuration with database fallback and caching"""
        cache_key = f"{config_type}_{tenant_id}" if tenant_id else config_type
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Try YAML first
            config_data = self.load_yaml_config(config_type)
            self._cache[cache_key] = config_data
            return config_data
        except FileNotFoundError:
            # Fallback to database
            if db and tenant_id:
                from app.services.database_config_service import db_config_service
                config_data = db_config_service.get_database_config(db, config_type, tenant_id)
                if config_data:
                    self._cache[cache_key] = config_data
                    return config_data
            
            raise FileNotFoundError(f"Configuration '{config_type}' not found in YAML or database")

    def invalidate_cache(self, config_type: str = None, tenant_id: int = None):
        """Invalidate specific cache entries"""
        if config_type and tenant_id:
            cache_key = f"{config_type}_{tenant_id}"
            self._cache.pop(cache_key, None)
        elif config_type:
            # Remove all entries for this config type
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{config_type}_")]
            for key in keys_to_remove:
                self._cache.pop(key, None)
        else:
            # Clear all cache
            self.clear_cache()
    
    def get_config_metadata(self, config_type: str) -> Optional[ConfigMetadata]:
        """Get configuration metadata"""
        if config_type not in self._metadata_cache:
            try:
                self.load_yaml_config(config_type)
            except FileNotFoundError:
                return None
        
        return self._metadata_cache.get(config_type)
    
    def list_available_configs(self) -> List[Dict[str, Any]]:
        """List all available configuration files"""
        configs = []
        
        # Scan main config directory
        for yml_file in self.config_root.glob("*.yml"):
            config_name = yml_file.stem
            metadata = self.get_config_metadata(config_name)
            configs.append({
                'name': config_name,
                'path': str(yml_file),
                'source': 'main',
                'metadata': metadata.dict() if metadata else None
            })
        
        # Scan shared config directory
        for yml_file in self.shared_config_root.rglob("*.yml"):
            relative_path = yml_file.relative_to(self.shared_config_root)
            config_name = str(relative_path.with_suffix(''))
            metadata = self.get_config_metadata(config_name)
            configs.append({
                'name': config_name,
                'path': str(yml_file),
                'source': 'shared',
                'metadata': metadata.dict() if metadata else None
            })
        
        return configs
    
    def validate_config_structure(self, config_data: Dict[str, Any], schema_path: Optional[str] = None) -> bool:
        """Validate configuration against schema (future enhancement)"""
        # Placeholder for JSON schema validation
        return True
    
    def clear_cache(self):
        """Clear configuration cache"""
        self.load_yaml_config.cache_clear()
        self._cache.clear()
        self._metadata_cache.clear()

# Global instance
config_manager = ConfigurationManager()
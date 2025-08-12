"""Configuration management service for YAML sync and management."""

import os
import yaml
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.config import (
    ConfigCategory, ConfigType, ConfigValue, 
    ConfigValueTranslation, ConfigSyncHistory
)


class ConfigSyncService:
    """Service for synchronizing YAML configuration files with database."""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_base_path = Path(__file__).parent.parent.parent.parent / "shared" / "config" / "reference-data"
        
    def sync_all_configs(self, triggered_by: str = "command") -> Dict[str, Any]:
        """Sync all YAML configuration files to database."""
        sync_session_id = uuid.uuid4()
        results = {
            "sync_session_id": str(sync_session_id),
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "files": []
        }
        
        # Find all YAML files in the config directory
        for yaml_file in self.config_base_path.rglob("*.yml"):
            results["total_files"] += 1
            try:
                file_result = self.sync_config_file(yaml_file, sync_session_id, triggered_by)
                results["files"].append(file_result)
                if file_result["status"] == "success":
                    results["successful"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["files"].append({
                    "file": str(yaml_file),
                    "status": "failed",
                    "error": str(e)
                })
                
        return results
    
    def sync_config_file(self, file_path: Path, sync_session_id: uuid.UUID, triggered_by: str) -> Dict[str, Any]:
        """Sync a single YAML configuration file to database."""
        start_time = datetime.utcnow()
        
        try:
            # Load and validate YAML file
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            # Validate required fields
            required_fields = ['version', 'category', 'type', 'name', 'values']
            for field in required_fields:
                if field not in config_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Get or create category
            category = self._get_or_create_category(config_data)
            
            # Get or create config type
            config_type = self._get_or_create_config_type(config_data, category)
            
            # Sync values
            sync_result = self._sync_config_values(config_data, config_type, file_path)
            
            # Update sync info
            config_type.source_file = str(file_path)
            config_type.sync_version = config_data['version']
            config_type.last_sync_at = datetime.utcnow()
            
            # Record sync history
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._record_sync_history(
                sync_session_id, config_type, file_path, "sync", "success",
                sync_result, triggered_by, duration_ms
            )
            
            self.db.commit()
            
            return {
                "file": str(file_path),
                "status": "success",
                "category": config_data['category'],
                "type": config_data['type'],
                "records_processed": sync_result['processed'],
                "records_created": sync_result['created'],
                "records_updated": sync_result['updated']
            }
            
        except Exception as e:
            self.db.rollback()
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Try to record error in history
            try:
                self._record_sync_history(
                    sync_session_id, None, file_path, "sync", "failed",
                    {"error": str(e)}, triggered_by, duration_ms, errors=[str(e)]
                )
                self.db.commit()
            except:
                pass
                
            raise e
    
    def _get_or_create_category(self, config_data: Dict[str, Any]) -> ConfigCategory:
        """Get or create a configuration category."""
        category_key = config_data['category']
        
        category = self.db.query(ConfigCategory).filter(
            ConfigCategory.category_key == category_key
        ).first()
        
        if not category:
            category = ConfigCategory(
                category_key=category_key,
                name=category_key.replace('_', ' ').title(),
                description=f"Configuration category for {category_key}",
                sort_order=self._get_category_sort_order(category_key),
                is_active=True
            )
            self.db.add(category)
            self.db.flush()  # Get the ID
            
        return category
    
    def _get_or_create_config_type(self, config_data: Dict[str, Any], category: ConfigCategory) -> ConfigType:
        """Get or create a configuration type."""
        type_key = config_data['type']
        
        config_type = self.db.query(ConfigType).filter(
            and_(
                ConfigType.category_id == category.id,
                ConfigType.type_key == type_key
            )
        ).first()
        
        if not config_type:
            config_type = ConfigType(
                category_id=category.id,
                type_key=type_key,
                name=config_data.get('name', type_key.replace('_', ' ').title()),
                description=config_data.get('description'),
                data_type='hierarchical' if self._has_hierarchical_data(config_data) else 'enum',
                sort_order=0,
                is_active=True
            )
            self.db.add(config_type)
            self.db.flush()  # Get the ID
            
        else:
            # Update existing type
            config_type.name = config_data.get('name', config_type.name)
            config_type.description = config_data.get('description', config_type.description)
            
        return config_type
    
    def _sync_config_values(self, config_data: Dict[str, Any], config_type: ConfigType, file_path: Path) -> Dict[str, int]:
        """Sync configuration values for a config type."""
        result = {"processed": 0, "created": 0, "updated": 0}
        
        values = config_data.get('values', [])
        
        for value_data in values:
            result["processed"] += 1
            
            # Process main value
            is_new = self._process_config_value(value_data, config_type, None, 1, file_path)
            if is_new:
                result["created"] += 1
            else:
                result["updated"] += 1
                
            # Process children if they exist
            children = value_data.get('children', [])
            if children:
                parent_value = self.db.query(ConfigValue).filter(
                    and_(
                        ConfigValue.config_type_id == config_type.id,
                        ConfigValue.value_key == value_data['key']
                    )
                ).first()
                
                for child_data in children:
                    result["processed"] += 1
                    is_new = self._process_config_value(
                        child_data, config_type, parent_value.id, 2, file_path
                    )
                    if is_new:
                        result["created"] += 1
                    else:
                        result["updated"] += 1
        
        return result
    
    def _process_config_value(self, value_data: Dict[str, Any], config_type: ConfigType, 
                            parent_id: Optional[int], level: int, file_path: Path) -> bool:
        """Process a single configuration value. Returns True if created, False if updated."""
        value_key = value_data['key']
        
        # Check if value exists
        existing_value = self.db.query(ConfigValue).filter(
            and_(
                ConfigValue.config_type_id == config_type.id,
                ConfigValue.value_key == value_key,
                ConfigValue.tenant_id.is_(None)  # Global config
            )
        ).first()
        
        if existing_value:
            # Update existing value
            existing_value.display_name = value_data.get('display_name', value_key)
            existing_value.description = value_data.get('description')
            existing_value.parent_value_id = parent_id
            existing_value.level = level
            existing_value.extra_metadata = value_data.get('extra_metadata')
            existing_value.tags = value_data.get('tags')
            existing_value.sort_order = value_data.get('sort_order', 0)
            existing_value.is_system = value_data.get('is_system', False)
            existing_value.source_file = str(file_path)
            existing_value.last_sync_at = datetime.utcnow()
            
            return False
        else:
            # Create new value
            new_value = ConfigValue(
                config_type_id=config_type.id,
                value_key=value_key,
                display_name=value_data.get('display_name', value_key),
                description=value_data.get('description'),
                parent_value_id=parent_id,
                level=level,
                extra_metadata=value_data.get('extra_metadata'),
                tags=value_data.get('tags'),
                sort_order=value_data.get('sort_order', 0),
                is_active=True,
                is_system=value_data.get('is_system', False),
                source_file=str(file_path),
                last_sync_at=datetime.utcnow()
            )
            self.db.add(new_value)
            
            return True
    
    def _has_hierarchical_data(self, config_data: Dict[str, Any]) -> bool:
        """Check if configuration data has hierarchical structure."""
        values = config_data.get('values', [])
        return any('children' in value for value in values)
    
    def _get_category_sort_order(self, category_key: str) -> int:
        """Get sort order for category based on predefined hierarchy."""
        order_map = {
            'core': 1,
            'professional': 2,
            'social': 3,
            'contact': 4
        }
        return order_map.get(category_key, 99)
    
    def _record_sync_history(self, sync_session_id: uuid.UUID, config_type: Optional[ConfigType], 
                           file_path: Path, action: str, status: str, changes: Dict[str, Any],
                           triggered_by: str, duration_ms: int, errors: List[str] = None):
        """Record sync operation in history."""
        history = ConfigSyncHistory(
            sync_session_id=sync_session_id,
            config_type_id=config_type.id if config_type else None,
            source_file=str(file_path),
            sync_action=action,
            sync_status=status,
            changes_summary=changes,
            records_processed=changes.get('processed', 0),
            records_created=changes.get('created', 0),
            records_updated=changes.get('updated', 0),
            records_deleted=changes.get('deleted', 0),
            errors=errors,
            triggered_by=triggered_by,
            duration_ms=duration_ms
        )
        self.db.add(history)
    
    def get_config_values(self, category_key: str = None, type_key: str = None, 
                         tenant_id: int = None) -> List[Dict[str, Any]]:
        """Get configuration values with optional filtering."""
        query = self.db.query(ConfigValue).join(ConfigType).join(ConfigCategory)
        
        if category_key:
            query = query.filter(ConfigCategory.category_key == category_key)
        if type_key:
            query = query.filter(ConfigType.type_key == type_key)
        if tenant_id is not None:
            query = query.filter(
                (ConfigValue.tenant_id == tenant_id) | (ConfigValue.tenant_id.is_(None))
            )
        else:
            query = query.filter(ConfigValue.tenant_id.is_(None))
            
        query = query.filter(ConfigValue.is_active == True)
        query = query.order_by(ConfigValue.sort_order, ConfigValue.display_name)
        
        values = query.all()
        
        # Convert to dictionary format
        result = []
        for value in values:
            value_dict = {
                "id": value.id,
                "key": value.value_key,
                "display_name": value.display_name,
                "description": value.description,
                "level": value.level,
                "parent_id": value.parent_value_id,
                "metadata": value.extra_metadata,
                "tags": value.tags,
                "sort_order": value.sort_order,
                "is_system": value.is_system,
                "category": value.config_type.category.category_key,
                "type": value.config_type.type_key
            }
            result.append(value_dict)
            
        return result
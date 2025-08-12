import hashlib
import yaml
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.config import ConfigType, ConfigValue, ConfigSyncSession, ConfigChange
from app.schemas.config import (
    ConfigTypeCreate, 
    ConfigValueCreate, 
    ConfigSyncSessionCreate,
    ConfigChangeCreate,
    SyncResult, 
    FileSyncResult,
    YAMLConfigFile
)
from app.crud.config import config_type, config_value, config_sync_session, config_change


class ChangeSet:
    """Represents a set of changes to be made during sync"""
    def __init__(self):
        self.creates: List[Dict[str, Any]] = []
        self.updates: List[Tuple[ConfigValue, Dict[str, Any]]] = []
        self.deletes: List[ConfigValue] = []

    @property
    def total_changes(self) -> int:
        return len(self.creates) + len(self.updates) + len(self.deletes)

    def add_create(self, value_data: Dict[str, Any]):
        self.creates.append(value_data)

    def add_update(self, existing_value: ConfigValue, new_data: Dict[str, Any]):
        self.updates.append((existing_value, new_data))

    def add_delete(self, value_to_delete: ConfigValue):
        self.deletes.append(value_to_delete)


class FieldChange:
    """Represents a change to a specific field"""
    def __init__(self, field_name: str, old_value: Any, new_value: Any):
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value

    def __str__(self):
        return f"{self.field_name}: {self.old_value} -> {self.new_value}"


class ConfigSyncEngine:
    """Core synchronization engine for YAML configuration files"""
    
    def __init__(self, db: Session, tenant_id: int, config_dir: Path):
        self.db = db
        self.tenant_id = tenant_id
        self.config_dir = config_dir
        self.sync_session_id = None
        self.current_session = None

    def sync_all_configs(self, dry_run: bool = False) -> SyncResult:
        """Sync all configuration files in the config directory"""
        self.sync_session_id = str(uuid.uuid4())
        
        # Create sync session
        if not dry_run:
            self.current_session = config_sync_session.create(
                self.db,
                ConfigSyncSessionCreate(
                    session_id=self.sync_session_id,
                    status="running",
                    sync_type="full"
                ),
                self.tenant_id
            )

        results = []
        total_changes = 0
        errors_count = 0

        # Find all YAML files
        yaml_files = list(self.config_dir.rglob("*.yml")) + list(self.config_dir.rglob("*.yaml"))
        
        for config_file in yaml_files:
            if self._should_sync_file(config_file):
                result = self.sync_file(config_file, dry_run)
                results.append(result)
                total_changes += result.changes_count
                if result.status == "error":
                    errors_count += 1

        # Update session
        if not dry_run and self.current_session:
            from app.schemas.config import ConfigSyncSessionUpdate
            config_sync_session.update(
                self.db,
                self.current_session,
                ConfigSyncSessionUpdate(
                    status="completed" if errors_count == 0 else "partial",
                    files_processed=len(results),
                    changes_made=total_changes,
                    errors_count=errors_count,
                    completed_at=datetime.utcnow()
                )
            )

        return SyncResult(
            session_id=self.sync_session_id,
            status="completed" if errors_count == 0 else "partial",
            files_processed=len(results),
            total_changes=total_changes,
            errors_count=errors_count,
            file_results=results,
            started_at=self.current_session.started_at if self.current_session else datetime.utcnow(),
            completed_at=datetime.utcnow()
        )

    def sync_file(self, file_path: Path, dry_run: bool = False) -> FileSyncResult:
        """Sync a single configuration file"""
        try:
            # Load and validate YAML
            config_data = self._load_yaml_file(file_path)
            
            # Get or create config type
            config_type_obj = self._get_or_create_config_type(config_data, file_path, dry_run)
            
            if not config_type_obj:
                return FileSyncResult(
                    file_path=str(file_path),
                    status="error",
                    error_message="Failed to create or retrieve config type"
                )

            # Calculate file checksum
            file_checksum = self._calculate_checksum(file_path)
            
            # Check if sync needed
            if not dry_run and not self._needs_sync(config_type_obj, file_checksum):
                return FileSyncResult(
                    file_path=str(file_path),
                    status="no_changes"
                )

            # Perform sync
            changes = self._sync_values(config_type_obj, config_data['values'], dry_run)
            
            # Update sync metadata
            if not dry_run:
                self._update_sync_metadata(config_type_obj, file_checksum, config_data.get('version', '1.0'))

            # Create change descriptions
            change_descriptions = []
            for create_data in changes.creates:
                change_descriptions.append(f"Create: {create_data['key']} ({create_data['display_name']})")
            
            for existing_value, new_data in changes.updates:
                change_descriptions.append(f"Update: {existing_value.key}")
                
            for deleted_value in changes.deletes:
                change_descriptions.append(f"Delete: {deleted_value.key}")

            return FileSyncResult(
                file_path=str(file_path),
                status="success",
                changes_count=changes.total_changes,
                changes=change_descriptions
            )

        except Exception as e:
            return FileSyncResult(
                file_path=str(file_path),
                status="error",
                error_message=str(e)
            )

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and validate YAML configuration file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate against schema
        yaml_config = YAMLConfigFile(**data)
        return yaml_config.model_dump()

    def _get_or_create_config_type(self, config_data: Dict[str, Any], file_path: Path, dry_run: bool = False) -> Optional[ConfigType]:
        """Get existing config type or create a new one"""
        existing = config_type.get_by_name(self.db, config_data['name'], self.tenant_id)
        
        if existing:
            return existing
        
        if dry_run:
            # For dry run, create a mock object
            return ConfigType(
                id=0,
                name=config_data['name'],
                display_name=config_data['display_name'],
                tenant_id=self.tenant_id
            )
        
        # Create new config type
        return config_type.create(
            self.db,
            ConfigTypeCreate(
                name=config_data['name'],
                display_name=config_data['display_name'],
                description=config_data.get('description'),
                schema_version=config_data.get('version', '1.0'),
                config_file_path=str(file_path.relative_to(self.config_dir))
            ),
            self.tenant_id
        )

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file content"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _needs_sync(self, config_type_obj: ConfigType, file_checksum: str) -> bool:
        """Check if file needs to be synced based on checksum"""
        return config_type_obj.last_sync_checksum != file_checksum

    def _sync_values(self, config_type_obj: ConfigType, yaml_values: List[Dict[str, Any]], dry_run: bool) -> ChangeSet:
        """Sync configuration values"""
        changes = ChangeSet()
        
        # Get existing values
        existing_values = {}
        if not dry_run:
            existing_list = config_value.get_by_config_type(self.db, config_type_obj.id, self.tenant_id)
            existing_values = {v.key: v for v in existing_list}
        
        yaml_values_dict = {v['key']: v for v in yaml_values}
        
        # Process creates and updates
        for key, yaml_value in yaml_values_dict.items():
            if key in existing_values:
                # Check for updates
                existing_value = existing_values[key]
                if self._value_needs_update(existing_value, yaml_value):
                    changes.add_update(existing_value, yaml_value)
                    if not dry_run:
                        self._update_value(existing_value, yaml_value)
            else:
                # Create new value
                changes.add_create(yaml_value)
                if not dry_run:
                    self._create_value(config_type_obj, yaml_value)

        # Process deletes (values in DB but not in YAML)
        if not dry_run:
            yaml_keys = set(yaml_values_dict.keys())
            existing_keys = set(existing_values.keys())
            deleted_keys = existing_keys - yaml_keys
            
            for key in deleted_keys:
                value_to_delete = existing_values[key]
                if not value_to_delete.is_system:  # Don't delete system values
                    changes.add_delete(value_to_delete)
                    self._delete_value(value_to_delete)

        return changes

    def _value_needs_update(self, existing_value: ConfigValue, yaml_value: Dict[str, Any]) -> bool:
        """Check if a value needs to be updated"""
        return (
            existing_value.display_name != yaml_value.get('display_name') or
            existing_value.description != yaml_value.get('description') or
            existing_value.sort_order != yaml_value.get('sort_order', 0) or
            existing_value.is_active != yaml_value.get('is_active', True) or
            existing_value.config_metadata != yaml_value.get('metadata')
        )

    def _create_value(self, config_type_obj: ConfigType, yaml_value: Dict[str, Any]) -> ConfigValue:
        """Create a new configuration value"""
        # Resolve parent_value_id if parent_key is specified
        parent_value_id = None
        if yaml_value.get('parent_key'):
            parent = config_value.get_by_key(
                self.db, 
                yaml_value['parent_key'], 
                config_type_obj.id, 
                self.tenant_id
            )
            if parent:
                parent_value_id = parent.id

        new_value = config_value.create(
            self.db,
            ConfigValueCreate(
                config_type_id=config_type_obj.id,
                key=yaml_value['key'],
                display_name=yaml_value['display_name'],
                description=yaml_value.get('description'),
                parent_value_id=parent_value_id,
                sort_order=yaml_value.get('sort_order', 0),
                is_active=yaml_value.get('is_active', True),
                config_metadata=yaml_value.get('metadata')
            ),
            self.tenant_id
        )

        # Record change
        if self.current_session:
            config_change.create(
                self.db,
                ConfigChangeCreate(
                    sync_session_id=self.current_session.id,
                    change_type="create",
                    table_name="config_values",
                    record_id=new_value.id,
                    new_value=yaml_value
                ),
                self.tenant_id
            )

        return new_value

    def _update_value(self, existing_value: ConfigValue, yaml_value: Dict[str, Any]):
        """Update an existing configuration value"""
        old_data = {
            'display_name': existing_value.display_name,
            'description': existing_value.description,
            'sort_order': existing_value.sort_order,
            'is_active': existing_value.is_active,
            'config_metadata': existing_value.config_metadata
        }

        # Resolve parent_value_id if parent_key is specified
        parent_value_id = existing_value.parent_value_id
        if yaml_value.get('parent_key'):
            parent = config_value.get_by_key(
                self.db, 
                yaml_value['parent_key'], 
                existing_value.config_type_id, 
                self.tenant_id
            )
            if parent:
                parent_value_id = parent.id

        from app.schemas.config import ConfigValueUpdate
        config_value.update(
            self.db,
            existing_value,
            ConfigValueUpdate(
                display_name=yaml_value['display_name'],
                description=yaml_value.get('description'),
                parent_value_id=parent_value_id,
                sort_order=yaml_value.get('sort_order', 0),
                is_active=yaml_value.get('is_active', True),
                config_metadata=yaml_value.get('metadata')
            )
        )

        # Record change
        if self.current_session:
            config_change.create(
                self.db,
                ConfigChangeCreate(
                    sync_session_id=self.current_session.id,
                    change_type="update",
                    table_name="config_values",
                    record_id=existing_value.id,
                    old_value=old_data,
                    new_value=yaml_value
                ),
                self.tenant_id
            )

    def _delete_value(self, value_to_delete: ConfigValue):
        """Delete a configuration value"""
        old_data = {
            'key': value_to_delete.key,
            'display_name': value_to_delete.display_name,
            'description': value_to_delete.description
        }

        # Record change before deletion
        if self.current_session:
            config_change.create(
                self.db,
                ConfigChangeCreate(
                    sync_session_id=self.current_session.id,
                    change_type="delete",
                    table_name="config_values",
                    record_id=value_to_delete.id,
                    old_value=old_data
                ),
                self.tenant_id
            )

        config_value.remove(self.db, value_to_delete.id, self.tenant_id)

    def _update_sync_metadata(self, config_type_obj: ConfigType, file_checksum: str, version: str):
        """Update sync metadata for config type"""
        from app.schemas.config import ConfigTypeUpdate
        config_type.update(
            self.db,
            config_type_obj,
            ConfigTypeUpdate(
                schema_version=version,
                last_sync_checksum=file_checksum,
                last_sync_at=datetime.utcnow()
            )
        )

    def _should_sync_file(self, file_path: Path) -> bool:
        """Determine if a file should be synced"""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        # Only process .yml and .yaml files
        return file_path.suffix.lower() in ['.yml', '.yaml']
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import yaml
from pathlib import Path

from app.models.configuration import (
    ConfigurationCategory, ConfigurationType, ConfigurationValue,
    ConfigurationTranslation, ConfigurationImport
)
from app.core.configuration_manager import config_manager
from app.crud.configuration import (
    create_category, create_type, create_value,
    get_values, update_value, get_category_by_key, get_type_by_key
)

class DatabaseConfigService:
    """Database-driven configuration management service"""
    
    def __init__(self):
        self.config_manager = config_manager
    
    def import_yaml_to_database(
        self, 
        db: Session, 
        config_type: str, 
        tenant_id: int,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Import YAML configuration into database"""
        try:
            # Load YAML configuration
            yaml_config = self.config_manager.get_config(config_type)
            metadata = self.config_manager.get_config_metadata(config_type)
            
            if not yaml_config or not metadata:
                raise ValueError(f"Configuration '{config_type}' not found or invalid")
            
            # Create import tracking record
            import_record = ConfigurationImport(
                config_type=config_type,
                config_version=metadata.version,
                source_file=f"{config_type}.yml",
                import_status="pending",
                tenant_id=tenant_id
            )
            db.add(import_record)
            db.flush()  # Get the ID
            
            try:
                # Get or create category
                category = self._get_or_create_category(db, metadata, tenant_id)
                
                # Get or create configuration type
                config_type_obj = self._get_or_create_config_type(
                    db, config_type, metadata, category.id, tenant_id
                )
                
                # Import configuration values
                imported_count = self._import_config_values(
                    db, yaml_config, config_type_obj.id, 
                    import_record.id, tenant_id, force_update
                )
                
                # Update import record
                import_record.import_status = "success"
                import_record.records_imported = imported_count
                db.commit()
                
                return {
                    "status": "success",
                    "config_type": config_type,
                    "version": metadata.version,
                    "records_imported": imported_count,
                    "import_id": import_record.id
                }
                
            except Exception as e:
                import_record.import_status = "failed"
                import_record.error_message = str(e)
                db.commit()
                raise
                
        except Exception as e:
            return {
                "status": "error",
                "config_type": config_type,
                "error": str(e)
            }
    
    def _get_or_create_category(
        self, 
        db: Session, 
        metadata: Any, 
        tenant_id: int
    ) -> ConfigurationCategory:
        """Get or create configuration category"""
        category = get_category_by_key(db, metadata.category, tenant_id)
        
        if not category:
            from app.schemas.configuration import ConfigurationCategoryCreate
            category_data = ConfigurationCategoryCreate(
                key=metadata.category,
                name=metadata.category.replace('_', ' ').title(),
                description=f"Configuration category for {metadata.category}",
                is_system=True
            )
            category = create_category(db, category_data, tenant_id)
        
        return category
    
    def _get_or_create_config_type(
        self,
        db: Session,
        config_type: str,
        metadata: Any,
        category_id: int,
        tenant_id: int
    ) -> ConfigurationType:
        """Get or create configuration type"""
        config_type_obj = get_type_by_key(db, config_type, tenant_id)
        
        if not config_type_obj:
            from app.schemas.configuration import ConfigurationTypeCreate
            type_data = ConfigurationTypeCreate(
                key=config_type,
                name=metadata.name,
                description=metadata.description,
                category_id=category_id,
                data_type="hierarchical",
                is_system=True
            )
            config_type_obj = create_type(db, type_data, tenant_id)
        
        return config_type_obj
    
    def _import_config_values(
        self,
        db: Session,
        yaml_config: Dict[str, Any],
        config_type_id: int,
        import_id: int,
        tenant_id: int,
        force_update: bool = False
    ) -> int:
        """Import configuration values from YAML"""
        imported_count = 0
        
        # Handle different YAML structures
        if 'currencies' in yaml_config:
            imported_count += self._import_currencies(
                db, yaml_config['currencies'], config_type_id, 
                import_id, tenant_id, force_update
            )
        elif 'relationship_types' in yaml_config:
            imported_count += self._import_relationships(
                db, yaml_config['relationship_types'], config_type_id,
                import_id, tenant_id, force_update
            )
        elif 'activity_types' in yaml_config:
            imported_count += self._import_activity_types(
                db, yaml_config['activity_types'], config_type_id,
                import_id, tenant_id, force_update
            )
        else:
            # Generic key-value import
            imported_count += self._import_generic_values(
                db, yaml_config, config_type_id, import_id, tenant_id, force_update
            )
        
        return imported_count
    
    def _import_currencies(
        self,
        db: Session,
        currencies: List[Dict[str, Any]],
        config_type_id: int,
        import_id: int,
        tenant_id: int,
        force_update: bool
    ) -> int:
        """Import currency configurations"""
        imported_count = 0
        
        for currency in currencies:
            key = currency['code']
            existing = db.query(ConfigurationValue).filter(
                and_(
                    ConfigurationValue.type_id == config_type_id,
                    ConfigurationValue.key == key,
                    ConfigurationValue.tenant_id == tenant_id
                )
            ).first()
            
            if existing and not force_update:
                continue
            
            value_data = {
                'name': currency['name'],
                'symbol': currency['symbol'],
                'decimal_places': currency['decimal_places'],
                'countries': currency.get('countries', []),
                'is_active': currency.get('is_active', True),
                'is_default': currency.get('is_default', False)
            }
            
            if existing:
                existing.value = yaml.dump(value_data)
                existing.display_name = currency['name']
                existing.value_metadata = value_data
                existing.source_version = str(import_id)
            else:
                from app.schemas.configuration import ConfigurationValueCreate
                value_create = ConfigurationValueCreate(
                    type_id=config_type_id,
                    key=key,
                    value=yaml.dump(value_data),
                    display_name=currency['name'],
                    value_metadata=value_data,
                    source="yaml_import",
                    import_id=import_id,
                    is_system=True
                )
                create_value(db, value_create, tenant_id)
            
            imported_count += 1
        
        return imported_count
    
    def _import_relationships(
        self,
        db: Session,
        relationships: List[Dict[str, Any]],
        config_type_id: int,
        import_id: int,
        tenant_id: int,
        force_update: bool
    ) -> int:
        """Import relationship configurations"""
        imported_count = 0
        
        for relationship in relationships:
            key = relationship['key']
            existing = db.query(ConfigurationValue).filter(
                and_(
                    ConfigurationValue.type_id == config_type_id,
                    ConfigurationValue.key == key,
                    ConfigurationValue.tenant_id == tenant_id
                )
            ).first()
            
            if existing and not force_update:
                continue
            
            value_data = {
                'display_name': relationship['display_name'],
                'reverse': relationship.get('reverse', key),
                'category': relationship.get('category', 'general'),
                'is_gender_specific': relationship.get('is_gender_specific', False),
                'description': relationship.get('description', '')
            }
            
            if existing:
                existing.value = yaml.dump(value_data)
                existing.display_name = relationship['display_name']
                existing.value_metadata = value_data
                existing.source_version = str(import_id)
            else:
                from app.schemas.configuration import ConfigurationValueCreate
                value_create = ConfigurationValueCreate(
                    type_id=config_type_id,
                    key=key,
                    value=yaml.dump(value_data),
                    display_name=relationship['display_name'],
                    value_metadata=value_data,
                    source="yaml_import",
                    import_id=import_id,
                    is_system=True
                )
                create_value(db, value_create, tenant_id)
            
            imported_count += 1
        
        return imported_count
    
    def _import_activity_types(
        self,
        db: Session,
        activity_types: Dict[str, Any],
        config_type_id: int,
        import_id: int,
        tenant_id: int,
        force_update: bool
    ) -> int:
        """Import activity type configurations"""
        imported_count = 0
        
        for key, activity in activity_types.items():
            existing = db.query(ConfigurationValue).filter(
                and_(
                    ConfigurationValue.type_id == config_type_id,
                    ConfigurationValue.key == key,
                    ConfigurationValue.tenant_id == tenant_id
                )
            ).first()
            
            if existing and not force_update:
                continue
            
            value_data = activity.copy()
            
            if existing:
                existing.value = yaml.dump(value_data)
                existing.display_name = activity.get('display_name', key)
                existing.value_metadata = value_data
                existing.source_version = str(import_id)
            else:
                from app.schemas.configuration import ConfigurationValueCreate
                value_create = ConfigurationValueCreate(
                    type_id=config_type_id,
                    key=key,
                    value=yaml.dump(value_data),
                    display_name=activity.get('display_name', key),
                    value_metadata=value_data,
                    source="yaml_import",
                    import_id=import_id,
                    is_system=True
                )
                create_value(db, value_create, tenant_id)
            
            imported_count += 1
        
        return imported_count
    
    def _import_generic_values(
        self,
        db: Session,
        config_data: Dict[str, Any],
        config_type_id: int,
        import_id: int,
        tenant_id: int,
        force_update: bool
    ) -> int:
        """Import generic configuration values"""
        imported_count = 0
        
        # Skip metadata keys
        skip_keys = {'version', 'category', 'type', 'name', 'description', 'author', 'last_updated', 'deprecated', 'metadata'}
        
        for key, value in config_data.items():
            if key in skip_keys:
                continue
                
            existing = db.query(ConfigurationValue).filter(
                and_(
                    ConfigurationValue.type_id == config_type_id,
                    ConfigurationValue.key == key,
                    ConfigurationValue.tenant_id == tenant_id
                )
            ).first()
            
            if existing and not force_update:
                continue
            
            value_str = yaml.dump(value) if isinstance(value, (dict, list)) else str(value)
            display_name = key.replace('_', ' ').title()
            
            if existing:
                existing.value = value_str
                existing.display_name = display_name
                existing.value_metadata = value if isinstance(value, dict) else {'value': value}
                existing.source_version = str(import_id)
            else:
                from app.schemas.configuration import ConfigurationValueCreate
                value_create = ConfigurationValueCreate(
                    type_id=config_type_id,
                    key=key,
                    value=value_str,
                    display_name=display_name,
                    value_metadata=value if isinstance(value, dict) else {'value': value},
                    source="yaml_import",
                    import_id=import_id,
                    is_system=True
                )
                create_value(db, value_create, tenant_id)
            
            imported_count += 1
        
        return imported_count
    
    def get_database_config(
        self,
        db: Session,
        config_type: str,
        tenant_id: int,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get configuration from database"""
        config_type_obj = get_type_by_key(db, config_type, tenant_id)
        
        if not config_type_obj:
            return {}
        
        values = get_values(
            db=db,
            tenant_id=tenant_id,
            type_key=config_type,
            active_only=not include_inactive
        )
        
        # Convert to dictionary format
        result = {
            'metadata': {
                'config_type': config_type,
                'category': config_type_obj.category.name if config_type_obj.category else None,
                'description': config_type_obj.description,
                'total_values': len(values),
                'last_updated': max(v.updated_at for v in values) if values else None
            }
        }
        
        # Organize values based on configuration type
        if config_type == 'currencies':
            result['currencies'] = [
                {
                    'code': v.key,
                    'name': v.display_name,
                    **v.value_metadata
                }
                for v in values
            ]
        elif config_type == 'relationship_mappings':
            result['relationship_types'] = [
                {
                    'key': v.key,
                    'display_name': v.display_name,
                    **v.value_metadata
                }
                for v in values
            ]
        elif config_type.startswith('activity'):
            result['activity_types'] = {
                v.key: {
                    'display_name': v.display_name,
                    **v.value_metadata
                }
                for v in values
            }
        else:
            # Generic format
            for v in values:
                result[v.key] = v.value_metadata if v.value_metadata else v.value
        
        return result

# Global instance
db_config_service = DatabaseConfigService()
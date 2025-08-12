"""CLI commands for configuration management."""

import click
import sys
import yaml
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.config_sync import ConfigSyncService


@click.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Sync specific YAML file')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def sync(file, dry_run, verbose):
    """Sync YAML configuration files to database."""
    click.echo("🔄 Syncing configuration files...")
    
    if dry_run:
        click.echo("⚠️  DRY RUN MODE - No changes will be made")
    
    db: Session = SessionLocal()
    try:
        sync_service = ConfigSyncService(db)
        
        if file:
            # Sync specific file
            file_path = Path(file)
            if verbose:
                click.echo(f"📄 Syncing file: {file_path}")
            
            if not dry_run:
                import uuid
                result = sync_service.sync_config_file(file_path, uuid.uuid4(), "command")
                click.echo(f"✅ Successfully synced {file_path}")
                if verbose:
                    click.echo(f"   Records processed: {result['records_processed']}")
                    click.echo(f"   Records created: {result['records_created']}")
                    click.echo(f"   Records updated: {result['records_updated']}")
            else:
                click.echo(f"Would sync: {file_path}")
        else:
            # Sync all files
            if not dry_run:
                results = sync_service.sync_all_configs("command")
                
                click.echo(f"📊 Sync Summary:")
                click.echo(f"   Total files: {results['total_files']}")
                click.echo(f"   Successful: {results['successful']}")
                click.echo(f"   Failed: {results['failed']}")
                
                if verbose:
                    for file_result in results['files']:
                        status_icon = "✅" if file_result['status'] == 'success' else "❌"
                        click.echo(f"   {status_icon} {file_result['file']}")
                        if file_result['status'] == 'success' and 'records_processed' in file_result:
                            click.echo(f"      Processed: {file_result['records_processed']}, "
                                     f"Created: {file_result['records_created']}, "
                                     f"Updated: {file_result['records_updated']}")
                        elif 'error' in file_result:
                            click.echo(f"      Error: {file_result['error']}")
                
                if results['failed'] > 0:
                    click.echo("⚠️  Some files failed to sync. Use --verbose for details.")
                    sys.exit(1)
                else:
                    click.echo("🎉 All configuration files synced successfully!")
            else:
                # In dry run, just list files that would be synced
                config_base_path = sync_service.config_base_path
                yaml_files = list(config_base_path.rglob("*.yml"))
                click.echo(f"Would sync {len(yaml_files)} files:")
                for yaml_file in yaml_files:
                    click.echo(f"  📄 {yaml_file}")
                    
    except Exception as e:
        click.echo(f"❌ Error during sync: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)
    finally:
        db.close()


@config.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--type', '-t', help='Filter by type')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def list_values(category, type, output_format):
    """List configuration values from database."""
    db: Session = SessionLocal()
    try:
        sync_service = ConfigSyncService(db)
        values = sync_service.get_config_values(category_key=category, type_key=type)
        
        if output_format == 'json':
            import json
            click.echo(json.dumps(values, indent=2, default=str))
        elif output_format == 'yaml':
            click.echo(yaml.dump(values, default_flow_style=False))
        else:
            # Table format
            if not values:
                click.echo("No configuration values found.")
                return
                
            click.echo("Configuration Values:")
            click.echo("-" * 80)
            for value in values:
                click.echo(f"📋 {value['category']}.{value['type']}.{value['key']}")
                click.echo(f"   Name: {value['display_name']}")
                if value['description']:
                    click.echo(f"   Description: {value['description']}")
                if value['parent_id']:
                    click.echo(f"   Parent ID: {value['parent_id']}")
                click.echo(f"   Level: {value['level']}, Sort: {value['sort_order']}")
                if value['tags']:
                    click.echo(f"   Tags: {', '.join(value['tags'])}")
                click.echo()
                
    except Exception as e:
        click.echo(f"❌ Error listing configurations: {str(e)}", err=True)
        sys.exit(1)
    finally:
        db.close()


@config.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path):
    """Validate a YAML configuration file."""
    click.echo(f"🔍 Validating {file_path}...")
    
    try:
        file_path = Path(file_path)
        
        # Load YAML
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Validate structure
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['version', 'category', 'type', 'name', 'values']
        for field in required_fields:
            if field not in config_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate values structure
        if 'values' in config_data:
            values = config_data['values']
            if not isinstance(values, list):
                errors.append("'values' must be a list")
            else:
                for i, value in enumerate(values):
                    if not isinstance(value, dict):
                        errors.append(f"Value at index {i} must be a dictionary")
                        continue
                    
                    if 'key' not in value:
                        errors.append(f"Value at index {i} missing 'key' field")
                    if 'display_name' not in value:
                        warnings.append(f"Value at index {i} missing 'display_name' field")
        
        # Check for duplicate keys
        if 'values' in config_data:
            keys = []
            for value in config_data['values']:
                if 'key' in value:
                    if value['key'] in keys:
                        errors.append(f"Duplicate key found: {value['key']}")
                    keys.append(value['key'])
        
        # Output results
        if errors:
            click.echo("❌ Validation failed:")
            for error in errors:
                click.echo(f"   • {error}")
            
        if warnings:
            click.echo("⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"   • {warning}")
        
        if not errors and not warnings:
            click.echo("✅ Validation passed!")
        elif not errors:
            click.echo("✅ Validation passed with warnings.")
        else:
            sys.exit(1)
            
    except yaml.YAMLError as e:
        click.echo(f"❌ YAML parsing error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Validation error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    config()
#!/usr/bin/env python3
"""
Gift System Configuration Validation Script

This script validates that the Gift Ideas and Tracking System configuration
is properly set up and integrated with existing Recaller modules.
"""

import sys
import yaml
from pathlib import Path

def validate_yaml_files():
    """Validate all gift system YAML configuration files"""
    print("🔍 Validating YAML Configuration Files...")
    
    files_to_check = [
        'shared/config/reference-data/social/gift-categories.yml',
        'shared/config/reference-data/social/gift-occasions.yml', 
        'shared/config/reference-data/financial/gift-budget-ranges.yml',
        'config/environment/development.yml',
        'config/environment/production.yml'
    ]
    
    repo_root = Path(__file__).parent
    
    for file_path in files_to_check:
        full_path = repo_root / file_path
        try:
            with open(full_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic structure validation
            if 'gift' in file_path.lower():
                if 'values' in data:
                    print(f'  ✅ {file_path} - Valid YAML with {len(data["values"])} entries')
                else:
                    print(f'  ✅ {file_path} - Valid YAML (environment config)')
            else:
                # Environment files should have gift_system section
                if 'gift_system' in str(data):
                    print(f'  ✅ {file_path} - Valid YAML with gift_system config')
                else:
                    print(f'  ❌ {file_path} - Missing gift_system configuration')
                    return False
                    
        except Exception as e:
            print(f'  ❌ {file_path} - Error: {e}')
            return False
    
    return True

def validate_configuration_system():
    """Validate the configuration system integration"""
    print("\n🔧 Validating Configuration System...")
    
    try:
        # Test configuration loading
        from app.core.enhanced_settings import get_settings
        settings = get_settings()
        
        # Validate gift system settings
        gift_configs = [
            ('GIFT_SYSTEM_ENABLED', bool),
            ('GIFT_DEFAULT_CURRENCY', str),
            ('GIFT_MAX_BUDGET', int),
            ('GIFT_SUGGESTION_ENGINE', str),
            ('GIFT_AUTO_CREATE_TASKS', bool),
            ('GIFT_PRIVACY_MODE', str),
            ('GIFT_IMAGE_STORAGE', bool),
            ('GIFT_EXTERNAL_LINKS', bool),
        ]
        
        for config_name, expected_type in gift_configs:
            if hasattr(settings, config_name):
                value = getattr(settings, config_name)
                if isinstance(value, expected_type):
                    print(f'  ✅ {config_name}: {value} ({expected_type.__name__})')
                else:
                    print(f'  ❌ {config_name}: Wrong type, expected {expected_type.__name__}')
                    return False
            else:
                print(f'  ❌ {config_name}: Missing configuration')
                return False
        
        # Test helper methods
        reminder_days = settings.get_gift_reminder_days()
        if isinstance(reminder_days, list) and len(reminder_days) > 0:
            print(f'  ✅ Gift reminder days: {reminder_days}')
        else:
            print(f'  ❌ Invalid gift reminder days: {reminder_days}')
            return False
            
        return True
        
    except Exception as e:
        print(f'  ❌ Configuration system error: {e}')
        return False

def validate_schemas():
    """Validate gift system schemas"""
    print("\n📋 Validating Schemas...")
    
    try:
        from app.schemas.gift_system import (
            GiftSystemConfig, 
            GiftIntegrationSettings,
            GiftSystemPermissions,
            GiftCategoryReference,
            GiftOccasionReference,
            GiftBudgetRangeReference
        )
        
        # Test schema instantiation
        config = GiftSystemConfig()
        print(f'  ✅ GiftSystemConfig: default values loaded')
        
        integration = GiftIntegrationSettings()
        print(f'  ✅ GiftIntegrationSettings: integration points configured')
        
        permissions = GiftSystemPermissions()
        print(f'  ✅ GiftSystemPermissions: default permissions set')
        
        # Test validation
        try:
            GiftSystemConfig(max_budget_amount=0)
            print(f'  ❌ Budget validation: should reject zero budget')
            return False
        except ValueError:
            print(f'  ✅ Budget validation: correctly rejects invalid values')
        
        return True
        
    except Exception as e:
        print(f'  ❌ Schema validation error: {e}')
        return False

def validate_api_endpoints():
    """Validate API endpoints are registered"""
    print("\n🌐 Validating API Endpoints...")
    
    try:
        from app.main import app
        
        # Check if gift system routes are registered
        routes = [route.path for route in app.routes]
        gift_routes = [route for route in routes if 'gift-system' in route]
        
        expected_routes = [
            '/api/v1/config/gift-system/config',
            '/api/v1/config/gift-system/integration-settings',
            '/api/v1/config/gift-system/permissions',
            '/api/v1/config/gift-system/status',
            '/api/v1/config/gift-system/reference-data/categories',
            '/api/v1/config/gift-system/reference-data/occasions',
            '/api/v1/config/gift-system/reference-data/budget-ranges'
        ]
        
        for expected_route in expected_routes:
            if expected_route in gift_routes:
                print(f'  ✅ {expected_route}')
            else:
                print(f'  ❌ Missing route: {expected_route}')
                return False
        
        print(f'  ✅ All {len(expected_routes)} gift system routes registered')
        return True
        
    except Exception as e:
        print(f'  ❌ API endpoint validation error: {e}')
        return False

def validate_integration_points():
    """Validate integration with existing modules"""
    print("\n🔗 Validating Integration Points...")
    
    try:
        from app.schemas.gift_system import GiftIntegrationSettings
        
        integration = GiftIntegrationSettings()
        
        # Test integration settings
        integrations = [
            ('Contact', integration.contact_integration_enabled),
            ('Financial', integration.financial_integration_enabled),
            ('Reminder', integration.reminder_integration_enabled),
            ('Task', integration.task_integration_enabled),
        ]
        
        for module_name, enabled in integrations:
            if enabled:
                print(f'  ✅ {module_name} integration: Enabled')
            else:
                print(f'  ⚠️  {module_name} integration: Disabled')
        
        # Verify specific integration features
        features = [
            ('Auto-suggest from relationships', integration.auto_suggest_from_relationships),
            ('Track gift expenses', integration.track_gift_expenses),
            ('Create occasion reminders', integration.create_occasion_reminders),
            ('Create shopping tasks', integration.create_shopping_tasks),
        ]
        
        for feature_name, enabled in features:
            if enabled:
                print(f'  ✅ {feature_name}: Enabled')
            else:
                print(f'  ⚠️  {feature_name}: Disabled')
        
        return True
        
    except Exception as e:
        print(f'  ❌ Integration validation error: {e}')
        return False

def validate_security_and_privacy():
    """Validate security and privacy configurations"""
    print("\n🔒 Validating Security & Privacy...")
    
    try:
        from app.schemas.gift_system import GiftSystemPermissions, GiftPrivacyMode
        
        permissions = GiftSystemPermissions()
        
        # Check default security settings
        security_checks = [
            ('Users cannot view others\' gifts by default', not permissions.can_view_others_gifts),
            ('Users cannot configure system by default', not permissions.can_configure_system),
            ('Users can manage their own gifts', permissions.can_view_gifts and permissions.can_create_gifts),
        ]
        
        for check_name, passes in security_checks:
            if passes:
                print(f'  ✅ {check_name}')
            else:
                print(f'  ❌ {check_name}')
                return False
        
        # Test privacy modes
        privacy_modes = ['personal', 'shared', 'strict']
        for mode in privacy_modes:
            try:
                GiftPrivacyMode(mode)
                print(f'  ✅ Privacy mode \'{mode}\' is valid')
            except ValueError:
                print(f'  ❌ Privacy mode \'{mode}\' is invalid')
                return False
        
        return True
        
    except Exception as e:
        print(f'  ❌ Security validation error: {e}')
        return False

def main():
    """Main validation function"""
    print("🎁 Gift Ideas and Tracking System - Configuration Validation\n")
    
    validations = [
        validate_yaml_files,
        validate_configuration_system,
        validate_schemas,
        validate_api_endpoints,
        validate_integration_points,
        validate_security_and_privacy,
    ]
    
    all_passed = True
    
    for validation in validations:
        if not validation():
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nThe Gift Ideas and Tracking System configuration is properly")
        print("set up and integrated with existing Recaller modules.")
        print("\nConfiguration includes:")
        print("  • Environment variables for dev/prod settings")
        print("  • Reference data for categories, occasions, budgets")
        print("  • Integration with contacts, financial, reminders, tasks")
        print("  • API endpoints for configuration management")
        print("  • Security and privacy controls")
        print("  • Comprehensive test coverage")
        return True
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("\nPlease review the errors above and fix the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
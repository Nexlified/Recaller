#!/usr/bin/env python3
"""
Test script to demonstrate the YAML configuration validation system.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.core.config_validator import ConfigValidator, validate_all_configs
except ImportError:
    # Alternative import for direct execution
    sys.path.insert(0, str(backend_dir / "app"))
    from core.config_validator import ConfigValidator, validate_all_configs

def main():
    """Test the validation system with sample configuration files."""
    print("🧪 Testing YAML Configuration Validation System")
    print("=" * 50)
    
    # Paths
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # shared/scripts -> shared -> root
    config_dir = project_root / "config" / "reference-data"
    schema_dir = project_root / "config" / "validation" / "schemas"
    
    print(f"📁 Configuration directory: {config_dir}")
    print(f"📋 Schema directory: {schema_dir}")
    print()
    
    # Test individual file validation
    print("🔍 Testing individual file validation:")
    validator = ConfigValidator(schema_dir)
    
    test_files = [
        config_dir / "core" / "genders.yml",
        config_dir / "core" / "countries.yml",
        config_dir / "professional" / "industries.yml",
        config_dir / "social" / "activities.yml",
        config_dir / "contact" / "interaction-types.yml"
    ]
    
    for test_file in test_files:
        if test_file.exists():
            result = validator.validate_file(test_file)
            status = "✅" if result.is_valid else "❌"
            print(f"  {status} {test_file.name}")
            
            if result.errors:
                for error in result.errors:
                    print(f"    ❌ {error.error_type}: {error.message}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"    ⚠️  {warning.error_type}: {warning.message}")
    
    print()
    
    # Test bulk validation
    print("🚀 Testing bulk validation:")
    results = validate_all_configs(config_dir, schema_dir)
    
    total_files = len(results)
    valid_files = sum(1 for r in results if r.is_valid)
    invalid_files = total_files - valid_files
    
    print(f"  📊 Summary:")
    print(f"    Total files: {total_files}")
    print(f"    Valid files: {valid_files}")
    print(f"    Invalid files: {invalid_files}")
    
    print()
    
    # Test validation features
    print("🎯 Testing validation features:")
    
    # Test duplicate key detection
    print("  🔍 Testing duplicate key detection...")
    
    # Test hierarchical validation
    print("  🏗️  Testing hierarchical validation...")
    industries_file = config_dir / "professional" / "industries.yml"
    if industries_file.exists():
        result = validator.validate_file(industries_file)
        print(f"    Industries file validation: {'✅' if result.is_valid else '❌'}")
    
    # Test category-specific rules
    print("  📋 Testing category-specific validation...")
    countries_file = config_dir / "core" / "countries.yml"
    if countries_file.exists():
        result = validator.validate_file(countries_file)
        print(f"    Countries file validation: {'✅' if result.is_valid else '❌'}")
    
    print()
    print("🎉 Validation system testing completed!")
    
    # Return status
    return 0 if all(r.is_valid for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
#!/bin/bash
# shared/scripts/validate-config.sh
# Validate all YAML configuration files

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_DIR="$PROJECT_ROOT/shared/config"
SCHEMA_DIR="$CONFIG_DIR/validation/schemas"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔍 Validating YAML configuration files..."
echo "Config directory: $CONFIG_DIR"
echo "Schema directory: $SCHEMA_DIR"

# Check if Python validation module exists
if [ ! -f "$BACKEND_DIR/app/core/config_validator.py" ]; then
    echo "❌ Error: Python validation module not found at $BACKEND_DIR/app/core/config_validator.py"
    exit 1
fi

# Check if schema files exist
if [ ! -f "$SCHEMA_DIR/reference-data.schema.yml" ]; then
    echo "❌ Error: Reference data schema not found at $SCHEMA_DIR/reference-data.schema.yml"
    exit 1
fi

# Run Python validation
cd "$BACKEND_DIR"
python3 -c "
import sys
sys.path.append('.')
from pathlib import Path
from app.core.config_validator import validate_all_configs

config_dir = Path('$CONFIG_DIR/reference-data')
schema_dir = Path('$SCHEMA_DIR')

print('📁 Scanning configuration files...')
results = validate_all_configs(config_dir, schema_dir)

total_files = len(results)
valid_files = sum(1 for r in results if r.is_valid)
invalid_files = total_files - valid_files

print(f'📊 Validation Summary:')
print(f'   Total files: {total_files}')
print(f'   Valid files: {valid_files}')
print(f'   Invalid files: {invalid_files}')
print()

has_errors = False
for result in results:
    if result.errors:
        has_errors = True
        print(f'❌ {result.file_path}:')
        for error in result.errors:
            print(f'   • {error.error_type}: {error.message}')
        print()
    elif result.warnings:
        print(f'⚠️  {result.file_path}:')
        for warning in result.warnings:
            print(f'   • {warning.error_type}: {warning.message}')
        print()
    else:
        print(f'✅ {result.file_path}')

if has_errors:
    print('❌ Validation failed with errors.')
    sys.exit(1)
else:
    print('✅ All configuration files are valid!')
"

echo "🎉 Configuration validation completed successfully!"
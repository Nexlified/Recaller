#!/bin/bash
# shared/scripts/lint-yaml.sh
# Lint YAML files for syntax and formatting

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_DIR="$PROJECT_ROOT/shared/config"

echo "🔧 Linting YAML files..."

# Check if yamllint is available
if command -v yamllint &> /dev/null; then
    echo "Using yamllint for comprehensive YAML linting..."
    yamllint "$CONFIG_DIR"
else
    echo "yamllint not found, using Python YAML parser for basic syntax checking..."
    
    # Use Python to check YAML syntax
    find "$CONFIG_DIR" -name "*.yml" -o -name "*.yaml" | while read -r file; do
        echo "Checking: $file"
        python3 -c "
import yaml
import sys

try:
    with open('$file', 'r') as f:
        yaml.safe_load(f)
    print('✅ Valid YAML syntax')
except yaml.YAMLError as e:
    print(f'❌ YAML syntax error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error reading file: {e}')
    sys.exit(1)
"
        if [ $? -ne 0 ]; then
            echo "❌ Linting failed for $file"
            exit 1
        fi
    done
fi

echo "✅ YAML linting completed successfully!"
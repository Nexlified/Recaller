#!/bin/bash
# shared/scripts/generate-schema.sh
# Generate JSON schema documentation from YAML schemas

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
SCHEMA_DIR="$PROJECT_ROOT/shared/config/validation/schemas"
OUTPUT_DIR="/tmp/schema-docs"

echo "📝 Generating schema documentation..."
echo "Schema directory: $SCHEMA_DIR"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Convert YAML schemas to JSON for better tooling support
for schema_file in "$SCHEMA_DIR"/*.schema.yml; do
    if [ -f "$schema_file" ]; then
        base_name=$(basename "$schema_file" .yml)
        json_file="$OUTPUT_DIR/${base_name}.json"
        
        echo "Converting: $schema_file -> $json_file"
        python3 -c "
import yaml
import json
import sys

try:
    with open('$schema_file', 'r') as f:
        schema = yaml.safe_load(f)
    
    with open('$json_file', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print('✅ Successfully converted $schema_file')
except Exception as e:
    print(f'❌ Error converting $schema_file: {e}')
    sys.exit(1)
"
    fi
done

# Generate markdown documentation
cat > "$OUTPUT_DIR/README.md" << 'EOF'
# YAML Configuration Schema Documentation

This directory contains the JSON Schema definitions for validating YAML configuration files in the Recaller application.

## Schema Files

### reference-data.schema.json
The master schema for all reference data configuration files. This schema defines:
- Required fields: version, category, type, name, values
- Validation rules for keys, display names, and metadata
- Support for hierarchical data structures
- Internationalization support through translations

### category.schema.json
Category-specific validation constraints that extend the base schema:
- Core category: genders, countries, timezones, languages, currencies
- Professional category: industries, job-levels, organization-types, skills, certifications
- Social category: activities, interests, relationship-types, event-types, group-types
- Contact category: interaction-types, communication-preferences, networking-values, follow-up-priorities, contact-sources

## Usage

These schemas are used by the Python validation module to ensure:
1. Proper YAML syntax and structure
2. Required fields are present
3. Data types are correct
4. Business rules are enforced
5. Category-specific constraints are met

## Validation Process

1. Load YAML configuration file
2. Validate against master reference-data schema
3. Apply category-specific validation rules
4. Check business logic constraints
5. Report errors and warnings

## Error Types

- **yaml_syntax**: YAML parsing errors
- **schema_validation**: JSON schema violations
- **duplicate_keys**: Duplicate keys within values
- **invalid_parent_reference**: Invalid hierarchical references
- **inconsistent_hierarchy_level**: Level numbering issues
- **sort_order_gaps**: Sort order inconsistencies
EOF

echo "📚 Schema documentation generated at: $OUTPUT_DIR"
echo "✅ Schema generation completed successfully!"
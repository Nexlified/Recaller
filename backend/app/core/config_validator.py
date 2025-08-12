# backend/app/core/config_validator.py
import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidationError:
    file_path: str
    error_type: str
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    file_path: str

class ConfigValidator:
    def __init__(self, schema_dir: Path):
        self.schema_dir = schema_dir
        self.schemas = self._load_schemas()
        
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load all validation schemas"""
        schemas = {}
        for schema_file in self.schema_dir.glob("*.schema.yml"):
            with open(schema_file) as f:
                schema_name = schema_file.stem.replace('.schema', '')
                schemas[schema_name] = yaml.safe_load(f)
        return schemas
        
    def validate_file(self, config_file: Path) -> ValidationResult:
        """Validate a single configuration file"""
        errors = []
        warnings = []
        
        try:
            # Load and parse YAML
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
                
            # Schema validation
            schema_errors = self._validate_schema(config_data, config_file)
            errors.extend(schema_errors)
            
            # Business rule validation
            rule_errors, rule_warnings = self._validate_business_rules(config_data, config_file)
            errors.extend(rule_errors)
            warnings.extend(rule_warnings)
            
            # Category-specific validation
            category_errors = self._validate_category_rules(config_data, config_file)
            errors.extend(category_errors)
            
        except yaml.YAMLError as e:
            errors.append(ValidationError(
                file_path=str(config_file),
                error_type="yaml_syntax",
                message=f"YAML syntax error: {str(e)}",
                line_number=getattr(e, 'problem_mark', {}).get('line', None)
            ))
        except Exception as e:
            errors.append(ValidationError(
                file_path=str(config_file),
                error_type="general",
                message=f"Validation error: {str(e)}"
            ))
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            file_path=str(config_file)
        )
        
    def _validate_schema(self, data: Dict, file_path: Path) -> List[ValidationError]:
        """Validate against JSON schema"""
        errors = []
        
        try:
            # Use main reference data schema
            jsonschema.validate(data, self.schemas['reference-data'])
            
            # Use category-specific schema if available
            category = data.get('category')
            if category and 'category' in self.schemas:
                jsonschema.validate(data, self.schemas['category'])
                
        except jsonschema.ValidationError as e:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="schema_validation",
                message=f"Schema validation error: {e.message}",
                line_number=None  # JSON schema doesn't provide line numbers
            ))
        except jsonschema.SchemaError as e:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="schema_error",
                message=f"Schema definition error: {e.message}"
            ))
            
        return errors
        
    def _validate_business_rules(self, data: Dict, file_path: Path) -> tuple[List[ValidationError], List[ValidationError]]:
        """Validate business logic rules"""
        errors = []
        warnings = []
        
        # Check for duplicate keys
        values = data.get('values', [])
        keys = [v.get('key') for v in values if v.get('key')]
        duplicate_keys = set([k for k in keys if keys.count(k) > 1])
        
        if duplicate_keys:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="duplicate_keys",
                message=f"Duplicate keys found: {', '.join(duplicate_keys)}"
            ))
            
        # Check hierarchical consistency
        hierarchy_errors = self._validate_hierarchy(values, file_path)
        errors.extend(hierarchy_errors)
        
        # Check sort order consistency
        sort_warnings = self._validate_sort_order(values, file_path)
        warnings.extend(sort_warnings)
        
        return errors, warnings
        
    def _validate_hierarchy(self, values: List[Dict], file_path: Path) -> List[ValidationError]:
        """Validate hierarchical structure"""
        errors = []
        all_keys = {v.get('key') for v in values if v.get('key')}
        
        def check_children(items, parent_key=None, level=1):
            for item in items:
                # Check parent references
                if item.get('parent_key') and item.get('parent_key') not in all_keys:
                    errors.append(ValidationError(
                        file_path=str(file_path),
                        error_type="invalid_parent_reference",
                        message=f"Key '{item.get('key')}' references non-existent parent '{item.get('parent_key')}'"
                    ))
                
                # Check level consistency
                if item.get('level', 1) != level:
                    errors.append(ValidationError(
                        file_path=str(file_path),
                        error_type="inconsistent_hierarchy_level",
                        message=f"Key '{item.get('key')}' has level {item.get('level')} but should be {level}"
                    ))
                
                # Recursively check children
                children = item.get('children', [])
                if children:
                    check_children(children, item.get('key'), level + 1)
        
        check_children(values)
        return errors
        
    def _validate_sort_order(self, values: List[Dict], file_path: Path) -> List[ValidationError]:
        """Validate sort order consistency"""
        warnings = []
        
        # Check for gaps in sort order
        sort_orders = [v.get('sort_order', 0) for v in values]
        sort_orders.sort()
        
        expected = list(range(len(sort_orders)))
        if sort_orders != expected and sort_orders != list(range(1, len(sort_orders) + 1)):
            warnings.append(ValidationError(
                file_path=str(file_path),
                error_type="sort_order_gaps",
                message="Sort order has gaps or doesn't start from 0 or 1"
            ))
            
        return warnings
        
    def _validate_category_rules(self, data: Dict, file_path: Path) -> List[ValidationError]:
        """Validate category-specific business rules"""
        errors = []
        category = data.get('category')
        config_type = data.get('type')
        
        # Category-specific validations
        if category == 'core' and config_type == 'countries':
            errors.extend(self._validate_countries(data.get('values', []), file_path))
        elif category == 'professional' and config_type == 'industries':
            errors.extend(self._validate_industries(data.get('values', []), file_path))
            
        return errors
        
    def _validate_countries(self, values: List[Dict], file_path: Path) -> List[ValidationError]:
        """Validate country-specific rules"""
        errors = []
        iso_codes = []
        
        for value in values:
            metadata = value.get('metadata', {})
            iso_code = metadata.get('iso_code')
            
            if iso_code:
                if iso_code in iso_codes:
                    errors.append(ValidationError(
                        file_path=str(file_path),
                        error_type="duplicate_iso_code",
                        message=f"Duplicate ISO code: {iso_code}"
                    ))
                iso_codes.append(iso_code)
                
        return errors
        
    def _validate_industries(self, values: List[Dict], file_path: Path) -> List[ValidationError]:
        """Validate industry-specific rules"""
        errors = []
        # Add industry-specific validation logic here
        return errors

def validate_all_configs(config_dir: Path, schema_dir: Path) -> List[ValidationResult]:
    """Validate all configuration files in a directory"""
    validator = ConfigValidator(schema_dir)
    results = []
    
    for config_file in config_dir.rglob("*.yml"):
        if "validation" not in str(config_file) and "environment" not in str(config_file):
            result = validator.validate_file(config_file)
            results.append(result)
            
    return results
# Shared Configuration Files

This directory contains configuration files that are shared between the backend and frontend (React) applications.

## Directory Structure

```
shared/
├── config/
│   ├── reference-data/         # Static reference data files
│   │   ├── core/              # Core data types (countries, genders, etc.)
│   │   │   ├── countries.yml  # ISO country codes and details
│   │   │   ├── currencies.yml # ISO 4217 currency codes
│   │   │   ├── genders.yml    # Gender options
│   │   │   └── timezones.yml  # Timezone identifiers and offsets
│   │   ├── professional/      # Professional/business data
│   │   ├── social/           # Social/activity data
│   │   └── contact/          # Contact/interaction data
│   ├── validation/           # Validation schemas and rules
│   │   ├── schemas/         # JSON Schema definitions
│   │   └── rules/           # Business rule configurations
│   └── environment/         # Environment-specific configs
├── scripts/                 # Validation and utility scripts
└── validation/             # Python validation engine
```

## Usage

### For React/Frontend Applications

These configuration files can be loaded directly in your React application for static values that don't need to be stored in the database.

**Example - Loading countries:**
```javascript
// Using fetch API
const loadCountries = async () => {
  const response = await fetch('/shared/config/reference-data/core/countries.yml');
  const countriesYaml = await response.text();
  const countries = YAML.parse(countriesYaml);
  return countries.values;
};

// Using in component
const CountrySelect = () => {
  const [countries, setCountries] = useState([]);
  
  useEffect(() => {
    loadCountries().then(setCountries);
  }, []);
  
  return (
    <select>
      {countries.map(country => (
        <option key={country.key} value={country.key}>
          {country.display_name}
        </option>
      ))}
    </select>
  );
};
```

### For Backend Applications

```python
from shared.validation.config_validator import ConfigValidator
from pathlib import Path
import yaml

# Load configuration
def load_config(config_type):
    config_path = Path(f"shared/config/reference-data/core/{config_type}.yml")
    with open(config_path) as f:
        return yaml.safe_load(f)

# Get countries
countries = load_config('countries')
currencies = load_config('currencies')
```

## Available Configuration Types

### Core Data (shared/config/reference-data/core/)
- **countries.yml** - ISO country codes, names, continents
- **currencies.yml** - ISO 4217 currency codes, symbols, decimal places
- **genders.yml** - Gender identity options
- **timezones.yml** - IANA timezone identifiers with offsets

### Professional Data (shared/config/reference-data/professional/)
- **industries.yml** - Industry categories with NAICS codes

### Social Data (shared/config/reference-data/social/)
- **activities.yml** - Social activity categories

### Contact Data (shared/config/reference-data/contact/)
- **interaction-types.yml** - Types of interactions for relationship management

## Validation

Use the provided scripts to validate configuration files:

```bash
# Validate all configuration files
./shared/scripts/validate-config.sh

# Test validation system
python3 ./shared/scripts/test-validation.py

# Lint YAML syntax
./shared/scripts/lint-yaml.sh
```

## Schema Structure

Each configuration file follows this schema:

```yaml
---
version: "1.0.0"
category: "core|professional|social|contact"
type: "countries|currencies|genders|etc"
name: "Human readable name"
description: "Description of the data"

metadata:
  author: "Author name"
  last_updated: "YYYY-MM-DD"
  deprecated: false

values:
  - key: "unique_identifier"
    display_name: "Human readable name"
    description: "Description"
    sort_order: 0
    is_system: true
    is_active: true
    metadata:
      # Type-specific metadata
    tags: ["tag1", "tag2"]
```

## Notes

- These files contain static data that can be used directly by both backend and frontend
- Values like activities and categories may later be managed by admin interfaces (not in current scope)
- All files are validated against JSON schemas to ensure consistency
- Use the validation scripts before making changes to ensure data integrity
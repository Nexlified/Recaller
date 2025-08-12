# Configuration Management System

A centralized configuration management system that reads reference data from YAML files and synchronizes them with the database. This system manages common lookup values like Gender, Activities, Location, Industries, etc., providing a single source of truth shared between frontend and backend.

## 🏗️ Architecture

### Directory Structure
```
shared/
├── config/
│   └── reference-data/
│       ├── core/                # Core system data
│       │   ├── genders.yml
│       │   ├── countries.yml
│       │   └── ...
│       ├── professional/        # Professional/business data
│       │   ├── industries.yml
│       │   └── ...
│       ├── social/             # Social activities data
│       │   ├── activities.yml
│       │   └── ...
│       └── contact/            # Contact management data
│           ├── interaction-types.yml
│           └── ...
├── scripts/
│   ├── sync-config.sh          # Configuration sync script
│   └── demo.sh                 # Demo script
└── types/
    └── generated/              # Auto-generated TypeScript types
        ├── enums.ts
        ├── interfaces.ts
        └── config-client.ts
```

### Database Schema

The system uses 5 main tables:

- **`config_categories`** - Top-level groupings (core, professional, social, contact)
- **`config_types`** - Second-level groupings (genders, industries, activities)  
- **`config_values`** - Actual configuration data with hierarchical support
- **`config_value_translations`** - Multi-language support
- **`config_sync_history`** - Audit trail of sync operations

## 🚀 Quick Start

### 1. Validate Configuration Files
```bash
# Validate all YAML files
cd backend
python -m app.cli config validate ../shared/config/reference-data/core/genders.yml

# Or use the convenience script
./shared/scripts/sync-config.sh validate ../shared/config/reference-data/core/genders.yml
```

### 2. Sync to Database
```bash
# Dry run to see what would be synced
python -m app.cli config sync --dry-run

# Sync all configuration files
python -m app.cli config sync

# Sync a specific file
python -m app.cli config sync --file ../shared/config/reference-data/core/genders.yml
```

### 3. Generate TypeScript Types
```bash
cd backend
python app/cli/generate_types.py
```

### 4. Start API Server
```bash
cd backend
uvicorn app.main:app --reload
```

## 📄 YAML Configuration Format

### Basic Structure
```yaml
version: "1.0.0"
category: "core"
type: "genders"
name: "Gender Options"
description: "Standard gender identity options for user profiles"

values:
  - key: "male"
    display_name: "Male"
    description: "Male gender identity"
    sort_order: 1
    extra_metadata:
      icon: "mars"
      color: "#4A90E2"
    is_system: true
```

### Hierarchical Structure
```yaml
values:
  - key: "technology"
    display_name: "Technology"
    level: 1
    children:
      - key: "software_development"
        display_name: "Software Development"
        level: 2
      - key: "artificial_intelligence"
        display_name: "Artificial Intelligence"
        level: 2
```

## 🔧 CLI Commands

### Configuration Management
```bash
# Sync commands
python -m app.cli config sync                    # Sync all files
python -m app.cli config sync --file path.yml    # Sync specific file
python -m app.cli config sync --dry-run          # Preview changes

# Validation
python -m app.cli config validate path.yml       # Validate YAML file

# Database viewing
python -m app.cli config list-values             # List all values
python -m app.cli config list-values --category core    # Filter by category
python -m app.cli config list-values --format json      # JSON output
```

## 🌐 REST API Endpoints

### Categories
```http
GET /api/v1/config/categories           # List all categories
```

### Types  
```http
GET /api/v1/config/types                # List all configuration types
GET /api/v1/config/types?category_key=core  # Filter by category
```

### Values
```http
GET /api/v1/config/values               # List all values
GET /api/v1/config/values?category_key=core&type_key=genders  # Filtered
GET /api/v1/config/values/core/genders  # Specific configuration
GET /api/v1/config/values/core/genders/hierarchy  # Hierarchical view
```

### Sync Operations
```http
POST /api/v1/config/sync                # Sync all files
POST /api/v1/config/sync                # Sync specific file
{
  "file_path": "path/to/config.yml"
}
```

## 💻 Frontend Usage

### Generated TypeScript Types
```typescript
import { 
  ConfigValue, 
  ConfigCategory, 
  CoreGenders,
  SocialActivities 
} from '../shared/types/generated';

// Use enums for type safety
const gender = CoreGenders.Male;
const activity = SocialActivities.ProfessionalNetworking;
```

### Configuration Client
```typescript
import { configClient } from '../shared/types/generated/config-client';

// Get all genders
const genders = await configClient.getCoreGenders();

// Get hierarchical industries
const industries = await configClient.getHierarchicalValues('professional', 'industries');

// Generic API
const values = await configClient.getValues('social', 'activities');
```

### React Hook Example
```typescript
import { useState, useEffect } from 'react';
import { configClient, ConfigValue } from '../shared/types/generated';

export function useConfig(category: string, type: string) {
  const [values, setValues] = useState<ConfigValue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    configClient.getValuesByType(category, type)
      .then(setValues)
      .finally(() => setLoading(false));
  }, [category, type]);

  return { values, loading };
}
```

## 🔄 Multi-Tenant Support

The system supports tenant-specific configuration overrides:

```typescript
// Get tenant-specific values
const values = await configClient.getValues('core', 'genders', { tenant_id: 123 });

// Global values (tenant_id = null) are returned as fallbacks
```

## 🌍 Internationalization

Support for multiple languages via translation tables:

```sql
-- Example: French translation
INSERT INTO config_value_translations (config_value_id, language_code, display_name)
VALUES (1, 'fr', 'Masculin');
```

## 🧪 Development Workflow

### Adding New Configuration

1. **Create YAML file**
   ```yaml
   # shared/config/reference-data/new-category/new-type.yml
   version: "1.0.0"
   category: "new_category"
   type: "new_type"
   # ... rest of configuration
   ```

2. **Validate**
   ```bash
   python -m app.cli config validate path/to/new-file.yml
   ```

3. **Sync to database**
   ```bash
   python -m app.cli config sync --file path/to/new-file.yml
   ```

4. **Generate TypeScript types**
   ```bash
   python app/cli/generate_types.py
   ```

5. **Use in frontend**
   ```typescript
   import { NewCategoryNewType } from '../shared/types/generated/enums';
   ```

### Making Changes

1. **Update YAML file** with new values
2. **Re-sync** to database (automatically detects changes)
3. **Regenerate types** if structure changed
4. **Update frontend** to use new values

## 📊 Monitoring & Audit

### Sync History
All sync operations are tracked in `config_sync_history`:
- What files were processed
- How many records created/updated/deleted
- Any errors or warnings
- Performance metrics

### Health Checks
```http
GET /api/v1/config/health  # Service health check
```

## 🛠️ Troubleshooting

### Common Issues

**YAML Validation Errors**
```bash
# Check file syntax
python -m app.cli config validate problematic-file.yml
```

**Sync Failures**
```bash
# Use verbose mode for detailed error info
python -m app.cli config sync --verbose
```

**Database Connection Issues**
- Ensure PostgreSQL is running
- Check connection settings in `app/core/config.py`
- Verify database exists and migrations are applied

### Demo Script
Run the complete demo to verify everything works:
```bash
./shared/scripts/demo.sh
```

This will validate all files, show sync preview, and display generated types.

## 🏷️ Features Summary

✅ **YAML-based Configuration** - Human-readable, version-controlled  
✅ **Database Synchronization** - Automatic sync with change detection  
✅ **Hierarchical Data** - Support for nested categories  
✅ **Multi-tenant** - Tenant-specific overrides  
✅ **Type Safety** - Auto-generated TypeScript types  
✅ **CLI Tools** - Command-line management interface  
✅ **REST API** - Full CRUD operations  
✅ **Audit Trail** - Complete sync history  
✅ **Validation** - Schema validation and error checking  
✅ **i18n Ready** - Multi-language support  

The configuration management system provides a robust, scalable foundation for managing reference data across the entire Recaller application.
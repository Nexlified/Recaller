# Gift Ideas and Tracking System - Configuration Guide

## Overview

The Gift Ideas and Tracking System is a comprehensive module within Recaller that helps users manage gift giving, track occasions, set budgets, and receive timely reminders. This guide covers all configuration options and integration points.

## Environment Configuration

### Gift System Configuration Variables

The following environment variables control the gift system behavior:

#### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GIFT_SYSTEM_ENABLED` | boolean | `true` | Enable/disable the entire gift system |
| `GIFT_DEFAULT_CURRENCY` | string | `USD` | Default currency for gift budgets |
| `GIFT_MAX_BUDGET` | integer | `10000` (dev), `5000` (prod) | Maximum budget amount allowed |
| `GIFT_SUGGESTION_ENGINE` | string | `basic` | Gift suggestion engine: `basic`, `enhanced`, `ai_powered` |

#### Reminder Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GIFT_REMINDER_DAYS` | string | `7,3,1` | Comma-separated days in advance for reminders |
| `GIFT_AUTO_CREATE_TASKS` | boolean | `true` | Automatically create shopping tasks for gifts |

#### Privacy and Storage

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GIFT_PRIVACY_MODE` | string | `personal` (dev), `strict` (prod) | Privacy mode: `personal`, `shared`, `strict` |
| `GIFT_IMAGE_STORAGE` | boolean | `true` (dev), `false` (prod) | Allow image storage for gift ideas |
| `GIFT_EXTERNAL_LINKS` | boolean | `true` (dev), `false` (prod) | Allow external links for gift references |

### Environment-Specific Configurations

#### Development Environment (`config/environment/development.yml`)

```yaml
gift_system:
  enabled: "${GIFT_SYSTEM_ENABLED:true}"
  default_budget_currency: "${GIFT_DEFAULT_CURRENCY:USD}"
  max_budget_amount: "${GIFT_MAX_BUDGET:10000}"
  suggestion_engine: "${GIFT_SUGGESTION_ENGINE:basic}"
  reminder_advance_days: "${GIFT_REMINDER_DAYS:7,3,1}"
  auto_create_tasks: "${GIFT_AUTO_CREATE_TASKS:true}"
  privacy_mode: "${GIFT_PRIVACY_MODE:personal}"
  image_storage_enabled: "${GIFT_IMAGE_STORAGE:true}"
  external_links_enabled: "${GIFT_EXTERNAL_LINKS:true}"
```

#### Production Environment (`config/environment/production.yml`)

```yaml
gift_system:
  enabled: "${GIFT_SYSTEM_ENABLED:true}"
  default_budget_currency: "${GIFT_DEFAULT_CURRENCY:USD}"
  max_budget_amount: "${GIFT_MAX_BUDGET:5000}"
  suggestion_engine: "${GIFT_SUGGESTION_ENGINE:basic}"
  reminder_advance_days: "${GIFT_REMINDER_DAYS:7,3,1}"
  auto_create_tasks: "${GIFT_AUTO_CREATE_TASKS:true}"
  privacy_mode: "${GIFT_PRIVACY_MODE:strict}"
  image_storage_enabled: "${GIFT_IMAGE_STORAGE:false}"
  external_links_enabled: "${GIFT_EXTERNAL_LINKS:false}"
```

## Reference Data Configuration

The gift system uses structured reference data for categories, occasions, and budget ranges:

### Gift Categories (`shared/config/reference-data/social/gift-categories.yml`)

Defines common gift categories with:
- **Key**: Unique identifier
- **Display Name**: Human-readable name
- **Description**: Category description
- **Metadata**: Icon, color, price range
- **Tags**: Searchable tags
- **Hierarchical Support**: Parent-child relationships

Example categories:
- Electronics (smartphones, headphones)
- Clothing & Accessories (jewelry)
- Books & Media
- Home & Garden
- Experiences
- Food & Beverages
- Health & Beauty
- Hobbies & Sports

### Gift Occasions (`shared/config/reference-data/social/gift-occasions.yml`)

Defines common gift-giving occasions with:
- **Frequency**: annual, milestone, spontaneous
- **Reminder Settings**: Custom advance reminder days
- **Budget Importance**: low, medium, high
- **Fixed Dates**: For occasions like Christmas (12-25)

Example occasions:
- Birthday (annual, high importance)
- Anniversary (annual, high importance)
- Christmas (annual, fixed date, high importance)
- Valentine's Day (annual, fixed date, medium importance)
- Graduation (milestone, medium importance)
- Just Because (spontaneous, low importance)

### Budget Ranges (`shared/config/reference-data/financial/gift-budget-ranges.yml`)

Defines common budget ranges with:
- **Amount Ranges**: Min/max amounts
- **Currency**: Default USD
- **Suggested Categories**: Recommended gift categories for each range
- **Visual Coding**: Colors for UI representation

Example ranges:
- Under $25: Small thoughtful gifts
- $25-$50: Moderate gifts for colleagues
- $50-$100: Nice gifts for friends and family
- $100-$250: Meaningful gifts for close relationships
- $250-$500: Special occasion gifts
- $500-$1000: Luxury milestone gifts
- Over $1000: Premium extraordinary occasions

## Integration Configuration

### Contact Integration

The gift system integrates with the contact system to:
- **Auto-suggest recipients** based on relationships
- **Use contact preferences** for gift suggestions
- **Track gift history** per contact
- **Relationship-aware reminders** (birthdays, anniversaries)

Configuration:
```python
contact_integration_enabled: bool = True
auto_suggest_from_relationships: bool = True
use_contact_preferences: bool = True
```

### Financial Integration

The gift system integrates with the financial system to:
- **Track gift expenses** as transactions
- **Monitor budget limits** per occasion/contact
- **Generate spending reports** for gift categories
- **Budget alerts** when approaching limits

Configuration:
```python
financial_integration_enabled: bool = True
track_gift_expenses: bool = True
budget_alerts_enabled: bool = True
```

### Reminder Integration

The gift system integrates with the reminder system to:
- **Create occasion reminders** for birthdays, holidays
- **Shopping reminders** based on advance days
- **Follow-up reminders** for gift delivery
- **Thank you note reminders** after giving

Configuration:
```python
reminder_integration_enabled: bool = True
create_occasion_reminders: bool = True
create_shopping_reminders: bool = True
```

### Task Integration

The gift system integrates with the task system to:
- **Auto-create shopping tasks** for gift purchases
- **Set task priorities** based on occasion importance
- **Create subtasks** for gift wrapping, delivery
- **Link tasks to contacts** and occasions

Configuration:
```python
task_integration_enabled: bool = True
create_shopping_tasks: bool = True
create_wrapping_tasks: bool = False  # Optional
```

## Permissions and Roles

### Default Permissions

When the gift system is enabled, users have the following default permissions:

| Permission | Default | Description |
|------------|---------|-------------|
| `can_view_gifts` | `true` | View own gift information |
| `can_create_gifts` | `true` | Create new gift ideas and plans |
| `can_edit_gifts` | `true` | Edit existing gift information |
| `can_delete_gifts` | `true` | Delete own gifts |
| `can_manage_budgets` | `true` | Set and modify gift budgets |
| `can_view_others_gifts` | `false` | View other users' gifts (privacy-first) |
| `can_export_gift_data` | `true` | Export own gift data |
| `can_configure_system` | `false` | Modify system-wide gift settings |

### Privacy Modes

The gift system supports three privacy modes:

#### Personal Mode (`personal`)
- Users see only their own gifts
- Basic sharing within tenant for occasions
- Moderate privacy protection

#### Shared Mode (`shared`)
- Enhanced collaboration within tenant
- Shared occasion tracking
- Gift coordination features

#### Strict Mode (`strict`)
- Maximum privacy protection
- No cross-user visibility
- Encrypted sensitive data

## API Endpoints

### Configuration Endpoints

All gift system configuration is accessible via API:

```bash
# Get gift system configuration
GET /api/v1/config/gift-system/config

# Get integration settings
GET /api/v1/config/gift-system/integration-settings

# Get user permissions
GET /api/v1/config/gift-system/permissions

# Get system status
GET /api/v1/config/gift-system/status

# Get reference data
GET /api/v1/config/gift-system/reference-data/categories
GET /api/v1/config/gift-system/reference-data/occasions
GET /api/v1/config/gift-system/reference-data/budget-ranges
```

### Response Examples

#### System Configuration
```json
{
  "enabled": true,
  "default_budget_currency": "USD",
  "max_budget_amount": 10000,
  "suggestion_engine": "basic",
  "reminder_advance_days": [7, 3, 1],
  "auto_create_tasks": true,
  "privacy_mode": "personal",
  "image_storage_enabled": true,
  "external_links_enabled": true
}
```

#### System Status
```json
{
  "is_enabled": true,
  "configuration_valid": true,
  "integration_status": {
    "contacts": true,
    "financial": true,
    "reminders": true,
    "tasks": true,
    "storage": true,
    "external_links": true
  },
  "version": "1.0.0",
  "total_gift_categories": 8,
  "total_gift_occasions": 12,
  "total_budget_ranges": 6
}
```

## Setup and Migration

### Initial Setup

1. **Environment Configuration**: Set required environment variables
2. **Reference Data**: Load gift categories, occasions, and budget ranges
3. **Integration Check**: Verify other modules are available
4. **Permissions Setup**: Configure user permissions per tenant

### Database Migration

No specific database migrations are required for the configuration setup. The gift system configuration uses:
- YAML configuration files for reference data
- Environment variables for runtime settings  
- Existing configuration tables for tenant-specific overrides

### Validation

The configuration system includes validation for:
- **Budget Limits**: Maximum amounts and currency codes
- **Reminder Days**: Positive integers in logical order
- **Privacy Modes**: Valid enum values
- **Integration Dependencies**: Required modules are available

## Testing

### Configuration Tests

Test the gift system configuration with:

```bash
# Test configuration loading
python -c "from app.core.enhanced_settings import get_settings; print(get_settings().GIFT_SYSTEM_ENABLED)"

# Test API endpoints
curl -H "Authorization: Bearer <token>" \
     -H "X-Tenant-ID: <tenant>" \
     http://localhost:8000/api/v1/config/gift-system/status
```

### Validation Tests

```python
# Test budget validation
from app.schemas.gift_system import GiftSystemConfig

config = GiftSystemConfig(max_budget_amount=0)  # Should raise validation error
config = GiftSystemConfig(reminder_advance_days=[])  # Should use default [7,3,1]
```

## Troubleshooting

### Common Issues

1. **Gift System Disabled**: Check `GIFT_SYSTEM_ENABLED` environment variable
2. **Invalid Budget**: Verify `GIFT_MAX_BUDGET` is positive and reasonable
3. **Missing Reference Data**: Ensure YAML files are properly formatted
4. **Integration Failures**: Check dependent modules are enabled

### Debug Information

Enable debug logging to troubleshoot configuration issues:

```bash
export LOG_LEVEL=DEBUG
export GIFT_SYSTEM_ENABLED=true
```

### Configuration Validation

The system performs automatic validation:
- Environment variable types and ranges
- Reference data schema compliance  
- Integration dependency checking
- Permission consistency verification

## Future Enhancements

### Planned Configuration Features

1. **Tenant-Specific Overrides**: Allow tenants to customize reference data
2. **Advanced Privacy Controls**: Granular privacy settings per gift type
3. **External Service Integration**: Gift suggestion APIs, price comparison
4. **Multi-Currency Support**: Enhanced currency handling and conversion
5. **Advanced AI Configuration**: Machine learning model settings
6. **Custom Occasion Types**: User-defined gift occasions
7. **Bulk Configuration**: Import/export configuration sets

### Migration Path

When new features are added:
1. **Backward Compatibility**: Existing configurations remain valid
2. **Gradual Rollout**: New features have sensible defaults
3. **Migration Scripts**: Automated updates for configuration schema changes
4. **Documentation Updates**: This guide will be updated with new options

---

This configuration guide ensures the Gift Ideas and Tracking System can be properly set up, configured, and integrated with existing Recaller modules while maintaining security, privacy, and usability standards.
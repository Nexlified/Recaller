# Gender-Specific Relationship Mapping System

## Overview

The Recaller application now includes an intelligent gender-specific relationship mapping system that automatically determines the correct relationship types based on the genders of the contacts involved. This ensures accurate bidirectional relationships for gender-specific relations like brother/sister, uncle/aunt, nephew/niece.

## Key Features

### Automatic Gender Resolution
- Users can select "sibling" and the system automatically resolves to "brother" or "sister" based on contact genders
- Supports all gender-specific relationships defined in the configuration
- Maintains bidirectional consistency (if A is B's brother, then B is A's brother or sister)

### Privacy-First Design
- Gender field is optional on contacts
- Falls back to manual selection when gender information is unavailable
- Supports non-binary and "prefer not to say" options
- Users can override automatic gender resolution

### Comprehensive Relationship Support
- 23 relationship types across 4 categories (family, professional, social, romantic)
- Gender-specific mappings for sibling and uncle/aunt relationships
- Extensible configuration system via YAML

## Architecture

### Configuration (`config/relationship_mappings.yaml`)
Defines all relationship types and their gender-specific mappings:

```yaml
gender_specific_relationships:
  sibling:
    mappings:
      male_male: ["brother", "brother"]
      male_female: ["brother", "sister"]
      female_male: ["sister", "brother"]
      female_female: ["sister", "sister"]
    fallback: ["sibling", "sibling"]
```

### Database Schema

#### Contacts Table (Enhanced)
- Added `gender` field: `VARCHAR(20)` nullable
- Supports: 'male', 'female', 'non_binary', 'prefer_not_to_say'

#### Contact Relationships Table (New)
- Stores bidirectional relationships between contacts
- Includes metadata about gender resolution
- Maintains audit trail of automatic vs manual relationship creation

### Service Layer

#### RelationshipMappingService
Core service that handles:
- Gender-specific relationship resolution
- Validation of relationship-gender compatibility
- Fallback handling for missing/non-binary genders
- Configuration loading and validation

#### CRUD Operations
- `create_contact_relationship()`: Creates bidirectional relationships with automatic gender resolution
- `update_bidirectional_relationship()`: Updates both sides of a relationship
- `get_relationship_summary()`: Returns relationships grouped by category

### API Endpoints

Base URL: `/api/v1/relationships/`

- `GET /options` - Get available relationship types for UI selection
- `GET /categories` - Get relationship categories
- `POST /` - Create new bidirectional relationship
- `GET /contact/{contact_id}` - Get all relationships for a contact
- `GET /contact/{contact_id}/summary` - Get relationship summary by category
- `PUT /{contact_a_id}/{contact_b_id}` - Update bidirectional relationship
- `DELETE /{contact_a_id}/{contact_b_id}` - Delete relationship

## Usage Examples

### Creating a Sibling Relationship

```python
# API Request
POST /api/v1/relationships/
{
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_type": "sibling",
    "notes": "Twin brothers"
}

# Response (if both contacts are male)
{
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_a_to_b": "brother",
    "relationship_b_to_a": "brother",
    "relationship_category": "family",
    "is_gender_resolved": true,
    "original_relationship_type": "sibling"
}
```

### Gender Resolution Logic

```python
from app.services.relationship_mapping import relationship_mapping_service

# Automatic resolution
result = relationship_mapping_service.determine_gender_specific_relationship(
    'sibling', 'male', 'female'
)
# Returns: brother <-> sister

# Fallback for missing gender
result = relationship_mapping_service.determine_gender_specific_relationship(
    'sibling', None, 'female'  
)
# Returns: sibling <-> sibling (with warning)
```

## Edge Cases and Fallbacks

### Missing Gender Information
- When either contact's gender is None, empty, or missing
- Falls back to base relationship type (e.g., "sibling" instead of "brother/sister")
- Includes validation warnings in response

### Non-Binary/Other Genders
- When gender is 'non_binary' or 'prefer_not_to_say'
- Falls back to base relationship type
- Respects privacy preferences

### Manual Override
- Users can set `override_gender_resolution: true` to bypass automatic resolution
- Useful for non-traditional family structures or personal preferences
- Still validates relationship compatibility

### Complex Family Structures
- Supports step-relationships and adoptions through notes field
- Allows custom relationship types in future extensions
- Maintains flexibility for diverse family arrangements

## Testing

### Unit Tests
- Comprehensive test suite for all gender combinations
- Edge case testing for missing/invalid genders
- Validation testing for relationship compatibility

### Integration Tests
- API endpoint testing with real database operations
- Bidirectional relationship consistency testing
- Tenant isolation validation

### Configuration Testing
- YAML structure validation
- Mapping completeness verification
- Fallback behavior testing

## Migration Guide

### Database Migration
Run the included Alembic migration to add the gender field and relationships table:

```bash
cd backend
alembic upgrade head
```

### API Integration
The new relationship endpoints are automatically included in the API router. No additional configuration required.

### Frontend Integration (Future)
When implementing the frontend:

1. Add gender field to contact forms (optional)
2. Use `/api/v1/relationships/options?include_base_types=true` for relationship selection
3. Show resolved relationship types in preview before saving
4. Provide override option for manual relationship specification

## Security Considerations

### Tenant Isolation
- All relationship operations are scoped to the current tenant
- Cross-tenant relationship creation is prevented
- Proper access controls on all endpoints

### Privacy Protection
- Gender information is optional and can be omitted
- Supports privacy-conscious options like "prefer not to say"
- No sensitive data in relationship metadata

### Data Integrity
- Bidirectional relationship consistency is enforced
- Unique constraints prevent duplicate relationships
- Proper foreign key relationships maintain data integrity

## Future Enhancements

### Planned Features
1. **Extended Gender Mappings**: Support for more relationship types (cousin, grandparent, etc.)
2. **Custom Relationship Types**: User-defined relationship types for specific needs
3. **Relationship Context**: Additional metadata like "step", "adopted", "in-law"
4. **Batch Operations**: Bulk relationship creation for families
5. **Relationship Validation**: Advanced validation rules for impossible relationships

### Frontend Components
1. **Relationship Selector**: Smart dropdown with gender-aware suggestions
2. **Family Tree Visualization**: Graphical representation of relationships
3. **Relationship Manager**: Dedicated interface for managing contact relationships
4. **Gender Privacy Controls**: Fine-grained privacy settings for gender information

## Configuration Reference

See `config/relationship_mappings.yaml` for the complete configuration structure including:
- All supported relationship types
- Gender-specific mapping rules
- Relationship categories
- Fallback behaviors

The configuration is designed to be easily extensible for additional relationship types and gender mappings as needed.
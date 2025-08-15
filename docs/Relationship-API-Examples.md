# Contact Relationship API Examples

## Overview
These examples demonstrate how to use the new contact relationship endpoints with gender-specific relationship mapping.

## Base URL
All endpoints are under `/api/v1/relationships/`

## Authentication
All requests require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Examples

### 1. Get Available Relationship Options

Get relationship types for UI selection (with base types like 'sibling'):

```bash
curl -X GET "http://localhost:8000/api/v1/relationships/options?include_base_types=true" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default"
```

Response:
```json
[
  {
    "key": "sibling",
    "display_name": "Sibling",
    "category": "family",
    "is_gender_specific": true,
    "description": "Brother/Sister relationship"
  },
  {
    "key": "friend",
    "display_name": "Friend",
    "category": "social",
    "is_gender_specific": false,
    "description": null
  }
]
```

### 2. Create a Sibling Relationship

Create a relationship that will be automatically resolved based on genders:

```bash
curl -X POST "http://localhost:8000/api/v1/relationships/" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_type": "sibling",
    "notes": "Twin brothers"
  }'
```

Response (if both contacts are male):
```json
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

### 3. Create Relationship with Manual Override

Bypass automatic gender resolution:

```bash
curl -X POST "http://localhost:8000/api/v1/relationships/" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_type": "brother",
    "override_gender_resolution": true,
    "notes": "Manually specified"
  }'
```

### 4. Get Contact Relationships

Get all relationships for a specific contact:

```bash
curl -X GET "http://localhost:8000/api/v1/relationships/contact/1" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default"
```

Response:
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "created_by_user_id": 1,
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_type": "brother",
    "relationship_category": "family",
    "notes": "Twin brothers",
    "is_active": true,
    "is_gender_resolved": true,
    "original_relationship_type": "sibling",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": null
  }
]
```

### 5. Get Relationship Summary

Get relationships grouped by category:

```bash
curl -X GET "http://localhost:8000/api/v1/relationships/contact/1/summary" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default"
```

Response:
```json
{
  "family": [
    {
      "relationship_id": 1,
      "relationship_type": "brother",
      "other_contact_id": 2,
      "other_contact_name": "John Smith",
      "is_gender_resolved": true,
      "original_relationship_type": "sibling",
      "notes": "Twin brothers",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "social": [
    {
      "relationship_id": 2,
      "relationship_type": "friend",
      "other_contact_id": 3,
      "other_contact_name": "Jane Doe",
      "is_gender_resolved": false,
      "original_relationship_type": null,
      "notes": "College friend",
      "created_at": "2024-01-01T12:05:00Z"
    }
  ]
}
```

### 6. Update Relationship

Update an existing bidirectional relationship:

```bash
curl -X PUT "http://localhost:8000/api/v1/relationships/1/2" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "new_relationship_type=friend&notes=Changed from sibling to friend"
```

### 7. Delete Relationship

Delete a bidirectional relationship:

```bash
curl -X DELETE "http://localhost:8000/api/v1/relationships/1/2" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default"
```

Response:
```json
{
  "message": "Relationship deleted successfully"
}
```

## Gender Resolution Examples

### Supported Gender Mappings

#### Sibling Relationships
- Male + Male → Brother ↔ Brother
- Male + Female → Brother ↔ Sister  
- Female + Male → Sister ↔ Brother
- Female + Female → Sister ↔ Sister

#### Uncle/Aunt - Nephew/Niece Relationships
- Male + Male → Uncle ↔ Nephew
- Male + Female → Uncle ↔ Niece
- Female + Male → Aunt ↔ Nephew
- Female + Female → Aunt ↔ Niece

### Fallback Scenarios

When gender resolution is not possible (missing gender, non-binary, etc.):

```bash
# Contact A has gender: null, Contact B has gender: "female"
curl -X POST "http://localhost:8000/api/v1/relationships/" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_a_id": 1,
    "contact_b_id": 2,
    "relationship_type": "sibling"
  }'
```

Response:
```json
{
  "contact_a_id": 1,
  "contact_b_id": 2,
  "relationship_a_to_b": "sibling",
  "relationship_b_to_a": "sibling",
  "relationship_category": "family",
  "is_gender_resolved": false,
  "original_relationship_type": "sibling"
}
```

## Error Responses

### Invalid Contact IDs
```json
{
  "detail": "One or both contacts not found"
}
```

### Self-Relationship
```json
{
  "detail": "Cannot create relationship with self"
}
```

### Duplicate Relationship
```json
{
  "detail": "Relationship already exists between these contacts"
}
```

### Relationship Not Found
```json
{
  "detail": "Relationship not found"
}
```

## Contact Gender Field

When creating or updating contacts, you can now include the gender field:

```bash
curl -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@example.com",
    "gender": "male"
  }'
```

### Supported Gender Values
- `"male"` - Male gender
- `"female"` - Female gender  
- `"non_binary"` - Non-binary gender
- `"prefer_not_to_say"` - Privacy option
- `null` or omitted - No gender specified

## Best Practices

1. **Use Base Types for UI**: Present users with simplified options like "Sibling" instead of "Brother/Sister"
2. **Show Resolution Preview**: Display the resolved relationship types before saving
3. **Provide Override Option**: Allow users to manually specify relationships when needed
4. **Respect Privacy**: Make gender field optional and support privacy-conscious options
5. **Handle Fallbacks Gracefully**: Inform users when automatic resolution isn't possible
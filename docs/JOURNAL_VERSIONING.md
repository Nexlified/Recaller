# Journal Entry Versioning System

This document describes the journal entry versioning system that allows users to view and manage version history of their journal entries.

## Overview

The versioning system automatically creates new versions when journal entries are updated, preserving the complete history of changes. Users can view all versions, revert to previous versions, and selectively delete old versions.

## Features

- **Automatic Versioning**: Updates create new versions by default, preserving history
- **Version Navigation**: Users can view all versions and navigate between them
- **Revert Capability**: Can revert to any previous version (creates new version)
- **Selective Deletion**: Can delete individual versions (with safety constraints)
- **Tag Preservation**: Tags are copied to new versions automatically
- **Security**: Full tenant and user isolation maintained
- **Backward Compatibility**: Optional versioning mode for non-breaking updates

## Database Schema

The journal entries table already includes versioning fields:

```sql
-- Existing fields in journal_entries table
entry_version INTEGER NOT NULL DEFAULT 1,
parent_entry_id INTEGER REFERENCES journal_entries(id),
```

- `entry_version`: Version number (1 for original, 2+ for subsequent versions)
- `parent_entry_id`: Reference to the root entry (NULL for original entry)

## API Endpoints

### Get Version History

```http
GET /api/v1/journal/{entry_id}/versions
```

Returns complete version history for a journal entry.

**Response:**
```json
{
  "current_version": {
    "id": 123,
    "entry_version": 3,
    "title": "Latest Title",
    "content": "Latest content...",
    "entry_date": "2024-01-15",
    "mood": "happy",
    "location": "Home",
    "weather": "Sunny",
    "is_private": true,
    "is_archived": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null,
    "parent_entry_id": 121
  },
  "versions": [
    {
      "id": 123,
      "entry_version": 3,
      "title": "Latest Title",
      "created_at": "2024-01-15T10:30:00Z",
      "changes_summary": "Version 3"
    },
    {
      "id": 122,
      "entry_version": 2,
      "title": "Updated Title",
      "created_at": "2024-01-15T10:15:00Z",
      "changes_summary": "Version 2"
    },
    {
      "id": 121,
      "entry_version": 1,
      "title": "Original Title",
      "created_at": "2024-01-15T10:00:00Z",
      "changes_summary": "Version 1"
    }
  ],
  "total_versions": 3
}
```

### Get Specific Version

```http
GET /api/v1/journal/{entry_id}/versions/{version}
```

Returns a specific version of a journal entry.

**Response:**
```json
{
  "id": 121,
  "entry_version": 1,
  "title": "Original Title",
  "content": "Original content...",
  "entry_date": "2024-01-15",
  "mood": "excited",
  "location": "Office",
  "weather": "Cloudy",
  "is_private": true,
  "is_archived": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": null,
  "parent_entry_id": null
}
```

### Revert to Version

```http
POST /api/v1/journal/{entry_id}/versions/{version}/revert
```

Reverts a journal entry to a specific version by creating a new version with the target version's content.

**Response:**
```json
{
  "success": true,
  "message": "Successfully reverted to version 1",
  "version": {
    "id": 124,
    "entry_version": 4,
    "title": "Original Title",
    "content": "Original content...",
    "entry_date": "2024-01-15",
    "mood": "excited",
    "location": "Office",
    "weather": "Cloudy",
    "is_private": true,
    "is_archived": false,
    "created_at": "2024-01-15T10:45:00Z",
    "updated_at": null,
    "parent_entry_id": 121
  }
}
```

### Delete Version

```http
DELETE /api/v1/journal/{entry_id}/versions/{version}
```

Deletes a specific version of a journal entry.

**Restrictions:**
- Cannot delete version 1 (original) if other versions exist
- Cannot delete the only remaining version

**Response:**
```json
{
  "success": true,
  "message": "Successfully deleted version 2",
  "version": null
}
```

## CRUD Operations

### Creating Versions

When updating a journal entry, a new version is created by default:

```python
# This creates a new version (default behavior)
updated_entry = journal_crud.update_journal_entry(
    db=db,
    entry_id=entry_id,
    user_id=user_id,
    tenant_id=tenant_id,
    journal_entry=update_data
)
```

To update in place without creating a version:

```python
# This updates the existing entry (backward compatibility)
updated_entry = journal_crud.update_journal_entry(
    db=db,
    entry_id=entry_id,
    user_id=user_id,
    tenant_id=tenant_id,
    journal_entry=update_data,
    create_version=False
)
```

### Version Management Functions

```python
# Get all versions
versions = journal_crud.get_journal_entry_versions(
    db=db,
    entry_id=entry_id,
    user_id=user_id,
    tenant_id=tenant_id
)

# Get specific version
version = journal_crud.get_journal_entry_version(
    db=db,
    entry_id=entry_id,
    version=2,
    user_id=user_id,
    tenant_id=tenant_id
)

# Revert to version
reverted = journal_crud.revert_journal_entry_to_version(
    db=db,
    entry_id=entry_id,
    version=1,
    user_id=user_id,
    tenant_id=tenant_id
)

# Delete version
success = journal_crud.delete_journal_entry_version(
    db=db,
    entry_id=entry_id,
    version=2,
    user_id=user_id,
    tenant_id=tenant_id
)
```

## Security and Isolation

The versioning system maintains the same security model as the base journal system:

- **Tenant Isolation**: Users can only access versions within their tenant
- **User Isolation**: Users can only access versions of their own entries
- **Permission Checks**: All version operations require proper authentication

## Data Models

### JournalEntryVersion

Complete version data including all fields:

```python
class JournalEntryVersion(BaseModel):
    id: int
    entry_version: int
    title: Optional[str]
    content: str
    entry_date: date
    mood: Optional[JournalEntryMoodEnum]
    location: Optional[str]
    weather: Optional[str]
    is_private: bool
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime]
    parent_entry_id: Optional[int]
```

### JournalEntryVersionSummary

Compact version info for lists:

```python
class JournalEntryVersionSummary(BaseModel):
    id: int
    entry_version: int
    title: Optional[str]
    created_at: datetime
    changes_summary: Optional[str] = None
```

### JournalEntryVersionHistory

Version history response:

```python
class JournalEntryVersionHistory(BaseModel):
    current_version: JournalEntryVersion
    versions: List[JournalEntryVersionSummary]
    total_versions: int
```

## Usage Examples

### Frontend Integration

```typescript
// Get version history
const response = await api.get(`/journal/${entryId}/versions`);
const history = response.data;

// Display versions
history.versions.forEach(version => {
  console.log(`Version ${version.entry_version}: ${version.title}`);
});

// Revert to version
await api.post(`/journal/${entryId}/versions/${versionNumber}/revert`);

// Delete version
await api.delete(`/journal/${entryId}/versions/${versionNumber}`);
```

### Backend Usage

```python
# Create entry and update it
entry = journal_crud.create_journal_entry(...)
updated = journal_crud.update_journal_entry(...)  # Creates version 2

# View history
versions = journal_crud.get_journal_entry_versions(...)
print(f"Entry has {len(versions)} versions")

# Revert to original
original = journal_crud.revert_journal_entry_to_version(
    ..., version=1
)  # Creates version 3 with version 1's content
```

## Migration

No database migration is required as the versioning fields already exist in the journal_entries table.

## Performance Considerations

- Version queries include proper indexes on `parent_entry_id` and `entry_version`
- Large version histories may impact performance - consider archiving old versions
- Tags are duplicated across versions - monitor storage usage

## Best Practices

1. **Regular Cleanup**: Consider implementing automatic cleanup of old versions
2. **Version Limits**: Optionally limit the number of versions per entry
3. **Meaningful Changes**: Only create versions for significant content changes
4. **User Education**: Inform users about the versioning system and how to use it
5. **Backup Strategy**: Include version data in backup procedures

## Testing

Comprehensive tests are provided in `tests/test_journal_versioning.py` covering:

- Version creation and management
- CRUD operations
- API endpoints
- Security and isolation
- Edge cases and error handling

Run tests with:
```bash
pytest tests/test_journal_versioning.py -v
```
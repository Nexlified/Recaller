# Journal API Endpoints

This document provides detailed information about journal-related endpoints in the Recaller API. The journal feature allows users to create, manage, and organize personal journal entries with rich metadata including tags, moods, locations, and attachments.

## Base URL

All journal endpoints are available at:
```
{base_url}/api/v1/journal/
```

## Authentication

**All journal endpoints require authentication.** Include the JWT token in the Authorization header:

```http
Authorization: Bearer your_jwt_token_here
```

**Multi-tenancy:** Journal entries are isolated by tenant. Include the tenant ID header for multi-tenant deployments:

```http
X-Tenant-ID: your_tenant_id
```

## Endpoints Overview

| Endpoint | Method | Description | Response Model |
|----------|--------|-------------|----------------|
| `/` | GET | List journal entries with filtering and pagination | `JournalEntryListResponse` |
| `/` | POST | Create a new journal entry | `JournalEntry` |
| `/{entry_id}` | GET | Get a specific journal entry | `JournalEntry` |
| `/{entry_id}` | PUT | Update a journal entry | `JournalEntry` |
| `/{entry_id}` | DELETE | Delete a journal entry (permanent) | Success message |
| `/{entry_id}/archive` | POST | Archive/unarchive a journal entry | `JournalEntry` |
| `/{entry_id}/tags` | POST | Add a tag to a journal entry | `JournalTag` |
| `/{entry_id}/tags/{tag_name}` | DELETE | Remove a tag from a journal entry | Success message |
| `/stats/` | GET | Get journal statistics | Statistics object |
| `/bulk-update` | POST | Bulk update multiple entries | `JournalEntryBulkResponse` |
| `/bulk-tag` | POST | Bulk add/remove tags from entries | `JournalEntryBulkResponse` |
| `/tags/popular` | GET | Get popular tags for the user | List of tag objects |

---

## GET /

List user's journal entries with pagination and advanced filtering options.

### Request

**URL:** `GET /api/v1/journal/`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (starts from 1) |
| `per_page` | integer | No | 20 | Number of entries per page (1-100) |
| `include_archived` | boolean | No | false | Include archived entries in results |
| `mood` | string | No | - | Filter by specific mood (see mood enum values) |
| `start_date` | date | No | - | Show entries from this date onwards (YYYY-MM-DD) |
| `end_date` | date | No | - | Show entries up to this date (YYYY-MM-DD) |
| `search` | string | No | - | Search in title and content (min 1 character) |

**Mood Values:**
- `VERY_HAPPY`, `HAPPY`, `CONTENT`, `NEUTRAL`, `ANXIOUS`, `SAD`, `VERY_SAD`, `ANGRY`, `EXCITED`, `GRATEFUL`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/journal/?page=1&per_page=10&mood=HAPPY&start_date=2023-01-01" \
  -H "Authorization: Bearer your_jwt_token"
```

**JavaScript Example:**

```javascript
const response = await fetch('/api/v1/journal/?page=1&per_page=10&mood=HAPPY', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenantId
  }
});

const data = await response.json();
console.log(`Found ${data.pagination.total} entries`);
```

### Response

**Success Response (200):**

```json
{
  "items": [
    {
      "id": 123,
      "title": "A Great Day",
      "entry_date": "2023-01-15",
      "mood": "HAPPY",
      "is_private": true,
      "is_archived": false,
      "created_at": "2023-01-15T14:30:00Z",
      "tag_count": 3,
      "attachment_count": 1
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 10,
    "total_pages": 15,
    "has_next": true,
    "has_previous": false
  }
}
```

### Error Responses

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["query", "per_page"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## POST /

Create a new journal entry with optional tags and metadata.

### Request

**URL:** `POST /api/v1/journal/`

**Content-Type:** `application/json`

**Body Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `content` | string | Yes | Main journal content | Min 1 character, max 50,000 |
| `title` | string | No | Entry title | Max 255 characters |
| `entry_date` | date | Yes | Date this entry represents | Format: YYYY-MM-DD |
| `mood` | string | No | Mood/sentiment | One of the mood enum values |
| `location` | string | No | Location context | Max 255 characters |
| `weather` | string | No | Weather context | Max 100 characters |
| `is_private` | boolean | No | Privacy setting | Default: true |
| `tags` | array | No | List of tags to add | Array of tag objects |

**Tag Object:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `tag_name` | string | Yes | Tag name | 1-50 characters, alphanumeric and spaces |
| `tag_color` | string | No | Hex color code | Format: #RRGGBB |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/journal/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "title": "My Amazing Day",
    "content": "Today was absolutely wonderful! I accomplished so much and felt really positive about everything.",
    "entry_date": "2023-01-15",
    "mood": "HAPPY",
    "location": "Home Office",
    "weather": "Sunny",
    "is_private": true,
    "tags": [
      {
        "tag_name": "productivity",
        "tag_color": "#4CAF50"
      },
      {
        "tag_name": "work"
      }
    ]
  }'
```

**JavaScript Example:**

```javascript
const newEntry = {
  title: "My Amazing Day",
  content: "Today was absolutely wonderful! I accomplished so much and felt really positive about everything.",
  entry_date: "2023-01-15",
  mood: "HAPPY",
  location: "Home Office",
  weather: "Sunny",
  is_private: true,
  tags: [
    { tag_name: "productivity", tag_color: "#4CAF50" },
    { tag_name: "work" }
  ]
};

const response = await fetch('/api/v1/journal/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenantId
  },
  body: JSON.stringify(newEntry)
});

const entry = await response.json();
```

### Response

**Success Response (201):**

```json
{
  "id": 123,
  "tenant_id": 1,
  "user_id": 456,
  "title": "My Amazing Day",
  "content": "Today was absolutely wonderful! I accomplished so much and felt really positive about everything.",
  "entry_date": "2023-01-15",
  "mood": "HAPPY",
  "location": "Home Office",
  "weather": "Sunny",
  "is_private": true,
  "is_archived": false,
  "entry_version": 1,
  "parent_entry_id": null,
  "is_encrypted": false,
  "created_at": "2023-01-15T14:30:00Z",
  "updated_at": null,
  "tags": [
    {
      "id": 1,
      "journal_entry_id": 123,
      "tag_name": "productivity",
      "tag_color": "#4CAF50",
      "created_at": "2023-01-15T14:30:00Z"
    },
    {
      "id": 2,
      "journal_entry_id": 123,
      "tag_name": "work",
      "tag_color": null,
      "created_at": "2023-01-15T14:30:00Z"
    }
  ],
  "attachments": []
}
```

### Error Responses

**Validation Error (422):**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["content"],
      "msg": "Value error, Content contains potentially malicious script patterns",
      "input": "<script>alert('xss')</script>Content"
    }
  ]
}
```

**Authentication Error (401):**

```json
{
  "detail": "Not authenticated"
}
```

---

## GET /{entry_id}

Get a specific journal entry by ID, including all related tags and attachments.

### Request

**URL:** `GET /api/v1/journal/{entry_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/journal/123" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
{
  "id": 123,
  "tenant_id": 1,
  "user_id": 456,
  "title": "My Amazing Day",
  "content": "Today was absolutely wonderful! I accomplished so much and felt really positive about everything.",
  "entry_date": "2023-01-15",
  "mood": "HAPPY",
  "location": "Home Office",
  "weather": "Sunny",
  "is_private": true,
  "is_archived": false,
  "entry_version": 1,
  "parent_entry_id": null,
  "is_encrypted": false,
  "created_at": "2023-01-15T14:30:00Z",
  "updated_at": "2023-01-15T16:45:00Z",
  "tags": [
    {
      "id": 1,
      "journal_entry_id": 123,
      "tag_name": "productivity",
      "tag_color": "#4CAF50",
      "created_at": "2023-01-15T14:30:00Z"
    }
  ],
  "attachments": []
}
```

### Error Responses

**Not Found (404):**

```json
{
  "detail": "Journal entry not found"
}
```

---

## PUT /{entry_id}

Update an existing journal entry. All fields are optional in updates.

### Request

**URL:** `PUT /api/v1/journal/{entry_id}`

**Content-Type:** `application/json`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |

**Body Parameters (all optional):**

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `title` | string | Entry title | Max 255 characters |
| `content` | string | Main journal content | Min 1 character, max 50,000 |
| `entry_date` | date | Date this entry represents | Format: YYYY-MM-DD |
| `mood` | string | Mood/sentiment | One of the mood enum values |
| `location` | string | Location context | Max 255 characters |
| `weather` | string | Weather context | Max 100 characters |
| `is_private` | boolean | Privacy setting | - |
| `is_archived` | boolean | Archive status | - |

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/api/v1/journal/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "title": "Updated: My Amazing Day",
    "mood": "EXCITED",
    "location": "Coffee Shop"
  }'
```

### Response

**Success Response (200):**

```json
{
  "id": 123,
  "tenant_id": 1,
  "user_id": 456,
  "title": "Updated: My Amazing Day",
  "content": "Today was absolutely wonderful! I accomplished so much and felt really positive about everything.",
  "entry_date": "2023-01-15",
  "mood": "EXCITED",
  "location": "Coffee Shop",
  "weather": "Sunny",
  "is_private": true,
  "is_archived": false,
  "entry_version": 2,
  "parent_entry_id": null,
  "is_encrypted": false,
  "created_at": "2023-01-15T14:30:00Z",
  "updated_at": "2023-01-15T18:00:00Z",
  "tags": [],
  "attachments": []
}
```

---

## DELETE /{entry_id}

Permanently delete a journal entry. This action cannot be undone.

### Request

**URL:** `DELETE /api/v1/journal/{entry_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/journal/123" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
{
  "detail": "Journal entry deleted successfully"
}
```

### Error Responses

**Not Found (404):**

```json
{
  "detail": "Journal entry not found"
}
```

---

## POST /{entry_id}/archive

Archive or unarchive a journal entry (soft delete/restore).

### Request

**URL:** `POST /api/v1/journal/{entry_id}/archive`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `archive` | boolean | No | true | true to archive, false to unarchive |

**Example Request:**

```bash
# Archive an entry
curl -X POST "http://localhost:8000/api/v1/journal/123/archive?archive=true" \
  -H "Authorization: Bearer your_jwt_token"

# Unarchive an entry
curl -X POST "http://localhost:8000/api/v1/journal/123/archive?archive=false" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
{
  "id": 123,
  "tenant_id": 1,
  "user_id": 456,
  "title": "My Amazing Day",
  "content": "Today was absolutely wonderful!",
  "entry_date": "2023-01-15",
  "mood": "HAPPY",
  "location": "Home Office",
  "weather": "Sunny",
  "is_private": true,
  "is_archived": true,
  "entry_version": 1,
  "parent_entry_id": null,
  "is_encrypted": false,
  "created_at": "2023-01-15T14:30:00Z",
  "updated_at": "2023-01-15T18:30:00Z",
  "tags": [],
  "attachments": []
}
```

---

## POST /{entry_id}/tags

Add a tag to a specific journal entry.

### Request

**URL:** `POST /api/v1/journal/{entry_id}/tags`

**Content-Type:** `application/json`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |

**Body Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `tag_name` | string | Yes | Tag name | 1-50 characters, alphanumeric and spaces |
| `tag_color` | string | No | Hex color code | Format: #RRGGBB |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/journal/123/tags" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "tag_name": "important",
    "tag_color": "#FF5722"
  }'
```

### Response

**Success Response (201):**

```json
{
  "id": 5,
  "journal_entry_id": 123,
  "tag_name": "important",
  "tag_color": "#FF5722",
  "created_at": "2023-01-15T19:00:00Z"
}
```

### Error Responses

**Entry Not Found (404):**

```json
{
  "detail": "Journal entry not found"
}
```

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "tag_color"],
      "msg": "string does not match expected pattern",
      "type": "value_error.str.regex"
    }
  ]
}
```

---

## DELETE /{entry_id}/tags/{tag_name}

Remove a specific tag from a journal entry.

### Request

**URL:** `DELETE /api/v1/journal/{entry_id}/tags/{tag_name}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Unique identifier of the journal entry |
| `tag_name` | string | Yes | Name of the tag to remove |

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/journal/123/tags/important" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
{
  "detail": "Tag removed successfully"
}
```

### Error Responses

**Not Found (404):**

```json
{
  "detail": "Journal entry or tag not found"
}
```

---

## GET /stats/

Get comprehensive journal statistics for the authenticated user.

### Request

**URL:** `GET /api/v1/journal/stats/`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/journal/stats/" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
{
  "total_entries": 45,
  "mood_distribution": {
    "HAPPY": 12,
    "CONTENT": 8,
    "NEUTRAL": 15,
    "ANXIOUS": 5,
    "SAD": 3,
    "EXCITED": 2
  },
  "most_used_tags": [
    {
      "tag_name": "work",
      "count": 20,
      "color": "#2196F3"
    },
    {
      "tag_name": "personal",
      "count": 15,
      "color": "#4CAF50"
    },
    {
      "tag_name": "reflection",
      "count": 10,
      "color": null
    }
  ]
}
```

---

## POST /bulk-update

Update multiple journal entries at once with the same changes.

### Request

**URL:** `POST /api/v1/journal/bulk-update`

**Content-Type:** `application/json`

**Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_ids` | array | Yes | List of entry IDs to update (min 1) |
| `is_archived` | boolean | No | Archive/unarchive all entries |
| `is_private` | boolean | No | Change privacy setting for all entries |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/journal/bulk-update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "entry_ids": [123, 124, 125],
    "is_archived": true,
    "is_private": false
  }'
```

### Response

**Success Response (200):**

```json
{
  "success_count": 3,
  "failed_count": 0,
  "errors": []
}
```

**Partial Success Response (200):**

```json
{
  "success_count": 2,
  "failed_count": 1,
  "errors": [
    "Entry 125 not found or not accessible"
  ]
}
```

---

## POST /bulk-tag

Add or remove tags from multiple journal entries at once.

### Request

**URL:** `POST /api/v1/journal/bulk-tag`

**Content-Type:** `application/json`

**Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_ids` | array | Yes | List of entry IDs to modify (min 1) |
| `tags_to_add` | array | No | List of tags to add to all entries |
| `tags_to_remove` | array | No | List of tag names to remove from all entries |

**Tag Object in tags_to_add:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tag_name` | string | Yes | Tag name |
| `tag_color` | string | No | Hex color code |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/journal/bulk-tag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "entry_ids": [123, 124, 125],
    "tags_to_add": [
      {
        "tag_name": "reviewed",
        "tag_color": "#9C27B0"
      }
    ],
    "tags_to_remove": ["draft", "temporary"]
  }'
```

### Response

**Success Response (200):**

```json
{
  "success_count": 8,
  "failed_count": 0,
  "errors": []
}
```

---

## GET /tags/popular

Get the most popular tags for the authenticated user, sorted by usage frequency.

### Request

**URL:** `GET /api/v1/journal/tags/popular`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Number of tags to return (1-100) |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/journal/tags/popular?limit=10" \
  -H "Authorization: Bearer your_jwt_token"
```

### Response

**Success Response (200):**

```json
[
  {
    "tag_name": "work",
    "count": 45,
    "color": "#2196F3"
  },
  {
    "tag_name": "personal",
    "count": 32,
    "color": "#4CAF50"
  },
  {
    "tag_name": "reflection",
    "count": 28,
    "color": null
  },
  {
    "tag_name": "goals",
    "count": 15,
    "color": "#FF9800"
  }
]
```

---

## Data Models

### JournalEntry

Complete journal entry object with all relationships:

```json
{
  "id": 123,
  "tenant_id": 1,
  "user_id": 456,
  "title": "Entry Title",
  "content": "Entry content...",
  "entry_date": "2023-01-15",
  "mood": "HAPPY",
  "location": "Location",
  "weather": "Weather",
  "is_private": true,
  "is_archived": false,
  "entry_version": 1,
  "parent_entry_id": null,
  "is_encrypted": false,
  "created_at": "2023-01-15T14:30:00Z",
  "updated_at": "2023-01-15T16:45:00Z",
  "tags": [
    {
      "id": 1,
      "journal_entry_id": 123,
      "tag_name": "tag_name",
      "tag_color": "#FF5722",
      "created_at": "2023-01-15T14:30:00Z"
    }
  ],
  "attachments": []
}
```

### JournalEntrySummary

Lightweight entry object for list responses:

```json
{
  "id": 123,
  "title": "Entry Title",
  "entry_date": "2023-01-15",
  "mood": "HAPPY",
  "is_private": true,
  "is_archived": false,
  "created_at": "2023-01-15T14:30:00Z",
  "tag_count": 3,
  "attachment_count": 1
}
```

### Pagination

Pagination metadata included in list responses:

```json
{
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```

---

## Error Handling

### Standard HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Common Error Formats

**Authentication Error:**
```json
{
  "detail": "Not authenticated"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found Error:**
```json
{
  "detail": "Journal entry not found"
}
```

---

## Security & Validation

### Content Security

- **XSS Prevention**: HTML content is automatically escaped
- **Script Injection**: Script tags and malicious patterns are blocked
- **Length Limits**: Content is limited to prevent DoS attacks
- **Unicode Support**: Proper handling of international characters

### Data Validation

- **Entry Dates**: Must be within reasonable timeframes (1900-2100)
- **Content Length**: 1-50,000 characters
- **Tag Names**: 1-50 characters, alphanumeric and spaces
- **Colors**: Must be valid hex color codes (#RRGGBB)

### Privacy & Tenancy

- **User Isolation**: Users can only access their own entries
- **Tenant Isolation**: Entries are isolated by tenant
- **Privacy Flags**: Entries can be marked private or public
- **Archive Support**: Soft deletion via archiving

---

## Best Practices

### Creating Entries

1. **Always validate dates** - Ensure entry_date is realistic
2. **Use meaningful titles** - Help with searching and organization
3. **Add relevant tags** - Improve categorization and filtering
4. **Set appropriate privacy** - Consider who should see the entry

### Querying Entries

1. **Use pagination** - Don't request too many entries at once
2. **Filter effectively** - Use date ranges and mood filters to narrow results
3. **Search wisely** - Use specific search terms for better performance
4. **Include archived sparingly** - Only when specifically needed

### Error Handling

1. **Check authentication** - Handle 401 errors by redirecting to login
2. **Validate input** - Check field constraints before sending requests
3. **Handle not found** - Gracefully handle 404 errors for deleted entries
4. **Show validation errors** - Display field-specific error messages to users

---

**Related Documentation:**
- [Authentication Guide](../guides/authentication.md) - JWT token authentication
- [Error Handling Guide](../guides/error-handling.md) - Comprehensive error management
- [Journal Validation](../../journal-validation.md) - Security and validation details
- [Main API Documentation](../../../API-Documentation.md) - Complete API overview
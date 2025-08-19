# Relationship Management System Guide

This guide explains how to use the new Relationship Management system that replaces the old Contacts API.

## Overview

The Relationship Management system provides a normalized, privacy-focused approach to managing person profiles and relationships. Instead of a monolithic "Contact" model, information is distributed across specialized tables for better organization and privacy control.

## Key Features

### 1. Minimal Profile Creation
You can create a person profile with just a name:

```typescript
// Frontend
const profile = await relationshipManagementService.createPersonProfile({
  first_name: "Alice"
});

// Backend
profile = create_person_profile(
  db, 
  obj_in=PersonProfileCreate(first_name="Alice"),
  tenant_id=user.tenant_id,
  created_by_user_id=user.id
)
```

### 2. Normalized Information Storage

Information is organized into logical categories:

- **PersonProfile**: Core information (name, basic details)
- **PersonContactInfo**: Email, phone, addresses
- **PersonProfessionalInfo**: Job, organization, work history
- **PersonPersonalInfo**: Birthday, family info, preferences
- **PersonLifeEvents**: Important dates, milestones
- **PersonBelongings**: Items they own or are associated with
- **PersonRelationships**: Connections to other profiles

### 3. Privacy Controls

Each piece of information can have its own privacy setting:

- `private`: Only visible to the creator
- `tenant_shared`: Visible to all users in the same tenant

```typescript
// Make contact info tenant-shared but keep personal info private
await relationshipManagementService.createPersonContactInfo(profileId, {
  email: "alice@example.com",
  visibility: "tenant_shared"
});

await relationshipManagementService.createPersonPersonalInfo(profileId, {
  date_of_birth: "1990-05-15",
  visibility: "private"  // Default
});
```

## API Endpoints

### Person Profiles
- `GET /relationship-management/profiles/` - List profiles
- `POST /relationship-management/profiles/` - Create profile
- `GET /relationship-management/profiles/{id}` - Get profile
- `PUT /relationship-management/profiles/{id}` - Update profile
- `DELETE /relationship-management/profiles/{id}` - Delete profile

### Information Categories
Each category has similar endpoints under `/relationship-management/profiles/{id}/`:
- `/contact-info/` - Contact information
- `/professional-info/` - Professional information
- `/personal-info/` - Personal information  
- `/life-events/` - Life events
- `/belongings/` - Belongings
- `/relationships/` - Relationships

### Relationships
- `GET /relationship-management/profiles/{id}/relationships/` - Get relationships
- `POST /relationship-management/relationships/` - Create relationship

## Usage Examples

### Creating a Complete Profile

```typescript
// 1. Create the basic profile
const profile = await relationshipManagementService.createPersonProfile({
  first_name: "Alice",
  last_name: "Johnson",
  display_name: "Alice J."
});

// 2. Add contact information
await relationshipManagementService.createPersonContactInfo(profile.id, {
  email: "alice@example.com",
  phone: "+1-555-0123",
  is_primary: true
});

// 3. Add professional information
await relationshipManagementService.createPersonProfessionalInfo(profile.id, {
  job_title: "Software Engineer",
  organization_name: "Tech Corp",
  is_current: true
});

// 4. Add personal information
await relationshipManagementService.createPersonPersonalInfo(profile.id, {
  date_of_birth: "1990-05-15",
  favorite_color: "blue",
  interests_hobbies: "photography, hiking"
});

// 5. Add a life event
await relationshipManagementService.createPersonLifeEvent(profile.id, {
  event_type: "graduation",
  title: "Computer Science Degree",
  event_date: "2012-06-15",
  significance: 8
});
```

### Creating Relationships

```typescript
// Create a family relationship
await relationshipManagementService.createFamilyRelationship(
  aliceId,
  bobId,
  "brother",
  "My older brother"
);

// Create a professional relationship
await relationshipManagementService.createProfessionalRelationship(
  aliceId,
  charlieId,
  "colleague",
  "Same engineering team"
);

// Create a social relationship
await relationshipManagementService.createSocialRelationship(
  aliceId,
  danaId,
  "friend",
  "Met at photography club"
);
```

### Privacy Management

```typescript
// Share a profile with the tenant
await relationshipManagementService.shareProfileWithTenant(profileId);

// Make a profile private again
await relationshipManagementService.makeProfilePrivate(profileId);
```

## Migration from Contacts

The old Contacts API (`/contacts/`) continues to work for backward compatibility, but new development should use the Relationship Management API (`/relationship-management/`).

### Key Differences

| Old Contacts | New Relationship Management |
|--------------|----------------------------|
| Single `contacts` table | 6 normalized tables |
| All-or-nothing privacy | Granular privacy per field type |
| Limited relationship types | Rich relationship management |
| No belongings/life events | Comprehensive person tracking |
| Contact-centric | Person-centric with relationships |

### Migration Strategy

1. **New Features**: Use Relationship Management API
2. **Existing Code**: Gradually migrate from Contacts API
3. **Data Migration**: Run the migration script to move existing contacts to person profiles

## Database Schema

### Core Tables

```sql
-- Core profile
person_profiles (id, tenant_id, created_by_user_id, first_name, last_name, ...)

-- Information categories
person_contact_info (id, person_id, email, phone, ...)
person_professional_info (id, person_id, job_title, organization_id, ...)
person_personal_info (id, person_id, date_of_birth, favorite_color, ...)
person_life_events (id, person_id, event_type, title, event_date, ...)
person_belongings (id, person_id, name, category, brand, ...)

-- Relationships
person_relationships (id, person_a_id, person_b_id, relationship_type, ...)
```

## Best Practices

1. **Start Small**: Create profiles with just a name, add details later
2. **Respect Privacy**: Use appropriate visibility settings
3. **Rich Relationships**: Take advantage of relationship categories and strength ratings
4. **Life Events**: Track important milestones for better relationship management
5. **Belongings**: Note items that help you understand or relate to the person

## Frontend Integration

The `relationshipManagementService` provides all necessary methods:

```typescript
import relationshipManagementService from '@/services/relationshipManagement';

// Get all profiles
const profiles = await relationshipManagementService.getPersonProfiles();

// Search profiles
const results = await relationshipManagementService.searchProfiles("alice");

// Get full profile with all information
const fullProfile = await relationshipManagementService.getFullPersonProfile(profileId);
```

## Error Handling

The API provides detailed error messages for validation and authorization issues:

```typescript
try {
  await relationshipManagementService.createPersonProfile(profileData);
} catch (error) {
  if (error.response?.status === 400) {
    // Validation error - check error.response.data.detail
  } else if (error.response?.status === 403) {
    // Permission error
  }
}
```

## Future Enhancements

The normalized structure makes it easy to add new features:

- Additional information categories
- More relationship types
- Enhanced privacy controls
- Integration with external services
- Advanced search and filtering
- Relationship analytics

For more details, see the API documentation and TypeScript type definitions.
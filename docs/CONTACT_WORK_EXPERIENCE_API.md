# Contact Work Experience API Documentation

This document describes the new Contact Work Experience API endpoints that have been implemented to enhance the Recaller contact system with comprehensive professional information tracking.

## Overview

The Contact Work Experience feature allows users to:
- Track multiple work experiences per contact (current and historical)
- Store rich professional information (company, role, duration, skills, etc.)
- Build professional networks based on shared companies
- Manage reference capabilities
- Analyze career progression and skills evolution

## Database Schema

### `contact_work_experience` Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `contact_id` | Integer | Foreign key to contacts table |
| `tenant_id` | Integer | Foreign key to tenants table |
| `company_name` | String(255) | Company name (required) |
| `company_id` | Integer | Optional link to organizations table |
| `job_title` | String(255) | Job title (required) |
| `department` | String(255) | Department/division |
| `employment_type` | String(50) | full-time, part-time, contract, etc. |
| `work_location` | String(255) | remote, hybrid, on-site, city |
| `start_date` | Date | Employment start date (required) |
| `end_date` | Date | Employment end date (NULL for current) |
| `is_current` | Boolean | Whether this is current position |
| `work_phone` | String(50) | Work phone number |
| `work_email` | String(255) | Work email address |
| `work_address` | Text | Work address |
| `job_description` | Text | Job description |
| `key_achievements` | Text[] | Array of achievements |
| `skills_used` | Text[] | Array of skills used |
| `salary_range` | String(100) | Salary range (optional) |
| `currency` | String(3) | Currency code (default: USD) |
| `linkedin_profile` | String(500) | LinkedIn profile URL |
| `other_profiles` | JSONB | Other professional profiles |
| `manager_contact_id` | Integer | Foreign key to contacts (manager) |
| `reporting_structure` | Text | Description of reporting structure |
| `can_be_reference` | Boolean | Can be used as reference |
| `reference_notes` | Text | Reference notes |
| `visibility` | String(20) | private, team, public |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## API Endpoints

### Contact Work Experience CRUD

#### Get Work Experiences for Contact
```http
GET /api/v1/work-experience/contacts/{contact_id}/work-experience
```
Returns all work experiences for a specific contact, ordered by start date (most recent first).

#### Get Current Work Experience
```http
GET /api/v1/work-experience/contacts/{contact_id}/work-experience/current
```
Returns the current work experience for a contact (where `is_current = true`).

#### Get Work Experience by ID
```http
GET /api/v1/work-experience/work-experience/{work_experience_id}
```
Returns a specific work experience by ID.

#### Create Work Experience
```http
POST /api/v1/work-experience/contacts/{contact_id}/work-experience
```
Creates a new work experience for a contact. If `is_current` is true, automatically sets other positions to non-current.

#### Update Work Experience
```http
PUT /api/v1/work-experience/work-experience/{work_experience_id}
```
Updates an existing work experience.

#### Delete Work Experience
```http
DELETE /api/v1/work-experience/work-experience/{work_experience_id}
```
Deletes a work experience.

### Professional Network & Discovery

#### Get Contacts by Company
```http
GET /api/v1/work-experience/work-experience/by-company?company_name={name}&current_only={bool}
```
Returns all contacts who worked/work at a specific company.

#### Get Professional Network
```http
GET /api/v1/work-experience/contacts/{contact_id}/professional-network?depth={1-3}
```
Returns professional network connections for a contact based on shared companies.

#### Get Career Timeline
```http
GET /api/v1/work-experience/contacts/{contact_id}/career-timeline
```
Returns career timeline for a contact (chronological work history).

### Search & Filter

#### Search Work Experiences
```http
GET /api/v1/work-experience/work-experience/search?q={query}
```
Searches work experiences by company name, job title, or description.

#### Get Contacts by Skills
```http
GET /api/v1/work-experience/work-experience/by-skills?skills={skill1,skill2}
```
Returns work experiences that include any of the specified skills.

#### Get Potential References
```http
GET /api/v1/work-experience/work-experience/references
```
Returns contacts who can be used as references (`can_be_reference = true`).

### Utility Endpoints

#### Get Companies
```http
GET /api/v1/work-experience/work-experience/companies
```
Returns list of unique company names in the tenant.

#### Get Skills
```http
GET /api/v1/work-experience/work-experience/skills
```
Returns list of unique skills across all work experiences in the tenant.

## Data Models

### ContactWorkExperience
```typescript
interface ContactWorkExperience {
  id: number;
  contact_id: number;
  tenant_id: number;
  company_name: string;
  company_id?: number;
  job_title: string;
  department?: string;
  employment_type?: EmploymentType;
  work_location?: string;
  start_date: string; // ISO date
  end_date?: string; // ISO date
  is_current: boolean;
  work_phone?: string;
  work_email?: string;
  work_address?: string;
  job_description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  salary_range?: string;
  currency: string;
  linkedin_profile?: string;
  other_profiles?: Record<string, any>;
  manager_contact_id?: number;
  reporting_structure?: string;
  can_be_reference: boolean;
  reference_notes?: string;
  visibility: WorkExperienceVisibility;
  created_at: string;
  updated_at?: string;
}
```

### Enums
```typescript
enum EmploymentType {
  FULL_TIME = "full-time",
  PART_TIME = "part-time",
  CONTRACT = "contract",
  INTERNSHIP = "internship",
  FREELANCE = "freelance",
  VOLUNTEER = "volunteer"
}

enum WorkLocation {
  REMOTE = "remote",
  HYBRID = "hybrid",
  ON_SITE = "on-site",
  TRAVEL = "travel"
}

enum WorkExperienceVisibility {
  PRIVATE = "private",
  TEAM = "team",
  PUBLIC = "public"
}
```

## Business Logic & Constraints

1. **Current Position Management**: Only one work experience per contact can be marked as current (`is_current = true`). When creating/updating a work experience with `is_current = true`, all other positions for that contact are automatically set to `is_current = false`.

2. **Date Validation**: End date must be greater than or equal to start date. Current positions (`is_current = true`) cannot have an end date.

3. **Tenant Isolation**: All operations are scoped to the user's tenant. Users can only access work experiences for contacts within their tenant.

4. **Access Control**: Users can only view work experiences for contacts they have access to (contacts they created or public contacts). Only contact owners can create, update, or delete work experiences.

5. **Professional Networks**: The system automatically builds professional networks by finding contacts who worked at the same companies, enabling discovery of professional connections.

## Security Features

- **Tenant Isolation**: All queries are filtered by tenant_id
- **User Access Control**: Users can only access contacts they own or public contacts
- **Input Validation**: All input is validated and sanitized
- **RBAC**: Only contact owners can modify work experience data

## Usage Examples

### Create a Work Experience
```javascript
const workExperience = await contactWorkExperienceService.createWorkExperience(123, {
  company_name: "TechCorp Inc",
  job_title: "Senior Software Engineer",
  department: "Engineering",
  employment_type: EmploymentType.FULL_TIME,
  work_location: "San Francisco, CA",
  start_date: "2023-01-15",
  is_current: true,
  skills_used: ["React", "TypeScript", "Node.js"],
  can_be_reference: true
});
```

### Find Professional Network
```javascript
const network = await contactWorkExperienceService.getProfessionalNetwork(123, 2);
console.log(`Found ${network.length} professional connections`);
```

### Search by Skills
```javascript
const experts = await contactWorkExperienceService.getContactsBySkills(["React", "TypeScript"]);
console.log(`Found ${experts.length} contacts with React/TypeScript experience`);
```

## Frontend Integration

The frontend service (`contactWorkExperienceService`) provides a complete TypeScript interface with helper methods for:
- CRUD operations
- Professional network discovery
- Company and skills management
- Data validation and formatting

## Migration

The database migration `016_create_contact_work_experience.py` creates the new table with proper indexes and constraints. Run with:

```bash
cd backend
alembic upgrade head
```

## Related Enhancements

This implementation enhances the existing Contact model with:
- New `work_experiences` relationship
- Helper properties: `current_work_experience` and `work_history`
- Backward compatibility with existing `job_title` and `organization_id` fields
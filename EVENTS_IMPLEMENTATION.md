# Events Management System - Implementation Guide

## Overview

This document provides a comprehensive guide to the Events Management System implementation for the Recaller application. The system allows users to track occasions, meetings, and events where contacts are met or interact, providing context for relationship building.

## Architecture

### Database Schema

The implementation includes five main tables:

#### 1. `events` - Core Event Information
- **Primary Key**: `id` (BIGSERIAL)
- **Tenant Isolation**: `tenant_id` (FK to tenants)
- **Basic Info**: name, description, event_type, event_category
- **Date/Time**: start_date, end_date, start_time, end_time, timezone
- **Location**: location, venue, address fields, virtual_event_url
- **Organization**: organizer_name, organizer_contact_id, host_organization_id
- **Capacity**: expected_attendees, actual_attendees, max_capacity
- **Properties**: is_recurring, is_private, requires_invitation
- **Metadata**: cost, currency, dress_code, special_instructions
- **Status**: status (planned, confirmed, ongoing, completed, cancelled, postponed)

#### 2. `contact_event_attendances` - Attendance Tracking
- **Association**: contact_id, event_id (composite unique key)
- **Attendance**: attendance_status, role_at_event, invitation_method
- **Interaction**: how_we_met_at_event, conversation_highlights
- **RSVP**: rsvp_date, rsvp_response, dietary_restrictions, plus_one_count
- **Relationship Impact**: relationship_strength_before/after, connection_quality
- **Memories**: personal_notes, memorable_moments, photos_with_contact

#### 3. `event_tags` - Event Categorization
- **Basic**: event_id, tag_name, tag_color
- **Unique constraint** on (event_id, tag_name)

#### 4. `event_follow_ups` - Action Management
- **Association**: event_id, contact_id, created_by_user_id
- **Details**: follow_up_type, description, due_date, priority, status
- **Completion**: completed_date, completion_notes

#### 5. `contacts` & `organizations` - Foundation Tables
- Basic contact and organization management to support events

### API Endpoints

#### Core Event Operations
```
GET    /api/v1/events                         # List events with filtering
POST   /api/v1/events                         # Create new event
GET    /api/v1/events/{id}                    # Get event details
PUT    /api/v1/events/{id}                    # Update event
DELETE /api/v1/events/{id}                    # Delete event
```

#### Event Discovery
```
GET    /api/v1/events/search                  # Search events
GET    /api/v1/events/types/{type}            # Get events by type
GET    /api/v1/events/upcoming                # Get upcoming events
GET    /api/v1/events/past                    # Get past events
GET    /api/v1/events/by-date/{date}          # Get events by date
GET    /api/v1/events/calendar/{year}/{month} # Calendar view
```

#### Attendance Management
```
GET    /api/v1/events/{id}/attendees          # Get attendees
POST   /api/v1/events/{id}/attendees          # Add attendee
PUT    /api/v1/events/{id}/attendees/{contact_id} # Update attendance
DELETE /api/v1/events/{id}/attendees/{contact_id} # Remove attendee
```

#### Relationship Tracking
```
GET    /api/v1/events/{id}/new-connections    # New relationships
GET    /api/v1/events/{id}/relationship-changes # Relationship changes
GET    /api/v1/events/{id}/analytics          # Event analytics
```

#### Follow-up Management
```
GET    /api/v1/events/{id}/follow-ups         # Get follow-ups
POST   /api/v1/events/{id}/follow-ups         # Create follow-up
```

#### Contact Integration
```
GET    /api/v1/contacts/{id}/events           # Contact's events
GET    /api/v1/contacts/{id}/shared-events/{other_id} # Shared events
```

## Usage Examples

### Creating an Event
```json
POST /api/v1/events
{
    "name": "Tech Meetup: AI in Healthcare",
    "description": "Monthly meetup discussing AI applications in healthcare",
    "event_type": "meetup",
    "event_category": "professional",
    "start_date": "2025-08-25",
    "start_time": "18:00:00",
    "end_time": "21:00:00",
    "location": "Innovation Hub",
    "venue": "Conference Room A",
    "address_city": "San Francisco",
    "address_state": "CA",
    "organizer_name": "Healthcare AI Group",
    "expected_attendees": 50,
    "cost": 25.00,
    "event_website": "https://healthcareai.meetup.com"
}
```

### Adding an Attendee with Context
```json
POST /api/v1/events/1/attendees
{
    "contact_id": 123,
    "attendance_status": "confirmed",
    "role_at_event": "speaker",
    "invitation_method": "direct",
    "how_we_met_at_event": "Approached after their presentation on medical imaging AI",
    "rsvp_response": "yes",
    "relationship_strength_before": 3,
    "follow_up_needed": true,
    "follow_up_notes": "Interested in collaboration on medical device project"
}
```

### Getting Event Analytics
```json
GET /api/v1/events/1/analytics

Response:
{
    "new_connections": 3,
    "strengthened_relationships": 5,
    "follow_ups_created": 8,
    "total_attendees": 42,
    "attendance_rate": 0.84
}
```

## Features

### Multi-Tenant Support
- All operations are tenant-aware
- Data isolation between tenants
- User authentication and authorization

### Relationship Tracking
- Track relationship strength before/after events
- Identify connection quality changes
- Monitor networking effectiveness

### Event Analytics
- New connections made at events
- Relationship strength improvements
- Follow-up action tracking
- Attendance rates and metrics

### Search and Filtering
- Text search across event fields
- Filter by type, status, date ranges
- Calendar view for date-based browsing
- Upcoming/past event views

### Follow-up Management
- Create action items from events
- Track completion status
- Link follow-ups to specific contacts
- Priority and due date management

## Database Migrations

The implementation includes 8 Alembic migrations:

1. `001_create_tenants` - Base tenant table
2. `002_create_users` - User management
3. `003_create_contacts` - Contact foundation
4. `004_create_organizations` - Organization foundation
5. `005_create_events` - Core events table
6. `006_create_attendances` - Attendance tracking
7. `007_create_event_tags` - Event categorization
8. `008_create_event_follow_ups` - Follow-up management

### Running Migrations
```bash
cd backend
alembic upgrade head
```

## Testing

The implementation includes comprehensive validation:

- Model imports and relationships
- Schema validation for all entities
- API endpoint registration
- FastAPI application building
- Tenant-aware operations

Run the validation script:
```bash
cd backend
PYTHONPATH=/path/to/backend python /tmp/test_events_system.py
```

## Security

### Authentication
- JWT token-based authentication
- Current user dependency injection
- Active user validation

### Authorization
- Tenant-aware data access
- User ownership validation
- Resource-level permissions

### Data Validation
- Pydantic schema validation
- SQL injection prevention
- Input sanitization

## Performance Considerations

### Database Indexes
- Primary keys on all tables
- Foreign key indexes
- Composite indexes for queries
- Date-based indexes for calendar views

### Query Optimization
- Selective loading of related data
- Pagination for large result sets
- Efficient join operations
- Filtered queries with proper indexes

## Deployment

### Prerequisites
- PostgreSQL database
- Python 3.8+
- FastAPI dependencies

### Steps
1. Set up database connection in environment
2. Run Alembic migrations
3. Start FastAPI application
4. Verify endpoints with API documentation

### Environment Variables
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=recaller
SECRET_KEY=your-secret-key
```

## Future Enhancements

### Planned Integrations
- Social Groups (#8.2) for group event planning
- Enhanced Contact Intelligence (#8.4) for advanced insights
- Organizations (#8.1) for corporate event management

### Potential Features
- Recurring event management
- Event templates
- Integration with calendar systems
- Email notifications
- Event photo management
- Advanced analytics and reporting

## Support

For issues or questions about the Events Management System:

1. Check the API documentation at `/docs` when running the server
2. Review the database schema in the migration files
3. Examine the test script for usage examples
4. Refer to the CRUD operations for data manipulation patterns

The system is designed to be extensible and maintainable, following FastAPI and SQLAlchemy best practices throughout.
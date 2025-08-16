# Personal Date Reminder System

The Personal Date Reminder System allows users to create flexible reminders for important personal dates like birthdays, anniversaries, and custom events with smart notification preferences and automatic task creation.

## Features

### Reminder Types
- **Birthday**: For tracking birthdays with age calculation
- **Anniversary**: For wedding anniversaries and other yearly celebrations  
- **Death Anniversary**: For memorial dates
- **Graduation**: For graduation ceremonies and milestones
- **Promotion**: For work anniversaries and promotions
- **Custom**: For any other important personal dates

### Smart Notifications
- **Flexible Timing**: Remind 1 week before, 1 day before, same day, or custom days
- **Multiple Methods**: App notifications, email alerts, automatic task creation
- **Importance Levels**: 5-level importance scale (1-5) for prioritization

### Contact Integration
- **Optional Association**: Link reminders to contacts or create standalone reminders
- **Contact Information**: Automatically include contact name and nickname in notifications
- **Family Context**: Leverage existing family information for better context

### Task Integration
- **Automatic Tasks**: Create actionable tasks when reminders trigger
- **Smart Descriptions**: Include age, years since, and contact information in task descriptions
- **Priority Mapping**: High importance reminders create high priority tasks

## API Endpoints

All endpoints are available under `/api/v1/personal-reminders/`

### Core Operations
- `POST /` - Create a new personal reminder
- `GET /` - List personal reminders with filtering
- `GET /{id}` - Get a specific reminder
- `PUT /{id}` - Update a reminder
- `DELETE /{id}` - Delete a reminder

### Special Views
- `GET /upcoming` - Get upcoming reminders (customizable days ahead)
- `GET /today` - Get reminders happening today
- `GET /this-week` - Get reminders in the next 7 days
- `GET /search` - Search reminders by text

### Actions
- `POST /{id}/celebrate` - Mark a reminder as celebrated for a specific year

## Usage Examples

### Create a Birthday Reminder
```json
POST /api/v1/personal-reminders/
{
  "title": "Mom's Birthday",
  "contact_id": 123,
  "event_date": "1965-08-15",
  "reminder_type": "birthday",
  "reminder_preferences": {
    "week_before": true,
    "day_before": true,
    "same_day": true
  },
  "notification_methods": {
    "app_notification": true,
    "task_creation": true,
    "email": false
  },
  "importance_level": 5
}
```

### Create a Custom Reminder
```json
POST /api/v1/personal-reminders/
{
  "title": "Submit Tax Returns",
  "description": "Annual tax filing deadline",
  "event_date": "2024-04-15",
  "reminder_type": "custom",
  "is_recurring": true,
  "reminder_preferences": {
    "custom_days": [30, 14, 7, 1]
  },
  "notification_methods": {
    "task_creation": true,
    "app_notification": true
  },
  "importance_level": 4
}
```

### Get Upcoming Reminders
```bash
GET /api/v1/personal-reminders/upcoming?days_ahead=30
```

### Search Reminders
```bash
GET /api/v1/personal-reminders/search?q=birthday&reminder_type=birthday
```

## Background Processing

The system includes automatic background processing via Celery:

- **Daily Processing**: Runs at 7 AM daily to check for triggered reminders
- **Task Creation**: Automatically creates tasks when reminders trigger
- **Smart Descriptions**: Includes contact information, age calculations, and custom details

### Manual Processing (for testing)
```bash
POST /api/v1/background-tasks/process-personal-reminders
```

## Database Schema

### Personal Reminders Table
- `id` - Primary key
- `tenant_id` - Tenant isolation
- `user_id` - Owner of the reminder
- `title` - Reminder title
- `description` - Optional description
- `reminder_type` - Type of reminder (enum)
- `contact_id` - Optional contact association
- `event_date` - The date of the event
- `is_recurring` - Whether the reminder repeats yearly
- `reminder_preferences` - JSON configuration for when to remind
- `notification_methods` - JSON configuration for how to notify
- `importance_level` - Priority level (1-5)
- `last_celebrated_year` - Track when last celebrated
- `is_active` - Enable/disable the reminder
- `created_at`, `updated_at` - Timestamps

### Reminder Preferences JSON Format
```json
{
  "week_before": true,
  "day_before": true,
  "same_day": true,
  "custom_days": [30, 14, 7, 3, 1]
}
```

### Notification Methods JSON Format
```json
{
  "email": false,
  "app_notification": true,
  "task_creation": true
}
```

## Integration with Existing Systems

### Family Information System
- Leverage existing contact birthdays and anniversaries
- Automatically suggest reminders from contact information
- Use family nicknames in reminder descriptions

### Task System
- Create actionable tasks from triggered reminders
- Use existing task categories and priority system
- Maintain task-contact relationships

### Notification System
- Ready for email notification integration
- Support for app-based notifications
- Extensible for additional notification methods

## Migration

Run the migration to create the personal_reminders table:

```bash
alembic upgrade head
```

This adds the `024_add_personal_reminders` migration which creates the table with proper indexes for performance.

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_personal_reminder_crud.py
pytest tests/test_personal_reminder_integration.py  
pytest tests/test_background_task_integration.py
```

The test suite covers:
- Basic CRUD operations
- Filtering and search functionality
- Contact integration
- Background task processing
- Task creation logic
- Celebration tracking
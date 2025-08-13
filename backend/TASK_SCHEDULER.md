# Task Scheduler Service

The Task Scheduler Service automatically generates recurring tasks based on user-defined patterns and lead times.

## Overview

This service runs in the background and periodically scans for recurring task patterns that need new task instances generated. It supports various recurrence types and handles lead times to ensure tasks are created with appropriate advance notice.

## Core Features

### Automatic Task Generation
- Scans active recurring task patterns hourly
- Generates new task instances based on recurrence rules
- Respects user-defined lead times
- Handles different recurrence patterns (daily, weekly, monthly, yearly)

### End Condition Management
- **Date-based**: Stops generating after specific end date
- **Count-based**: Stops after maximum occurrences reached
- **Manual**: Users can disable recurrence anytime

### Lead Time Implementation
- Creates tasks X days before they're due
- Default lead time: 0 days (create on due date)
- User configurable per recurring task
- Example: Monthly bill reminder created 3 days early

## Recurrence Patterns

### Daily Recurrence
```python
recurrence_type = "daily"
recurrence_interval = 3  # Every 3 days
```

### Weekly Recurrence
```python
recurrence_type = "weekly"
recurrence_interval = 1  # Every week
days_of_week = "1,3,5"   # Monday, Wednesday, Friday (1=Mon, 2=Tue, etc.)
```

### Monthly Recurrence
```python
recurrence_type = "monthly"
recurrence_interval = 1   # Every month
day_of_month = 15        # 15th of each month
```

### Yearly Recurrence
```python
recurrence_type = "yearly"
recurrence_interval = 1  # Every year (same date)
```

## Database Schema

### New Fields Added

#### task_recurrence table
- `last_generated_at` (TIMESTAMP): When the last task was generated
- `next_generation_at` (TIMESTAMP): When the next task should be generated
- `generation_count` (INTEGER): Total number of tasks generated

#### tasks table
- `parent_task_id` (INTEGER): Links generated tasks to their recurring parent

## API Endpoints

### Task Scheduler Management

#### GET /api/v1/task-scheduler/status
Get the current status of the task scheduler service.

**Response:**
```json
{
  "is_running": true,
  "scheduler_state": "running",
  "jobs": [
    {
      "id": "generate_recurring_tasks",
      "name": "Generate Recurring Tasks",
      "next_run_time": "2025-01-15T15:00:00"
    }
  ]
}
```

#### POST /api/v1/task-scheduler/generate
Manually trigger task generation for testing/debugging.

**Response:**
```json
{
  "message": "Manual task generation completed",
  "stats": {
    "total_recurrences_checked": 10,
    "tasks_generated": 3,
    "errors": 0
  }
}
```

#### POST /api/v1/task-scheduler/start
Start the task scheduler service.

#### POST /api/v1/task-scheduler/stop
Stop the task scheduler service.

## Configuration

### Environment Variables
- Schedule timing is configurable via the service implementation
- Default: Generate every hour, cleanup every 6 hours

### Logging
The service provides comprehensive logging for:
- Task generation events
- Error conditions
- Performance metrics
- Scheduler lifecycle events

## Usage Examples

### Creating a Recurring Task
When a user creates a recurring task through the existing task API endpoints, they can specify:

```json
{
  "title": "Monthly Budget Review",
  "description": "Review and update monthly budget",
  "is_recurring": true,
  "recurrence": {
    "recurrence_type": "monthly",
    "recurrence_interval": 1,
    "day_of_month": 1,
    "lead_time_days": 3,
    "end_date": "2025-12-31"
  }
}
```

This will:
1. Create the base recurring task
2. The scheduler will automatically generate instances 3 days before the 1st of each month
3. Stop generating after December 31, 2025

### Manual Generation
For testing or immediate generation:

```bash
curl -X POST /api/v1/task-scheduler/generate \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: default"
```

## Error Handling

### Edge Cases Handled
- **Timezone changes**: DST transitions handled gracefully
- **Invalid dates**: Skips generation for impossible dates (e.g., Feb 30)
- **System downtime**: Catches up on missed generations
- **Duplicate prevention**: Avoids generating the same task multiple times
- **Calendar edge cases**: Handles last day of month, leap years

### Error Recovery
- Failed generations are logged but don't stop the service
- Database rollback on errors prevents partial state
- Service continues processing other recurrences if one fails

## Performance Considerations

### Optimization Features
- Efficient database queries with proper indexing
- Batch processing for multiple task generations
- Asynchronous processing to avoid blocking
- Rate limiting to prevent system overload

### Scalability
- Designed to handle 1000+ recurring tasks
- Efficient filtering of recurrences due for generation
- Minimal database impact during normal operation

## Monitoring and Observability

### Logging Levels
- **INFO**: Normal operation, task generation events
- **WARNING**: Non-critical issues, skipped generations
- **ERROR**: Critical failures, service issues

### Metrics Available
- Number of recurrences processed
- Tasks generated per run
- Processing time per generation cycle
- Error rates and types

## Integration Points

### With Existing Task System
- Uses existing CRUD operations for task creation
- Maintains task relationships and associations
- Preserves user permissions and tenant isolation

### With Notification System (Future)
- Ready for integration with notification services
- Can trigger alerts for generated tasks
- Supports reminder workflows

## Testing

### Test Coverage
- Unit tests for date calculation logic
- Integration tests for full generation flow
- Edge case testing (leap years, DST, etc.)
- Performance testing with large datasets
- Failure recovery testing

### Manual Testing
Use the manual generation endpoint for testing:
1. Create recurring tasks with short intervals
2. Trigger manual generation
3. Verify correct task instances are created
4. Check lead time calculations

## Deployment

### Automatic Startup
The scheduler starts automatically when the FastAPI application starts and stops when the application shuts down.

### Health Checks
Monitor the `/api/v1/task-scheduler/status` endpoint to ensure the service is running properly.

### Maintenance
- Review logs regularly for any recurring errors
- Monitor generation statistics for performance trends
- Adjust lead times based on user feedback

## Future Enhancements

### Potential Improvements
- Dynamic scheduling intervals based on load
- Advanced recurrence patterns (e.g., "every 2nd Tuesday")
- Bulk operations for managing multiple recurrences
- Integration with calendar systems
- Advanced notification options
- Analytics and reporting on recurring task patterns
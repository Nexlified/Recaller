import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.crud import personal_reminder
from app.schemas.personal_reminder import (
    PersonalReminderCreate, PersonalReminderUpdate, 
    ReminderTypeEnum, ImportanceLevelEnum
)
from app.models.personal_reminder import PersonalReminder


class TestPersonalReminderCRUD:
    """Test Personal Reminder CRUD operations."""
    
    def test_create_reminder_minimal(self, db_session: Session):
        """Test creating a reminder with minimal data."""
        reminder_data = PersonalReminderCreate(
            title="Test Birthday",
            event_date=date(2024, 6, 15),
            reminder_type=ReminderTypeEnum.BIRTHDAY
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_reminder.id is not None
        assert created_reminder.title == "Test Birthday"
        assert created_reminder.user_id == 1
        assert created_reminder.tenant_id == 1
        assert created_reminder.reminder_type == ReminderTypeEnum.BIRTHDAY.value
        assert created_reminder.importance_level == ImportanceLevelEnum.MEDIUM.value
        assert created_reminder.is_recurring is True
        assert created_reminder.is_active is True
    
    def test_create_reminder_with_all_fields(self, db_session: Session):
        """Test creating a reminder with all optional fields."""
        reminder_data = PersonalReminderCreate(
            title="Anniversary Reminder",
            description="Wedding anniversary celebration",
            reminder_type=ReminderTypeEnum.ANNIVERSARY,
            contact_id=1,
            event_date=date(2020, 8, 20),
            is_recurring=True,
            reminder_preferences={
                "week_before": True,
                "day_before": True,
                "same_day": True,
                "custom_days": [7, 3, 1]
            },
            notification_methods={
                "email": False,
                "app_notification": True,
                "task_creation": True
            },
            importance_level=ImportanceLevelEnum.HIGH,
            last_celebrated_year=2023,
            is_active=True
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_reminder.id is not None
        assert created_reminder.title == "Anniversary Reminder"
        assert created_reminder.description == "Wedding anniversary celebration"
        assert created_reminder.contact_id == 1
        assert created_reminder.reminder_type == ReminderTypeEnum.ANNIVERSARY.value
        assert created_reminder.importance_level == ImportanceLevelEnum.HIGH.value
        assert created_reminder.last_celebrated_year == 2023
        assert created_reminder.reminder_preferences["week_before"] is True
        assert created_reminder.notification_methods["task_creation"] is True
    
    def test_get_upcoming_reminders(self, db_session: Session):
        """Test getting upcoming reminders."""
        # Create a reminder for next month
        next_month = date.today() + timedelta(days=20)
        reminder_data = PersonalReminderCreate(
            title="Upcoming Birthday",
            event_date=next_month,
            reminder_type=ReminderTypeEnum.BIRTHDAY
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Test getting upcoming reminders
        upcoming = personal_reminder.get_upcoming_reminders(
            db=db_session,
            user_id=1,
            tenant_id=1,
            days_ahead=30
        )
        
        assert len(upcoming) > 0
        assert any(r.reminder_id == created_reminder.id for r in upcoming)
    
    def test_update_reminder(self, db_session: Session):
        """Test updating a reminder."""
        # Create a reminder first
        reminder_data = PersonalReminderCreate(
            title="Original Title",
            event_date=date(2024, 12, 25),
            reminder_type=ReminderTypeEnum.CUSTOM
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Update the reminder
        update_data = PersonalReminderUpdate(
            title="Updated Title",
            importance_level=ImportanceLevelEnum.HIGH,
            is_active=False
        )
        
        updated_reminder = personal_reminder.update_reminder(
            db=db_session,
            db_obj=created_reminder,
            obj_in=update_data
        )
        
        assert updated_reminder.title == "Updated Title"
        assert updated_reminder.importance_level == ImportanceLevelEnum.HIGH.value
        assert updated_reminder.is_active is False
    
    def test_search_reminders(self, db_session: Session):
        """Test searching reminders."""
        # Create reminders with searchable titles
        reminder1_data = PersonalReminderCreate(
            title="Birthday Party Planning",
            event_date=date(2024, 6, 15),
            reminder_type=ReminderTypeEnum.BIRTHDAY
        )
        
        reminder2_data = PersonalReminderCreate(
            title="Anniversary Dinner",
            event_date=date(2024, 8, 20),
            reminder_type=ReminderTypeEnum.ANNIVERSARY
        )
        
        personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder1_data,
            user_id=1,
            tenant_id=1
        )
        
        personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder2_data,
            user_id=1,
            tenant_id=1
        )
        
        # Search for reminders
        results = personal_reminder.search_reminders(
            db=db_session,
            user_id=1,
            tenant_id=1,
            query="birthday"
        )
        
        assert len(results) >= 1
        assert any("Birthday" in r.title for r in results)
    
    def test_delete_reminder(self, db_session: Session):
        """Test deleting a reminder."""
        # Create a reminder first
        reminder_data = PersonalReminderCreate(
            title="To Be Deleted",
            event_date=date(2024, 12, 31),
            reminder_type=ReminderTypeEnum.CUSTOM
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Delete the reminder
        success = personal_reminder.delete_reminder(
            db=db_session,
            reminder_id=created_reminder.id,
            tenant_id=1
        )
        
        assert success is True
        
        # Verify it's deleted
        deleted_reminder = personal_reminder.get_reminder(
            db=db_session,
            reminder_id=created_reminder.id,
            tenant_id=1
        )
        
        assert deleted_reminder is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
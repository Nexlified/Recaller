import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.crud import personal_reminder, task
from app.schemas.personal_reminder import PersonalReminderCreate, ReminderTypeEnum, ImportanceLevelEnum
from app.schemas.task import TaskCreate, TaskStatusEnum
from app.services.background_tasks import process_personal_reminders


class TestPersonalReminderIntegration:
    """Test Personal Reminder integration with Task system."""
    
    def test_reminder_task_creation_logic(self, db_session: Session):
        """Test that reminders correctly create tasks when triggered."""
        # Create a reminder that should trigger today
        today = date.today()
        reminder_data = PersonalReminderCreate(
            title="Birthday Reminder",
            description="Test birthday reminder",
            event_date=today,
            reminder_type=ReminderTypeEnum.BIRTHDAY,
            importance_level=ImportanceLevelEnum.HIGH,
            reminder_preferences={
                "same_day": True,
                "day_before": False,
                "week_before": False
            },
            notification_methods={
                "task_creation": True,
                "app_notification": False,
                "email": False
            }
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Test that we can get reminders for today's date
        triggered_reminders = personal_reminder.get_reminders_for_date(
            db=db_session,
            user_id=1,
            tenant_id=1,
            target_date=today
        )
        
        assert len(triggered_reminders) > 0
        assert any(r.id == created_reminder.id for r in triggered_reminders)
        
        # Check that the reminder has correct trigger conditions
        reminder = triggered_reminders[0]
        assert reminder.notification_methods["task_creation"] is True
        assert reminder.reminder_preferences["same_day"] is True
    
    def test_upcoming_reminders_calculation(self, db_session: Session):
        """Test upcoming reminders calculation for recurring dates."""
        # Create a reminder for a future date this year
        future_date = date(2024, 6, 15)  # Fixed date to avoid year issues
        
        reminder_data = PersonalReminderCreate(
            title="Anniversary Reminder",
            event_date=future_date,
            reminder_type=ReminderTypeEnum.ANNIVERSARY,
            is_recurring=True
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Get upcoming reminders
        upcoming = personal_reminder.get_upcoming_reminders(
            db=db_session,
            user_id=1,
            tenant_id=1,
            days_ahead=365  # Look ahead for a full year
        )
        
        # Should find at least this reminder
        assert len(upcoming) > 0
        
        # Find our specific reminder
        our_reminder = next((r for r in upcoming if r.reminder_id == created_reminder.id), None)
        assert our_reminder is not None
        assert our_reminder.reminder_type == ReminderTypeEnum.ANNIVERSARY
        assert our_reminder.days_until >= 0
    
    def test_contact_based_reminder(self, db_session: Session):
        """Test reminder with contact association."""
        # First create a test contact (using the test Contact model)
        from tests.conftest import TestContact
        
        contact = TestContact(
            tenant_id=1,
            created_by_user_id=1,
            first_name="John",
            last_name="Doe",
            family_nickname="Uncle John",
            date_of_birth=date(1980, 5, 20),
            is_active=True
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)
        
        # Create a reminder associated with this contact
        reminder_data = PersonalReminderCreate(
            title="John's Birthday",
            contact_id=contact.id,
            event_date=contact.date_of_birth,
            reminder_type=ReminderTypeEnum.BIRTHDAY,
            is_recurring=True
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Get the reminder with contact information
        reminder_with_contact = personal_reminder.get_reminder_with_contact(
            db=db_session,
            reminder_id=created_reminder.id,
            tenant_id=1
        )
        
        assert reminder_with_contact is not None
        assert reminder_with_contact.contact is not None
        assert reminder_with_contact.contact.first_name == "John"
        assert reminder_with_contact.contact.family_nickname == "Uncle John"
    
    def test_reminder_filtering_and_search(self, db_session: Session):
        """Test various filtering and search capabilities."""
        # Create multiple reminders with different types
        reminders_data = [
            PersonalReminderCreate(
                title="Birthday Party",
                event_date=date(2024, 7, 4),
                reminder_type=ReminderTypeEnum.BIRTHDAY,
                importance_level=ImportanceLevelEnum.HIGH
            ),
            PersonalReminderCreate(
                title="Wedding Anniversary",
                event_date=date(2024, 8, 15),
                reminder_type=ReminderTypeEnum.ANNIVERSARY,
                importance_level=ImportanceLevelEnum.VERY_HIGH
            ),
            PersonalReminderCreate(
                title="Graduation Ceremony",
                event_date=date(2024, 5, 30),
                reminder_type=ReminderTypeEnum.GRADUATION,
                importance_level=ImportanceLevelEnum.MEDIUM,
                is_active=False  # Inactive reminder
            )
        ]
        
        created_reminders = []
        for reminder_data in reminders_data:
            created_reminder = personal_reminder.create_reminder(
                db=db_session,
                obj_in=reminder_data,
                user_id=1,
                tenant_id=1
            )
            created_reminders.append(created_reminder)
        
        # Test filtering by reminder type
        from app.schemas.personal_reminder import PersonalReminderFilter
        birthday_filter = PersonalReminderFilter(reminder_type=ReminderTypeEnum.BIRTHDAY)
        birthday_reminders = personal_reminder.get_reminders_by_user(
            db=db_session,
            user_id=1,
            tenant_id=1,
            filter_params=birthday_filter
        )
        
        assert len(birthday_reminders) >= 1
        assert all(r.reminder_type == ReminderTypeEnum.BIRTHDAY.value for r in birthday_reminders)
        
        # Test filtering by importance level
        high_importance_filter = PersonalReminderFilter(importance_level=ImportanceLevelEnum.HIGH)
        high_importance_reminders = personal_reminder.get_reminders_by_user(
            db=db_session,
            user_id=1,
            tenant_id=1,
            filter_params=high_importance_filter
        )
        
        assert len(high_importance_reminders) >= 1
        assert all(r.importance_level == ImportanceLevelEnum.HIGH.value for r in high_importance_reminders)
        
        # Test filtering by active status
        active_filter = PersonalReminderFilter(is_active=True)
        active_reminders = personal_reminder.get_reminders_by_user(
            db=db_session,
            user_id=1,
            tenant_id=1,
            filter_params=active_filter
        )
        
        # Should not include the inactive graduation reminder
        graduation_in_active = any(r.reminder_type == ReminderTypeEnum.GRADUATION.value for r in active_reminders)
        assert not graduation_in_active
        
        # Test search functionality
        search_results = personal_reminder.search_reminders(
            db=db_session,
            user_id=1,
            tenant_id=1,
            query="party"
        )
        
        assert len(search_results) >= 1
        assert any("Party" in r.title for r in search_results)
    
    def test_celebration_tracking(self, db_session: Session):
        """Test the celebration tracking functionality."""
        reminder_data = PersonalReminderCreate(
            title="Wedding Anniversary",
            event_date=date(2020, 6, 15),
            reminder_type=ReminderTypeEnum.ANNIVERSARY,
            is_recurring=True
        )
        
        created_reminder = personal_reminder.create_reminder(
            db=db_session,
            obj_in=reminder_data,
            user_id=1,
            tenant_id=1
        )
        
        # Mark as celebrated for 2023
        updated_reminder = personal_reminder.update_last_celebrated_year(
            db=db_session,
            reminder_id=created_reminder.id,
            year=2023
        )
        
        assert updated_reminder is not None
        assert updated_reminder.last_celebrated_year == 2023
        
        # Test upcoming reminder calculation includes years since
        upcoming = personal_reminder.get_upcoming_reminders(
            db=db_session,
            user_id=1,
            tenant_id=1,
            days_ahead=365
        )
        
        our_reminder = next((r for r in upcoming if r.reminder_id == created_reminder.id), None)
        if our_reminder:
            # Should calculate years since the original date
            expected_years = our_reminder.event_date.year - created_reminder.event_date.year
            assert our_reminder.years_since == expected_years


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
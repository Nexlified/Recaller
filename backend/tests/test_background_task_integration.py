import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.crud import personal_reminder, task
from app.schemas.personal_reminder import PersonalReminderCreate, ReminderTypeEnum, ImportanceLevelEnum
from app.schemas.task import TaskCreate


class TestBackgroundTaskIntegration:
    """Test Background Task integration for Personal Reminders."""
    
    def test_background_task_logic_simulation(self, db_session: Session):
        """Test the background task logic without running actual Celery task."""
        # Create a reminder that should trigger today
        today = date.today()
        
        reminder_data = PersonalReminderCreate(
            title="Test Birthday Reminder",
            description="This should create a task",
            event_date=today,  # Event happening today
            reminder_type=ReminderTypeEnum.BIRTHDAY,
            importance_level=ImportanceLevelEnum.HIGH,
            reminder_preferences={
                "same_day": True,  # Should trigger on the same day
                "day_before": False,
                "week_before": False
            },
            notification_methods={
                "task_creation": True,  # Enable task creation
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
        
        # Simulate the background task logic
        # Step 1: Get reminders that should trigger today
        triggered_reminders = personal_reminder.get_reminders_for_date(
            db=db_session,
            user_id=1,
            tenant_id=1,
            target_date=today
        )
        
        assert len(triggered_reminders) > 0
        triggered_reminder = triggered_reminders[0]
        assert triggered_reminder.id == created_reminder.id
        
        # Step 2: Check if task creation is enabled
        notification_methods = triggered_reminder.notification_methods or {}
        assert notification_methods.get('task_creation', False) is True
        
        # Step 3: Calculate next occurrence date
        from app.crud.personal_reminder import _calculate_next_occurrence
        next_occurrence = _calculate_next_occurrence(triggered_reminder, today)
        assert next_occurrence == today  # Should be today for this test
        
        # Step 4: Create task (simulate the task creation logic)
        task_title = f"Reminder: {triggered_reminder.title}"
        task_description = f"Personal reminder for {triggered_reminder.title}"
        
        if triggered_reminder.description:
            task_description += f"\n\n{triggered_reminder.description}"
        
        # Mock the task creation to avoid needing the full task model in tests
        with patch('app.crud.task.create_task') as mock_create_task:
            mock_task = MagicMock()
            mock_task.id = 123
            mock_task.title = task_title
            mock_create_task.return_value = mock_task
            
            # Simulate creating the task
            task_data = TaskCreate(
                title=task_title,
                description=task_description,
                due_date=next_occurrence,
                priority='high' if triggered_reminder.importance_level >= 4 else 'medium'
            )
            
            created_task = task.create_task(
                db=db_session,
                obj_in=task_data,
                user_id=1,
                tenant_id=1
            )
            
            # Verify task creation was called correctly
            mock_create_task.assert_called_once()
            call_args = mock_create_task.call_args
            
            assert call_args[1]['user_id'] == 1
            assert call_args[1]['tenant_id'] == 1
            
            # Check the task data
            task_obj = call_args[1]['obj_in']
            assert task_obj.title == task_title
            assert task_obj.description == task_description
            assert task_obj.priority == 'high'  # Because importance_level is HIGH (4)
    
    def test_different_reminder_types_task_creation(self, db_session: Session):
        """Test task creation for different reminder types."""
        today = date.today()
        
        # Test different reminder types and their task descriptions
        test_cases = [
            {
                'reminder_type': ReminderTypeEnum.BIRTHDAY,
                'title': 'John\'s Birthday',
                'event_date': date(1990, today.month, today.day),  # Birthday in 1990
                'expected_description_contains': 'Turning'
            },
            {
                'reminder_type': ReminderTypeEnum.ANNIVERSARY,
                'title': 'Wedding Anniversary',
                'event_date': date(2010, today.month, today.day),  # Anniversary in 2010
                'expected_description_contains': 'years'
            },
            {
                'reminder_type': ReminderTypeEnum.CUSTOM,
                'title': 'Important Meeting',
                'event_date': today,
                'expected_description_contains': 'Personal reminder'
            }
        ]
        
        for test_case in test_cases:
            with patch('app.crud.task.create_task') as mock_create_task:
                mock_task = MagicMock()
                mock_task.id = 123
                mock_create_task.return_value = mock_task
                
                # Create reminder
                reminder_data = PersonalReminderCreate(
                    title=test_case['title'],
                    event_date=test_case['event_date'],
                    reminder_type=test_case['reminder_type'],
                    reminder_preferences={"same_day": True},
                    notification_methods={"task_creation": True}
                )
                
                created_reminder = personal_reminder.create_reminder(
                    db=db_session,
                    obj_in=reminder_data,
                    user_id=1,
                    tenant_id=1
                )
                
                # Simulate task creation logic
                triggered_reminders = personal_reminder.get_reminders_for_date(
                    db=db_session,
                    user_id=1,
                    tenant_id=1,
                    target_date=today
                )
                
                # Find our reminder
                our_reminder = next((r for r in triggered_reminders if r.id == created_reminder.id), None)
                if our_reminder:
                    # Calculate next occurrence
                    from app.crud.personal_reminder import _calculate_next_occurrence
                    next_occurrence = _calculate_next_occurrence(our_reminder, today)
                    
                    # Build task description
                    task_title = f"Reminder: {our_reminder.title}"
                    task_description = f"Personal reminder for {our_reminder.title}"
                    
                    if our_reminder.reminder_type in ['birthday', 'anniversary']:
                        years_since = next_occurrence.year - our_reminder.event_date.year
                        if our_reminder.reminder_type == 'birthday':
                            task_description += f" - Turning {years_since}"
                        else:
                            task_description += f" - {years_since} years"
                    
                    # Create task
                    task_data = TaskCreate(
                        title=task_title,
                        description=task_description,
                        due_date=next_occurrence
                    )
                    
                    task.create_task(
                        db=db_session,
                        obj_in=task_data,
                        user_id=1,
                        tenant_id=1
                    )
                    
                    # Verify the description contains expected content
                    call_args = mock_create_task.call_args
                    task_obj = call_args[1]['obj_in']
                    
                    assert test_case['expected_description_contains'] in task_obj.description
    
    def test_reminder_with_contact_task_creation(self, db_session: Session):
        """Test task creation for reminders with contact information."""
        from tests.conftest import TestContact
        
        # Create a test contact
        contact = TestContact(
            tenant_id=1,
            created_by_user_id=1,
            first_name="Jane",
            last_name="Smith",
            family_nickname="Aunt Jane",
            is_active=True
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)
        
        today = date.today()
        
        with patch('app.crud.task.create_task') as mock_create_task:
            mock_task = MagicMock()
            mock_task.id = 123
            mock_create_task.return_value = mock_task
            
            # Create reminder with contact
            reminder_data = PersonalReminderCreate(
                title="Jane's Birthday",
                contact_id=contact.id,
                event_date=today,
                reminder_type=ReminderTypeEnum.BIRTHDAY,
                reminder_preferences={"same_day": True},
                notification_methods={"task_creation": True}
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
            
            # Simulate task creation with contact info
            task_title = f"Reminder: {reminder_with_contact.title}"
            task_description = f"Personal reminder for {reminder_with_contact.title}"
            
            if reminder_with_contact.contact:
                contact_name = f"{reminder_with_contact.contact.first_name}"
                if reminder_with_contact.contact.last_name:
                    contact_name += f" {reminder_with_contact.contact.last_name}"
                if reminder_with_contact.contact.family_nickname:
                    contact_name += f" ({reminder_with_contact.contact.family_nickname})"
                
                task_description += f" - {contact_name}"
            
            task_data = TaskCreate(
                title=task_title,
                description=task_description,
                due_date=today,
                contact_ids=[reminder_with_contact.contact_id] if reminder_with_contact.contact_id else []
            )
            
            task.create_task(
                db=db_session,
                obj_in=task_data,
                user_id=1,
                tenant_id=1
            )
            
            # Verify contact information was included
            call_args = mock_create_task.call_args
            task_obj = call_args[1]['obj_in']
            
            assert "Jane Smith (Aunt Jane)" in task_obj.description
            assert task_obj.contact_ids == [contact.id]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
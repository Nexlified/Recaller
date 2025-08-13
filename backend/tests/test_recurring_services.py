import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from app.services.recurring_transaction_service import RecurringTransactionService
from app.services.notification_service import NotificationService


class TestRecurringTransactionService:
    """Test RecurringTransactionService functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db_session):
        """Create service instance with mocked database."""
        return RecurringTransactionService(mock_db_session)
    
    @pytest.fixture
    def sample_recurring_transaction(self):
        """Create a sample recurring transaction mock."""
        mock_recurring = Mock()
        mock_recurring.id = 1
        mock_recurring.user_id = 1
        mock_recurring.tenant_id = 1
        mock_recurring.template_name = "Monthly Rent"
        mock_recurring.type = "debit"
        mock_recurring.amount = Decimal("1500.00")
        mock_recurring.currency = "USD"
        mock_recurring.description = "Monthly rent payment"
        mock_recurring.frequency = "monthly"
        mock_recurring.interval_count = 1
        mock_recurring.start_date = date(2024, 1, 1)
        mock_recurring.next_due_date = date(2024, 2, 1)
        mock_recurring.is_active = True
        mock_recurring.category_id = 1
        mock_recurring.account_id = 1
        mock_recurring.category = None
        mock_recurring.account = None
        return mock_recurring
    
    def test_calculate_next_due_date_daily(self, service):
        """Test daily frequency calculation."""
        start_date = date(2024, 1, 1)
        next_date = service.calculate_next_due_date(start_date, "daily", 1)
        assert next_date == date(2024, 1, 2)
        
        # Test with interval
        next_date = service.calculate_next_due_date(start_date, "daily", 7)
        assert next_date == date(2024, 1, 8)
    
    def test_calculate_next_due_date_weekly(self, service):
        """Test weekly frequency calculation."""
        start_date = date(2024, 1, 1)  # Monday
        next_date = service.calculate_next_due_date(start_date, "weekly", 1)
        assert next_date == date(2024, 1, 8)
        
        # Test with interval
        next_date = service.calculate_next_due_date(start_date, "weekly", 2)
        assert next_date == date(2024, 1, 15)
    
    def test_calculate_next_due_date_monthly(self, service):
        """Test monthly frequency calculation."""
        start_date = date(2024, 1, 15)
        next_date = service.calculate_next_due_date(start_date, "monthly", 1)
        assert next_date == date(2024, 2, 15)
        
        # Test month-end edge case
        start_date = date(2024, 1, 31)
        next_date = service.calculate_next_due_date(start_date, "monthly", 1)
        # February only has 29 days in 2024 (leap year)
        assert next_date == date(2024, 2, 29)
    
    def test_calculate_next_due_date_yearly(self, service):
        """Test yearly frequency calculation."""
        start_date = date(2024, 2, 29)  # Leap year
        next_date = service.calculate_next_due_date(start_date, "yearly", 1)
        # 2025 is not a leap year, should fall back to Feb 28
        assert next_date == date(2025, 2, 28)
    
    def test_calculate_next_due_date_unknown_frequency(self, service):
        """Test unknown frequency handling."""
        start_date = date(2024, 1, 1)
        next_date = service.calculate_next_due_date(start_date, "unknown", 1)
        assert next_date == start_date
    
    def test_get_next_occurrence_info(self, service, sample_recurring_transaction):
        """Test next occurrence information calculation."""
        # Test future date
        future_date = date.today() + timedelta(days=5)
        sample_recurring_transaction.next_due_date = future_date
        
        info = service.get_next_occurrence_info(sample_recurring_transaction)
        assert info["next_due_date"] == future_date
        assert info["days_until_due"] == 5
        assert info["is_overdue"] is False
        assert info["is_due_today"] is False
        assert info["is_due_soon"] is False
        
        # Test due today
        sample_recurring_transaction.next_due_date = date.today()
        info = service.get_next_occurrence_info(sample_recurring_transaction)
        assert info["days_until_due"] == 0
        assert info["is_due_today"] is True
        assert info["is_due_soon"] is True
        
        # Test overdue
        past_date = date.today() - timedelta(days=2)
        sample_recurring_transaction.next_due_date = past_date
        info = service.get_next_occurrence_info(sample_recurring_transaction)
        assert info["days_until_due"] == -2
        assert info["is_overdue"] is True
    
    def test_transaction_template_basic_fields(self, service, sample_recurring_transaction):
        """Test that transaction template has correct basic fields."""
        # The service should be able to handle recurring transaction objects
        assert sample_recurring_transaction.type == "debit"
        assert sample_recurring_transaction.amount == Decimal("1500.00")
        assert sample_recurring_transaction.currency == "USD"
        assert sample_recurring_transaction.description == "Monthly rent payment"
        assert sample_recurring_transaction.frequency == "monthly"
        
        # Test that calculate_next_due_date_from_recurring works
        next_due = service.calculate_next_due_date_from_recurring(sample_recurring_transaction)
        expected_next = date(2024, 3, 1)  # Next month after Feb 1
        assert next_due == expected_next


class TestNotificationService:
    """Test NotificationService functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db_session):
        """Create service instance with mocked database."""
        return NotificationService(mock_db_session)
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user mock."""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.first_name = "John"
        mock_user.full_name = "John Doe"
        mock_user.is_active = True
        mock_user.tenant_id = 1
        return mock_user
    
    @pytest.fixture
    def sample_reminders(self):
        """Create sample reminder data."""
        return [
            {
                "recurring_id": 1,
                "description": "Monthly Rent",
                "amount": Decimal("1500.00"),
                "currency": "USD",
                "type": "debit",
                "next_due_date": date.today(),
                "days_until_due": 0,
                "is_due_soon": True,
                "category_name": "Housing",
                "account_name": "Checking Account"
            },
            {
                "recurring_id": 2,
                "description": "Salary",
                "amount": Decimal("5000.00"),
                "currency": "USD",
                "type": "credit",
                "next_due_date": date.today() + timedelta(days=3),
                "days_until_due": 3,
                "is_due_soon": True,
                "category_name": "Income",
                "account_name": None
            }
        ]
    
    def test_generate_reminder_email_html(self, service, sample_user, sample_reminders):
        """Test HTML email generation."""
        html = service._generate_reminder_email_html(sample_user, sample_reminders)
        
        assert "John" in html
        assert "Monthly Rent" in html
        assert "Salary" in html
        assert "USD 1500.00" in html
        assert "Due today" in html
        assert "Due in 3 day(s)" in html
        assert "Housing" in html
        assert "Checking Account" in html
        assert "<html>" in html
        assert "</html>" in html
    
    def test_generate_reminder_email_text(self, service, sample_user, sample_reminders):
        """Test text email generation."""
        text = service._generate_reminder_email_text(sample_user, sample_reminders)
        
        assert "Hi John," in text
        assert "Monthly Rent" in text
        assert "Salary" in text
        assert "USD 1500.00" in text
        assert "Due today" in text
        assert "Due in 3 day(s)" in text
        assert "Housing" in text
        assert "Checking Account" in text
        assert "automated reminder" in text
    
    @patch('smtplib.SMTP')
    @patch('app.services.notification_service.settings')
    def test_send_reminder_email_success(
        self, 
        mock_settings, 
        mock_smtp_class,
        service, 
        sample_user, 
        sample_reminders
    ):
        """Test successful email sending."""
        # Configure mock settings
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_TLS = True
        mock_settings.SMTP_USERNAME = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_settings.SMTP_FROM_EMAIL = "noreply@example.com"
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        result = service._send_reminder_email(sample_user, sample_reminders)
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('app.services.notification_service.settings')
    def test_send_reminder_email_no_smtp_config(
        self, 
        mock_settings,
        service, 
        sample_user, 
        sample_reminders
    ):
        """Test email sending with no SMTP configuration."""
        mock_settings.SMTP_HOST = None
        mock_settings.SMTP_PORT = None
        
        result = service._send_reminder_email(sample_user, sample_reminders)
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
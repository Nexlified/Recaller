import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from decimal import Decimal

from app.services.recurring_transaction_service import RecurringTransactionService
from app.services.notification_service import NotificationService


class TestServiceIntegration:
    """Integration tests for the recurring transaction and notification services."""
    
    def test_service_initialization(self):
        """Test that services can be initialized properly."""
        mock_db = Mock()
        
        # Test RecurringTransactionService initialization
        recurring_service = RecurringTransactionService(mock_db)
        assert recurring_service.db == mock_db
        
        # Test NotificationService initialization
        notification_service = NotificationService(mock_db)
        assert notification_service.db == mock_db
        assert isinstance(notification_service.recurring_service, RecurringTransactionService)
    
    def test_date_calculation_integration(self):
        """Test date calculation methods work together correctly."""
        mock_db = Mock()
        service = RecurringTransactionService(mock_db)
        
        # Test various date calculations
        start_date = date(2024, 1, 15)
        
        # Daily
        daily_next = service.calculate_next_due_date(start_date, "daily", 5)
        assert daily_next == date(2024, 1, 20)
        
        # Weekly  
        weekly_next = service.calculate_next_due_date(start_date, "weekly", 2)
        assert weekly_next == date(2024, 1, 29)
        
        # Monthly
        monthly_next = service.calculate_next_due_date(start_date, "monthly", 3)
        assert monthly_next == date(2024, 4, 15)
        
        # Yearly
        yearly_next = service.calculate_next_due_date(start_date, "yearly", 2)
        assert yearly_next == date(2026, 1, 15)
    
    def test_occurrence_info_comprehensive(self):
        """Test occurrence info calculation for various scenarios."""
        mock_db = Mock()
        service = RecurringTransactionService(mock_db)
        
        # Create mock recurring transaction
        mock_recurring = Mock()
        
        # Test future due date
        mock_recurring.next_due_date = date.today() + timedelta(days=10)
        info = service.get_next_occurrence_info(mock_recurring)
        assert info["days_until_due"] == 10
        assert info["is_overdue"] is False
        assert info["is_due_today"] is False
        assert info["is_due_soon"] is False
        
        # Test due soon
        mock_recurring.next_due_date = date.today() + timedelta(days=2)
        info = service.get_next_occurrence_info(mock_recurring)
        assert info["days_until_due"] == 2
        assert info["is_due_soon"] is True
        
        # Test due today
        mock_recurring.next_due_date = date.today()
        info = service.get_next_occurrence_info(mock_recurring)
        assert info["days_until_due"] == 0
        assert info["is_due_today"] is True
        assert info["is_due_soon"] is True
        
        # Test overdue
        mock_recurring.next_due_date = date.today() - timedelta(days=3)
        info = service.get_next_occurrence_info(mock_recurring)
        assert info["days_until_due"] == -3
        assert info["is_overdue"] is True
    
    def test_notification_email_generation_integration(self):
        """Test that notification email generation works with various data."""
        mock_db = Mock()
        service = NotificationService(mock_db)
        
        # Create mock user
        mock_user = Mock()
        mock_user.first_name = "Alice"
        mock_user.email = "alice@example.com"
        
        # Create sample reminders with various scenarios
        reminders = [
            {
                "recurring_id": 1,
                "description": "Rent Payment",
                "amount": Decimal("1200.00"),
                "currency": "USD",
                "type": "debit",
                "next_due_date": date.today(),
                "days_until_due": 0,
                "is_due_soon": True,
                "category_name": "Housing",
                "account_name": "Checking"
            },
            {
                "recurring_id": 2,
                "description": "Salary Deposit",
                "amount": Decimal("5000.00"),
                "currency": "USD",
                "type": "credit",
                "next_due_date": date.today() + timedelta(days=1),
                "days_until_due": 1,
                "is_due_soon": True,
                "category_name": "Income",
                "account_name": None
            },
            {
                "recurring_id": 3,
                "description": "Insurance Premium",
                "amount": Decimal("300.50"),
                "currency": "USD",
                "type": "debit",
                "next_due_date": date.today() + timedelta(days=7),
                "days_until_due": 7,
                "is_due_soon": False,
                "category_name": "Insurance",
                "account_name": "Savings"
            }
        ]
        
        # Test HTML email generation
        html_content = service._generate_reminder_email_html(mock_user, reminders)
        
        # Verify key content is present
        assert "Alice" in html_content
        assert "Rent Payment" in html_content
        assert "Salary Deposit" in html_content
        assert "Insurance Premium" in html_content
        assert "USD 1200.00" in html_content
        assert "USD 5000.00" in html_content
        assert "USD 300.50" in html_content
        assert "Due today" in html_content
        assert "Due in 1 day(s)" in html_content
        assert "Due in 7 day(s)" in html_content
        assert "Housing" in html_content
        assert "Income" in html_content
        assert "Insurance" in html_content
        assert "Checking" in html_content
        assert "Savings" in html_content
        
        # Test text email generation
        text_content = service._generate_reminder_email_text(mock_user, reminders)
        
        # Verify key content is present
        assert "Hi Alice," in text_content
        assert "Rent Payment" in text_content
        assert "Salary Deposit" in text_content
        assert "Insurance Premium" in text_content
        assert "USD 1200.00" in text_content
        assert "automated reminder" in text_content
    
    @patch('app.services.notification_service.settings')
    def test_email_sending_with_no_config(self, mock_settings):
        """Test email service handles missing SMTP configuration gracefully."""
        mock_db = Mock()
        service = NotificationService(mock_db)
        
        # Configure no SMTP settings
        mock_settings.SMTP_HOST = None
        mock_settings.SMTP_PORT = None
        
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        reminders = [{"description": "Test", "amount": Decimal("100")}]
        
        # Should return False when no SMTP configuration
        result = service._send_reminder_email(mock_user, reminders)
        assert result is False
    
    def test_frequency_edge_cases(self):
        """Test edge cases in frequency calculations."""
        mock_db = Mock()
        service = RecurringTransactionService(mock_db)
        
        # Test leap year handling
        leap_day = date(2024, 2, 29)
        next_year = service.calculate_next_due_date(leap_day, "yearly", 1)
        assert next_year == date(2025, 2, 28)  # Falls back to Feb 28 in non-leap year
        
        # Test month-end edge cases
        jan_31 = date(2024, 1, 31)
        feb_end = service.calculate_next_due_date(jan_31, "monthly", 1)
        assert feb_end == date(2024, 2, 29)  # 2024 is leap year
        
        # Test quarterly calculation
        start = date(2024, 1, 15)
        quarterly = service.calculate_next_due_date(start, "quarterly", 1)
        assert quarterly == date(2024, 4, 15)
        
        # Test unknown frequency
        unknown = service.calculate_next_due_date(start, "unknown", 1)
        assert unknown == start  # Should return start date unchanged


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
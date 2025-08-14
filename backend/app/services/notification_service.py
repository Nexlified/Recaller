from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging

from app import crud
from app.models.user import User
from app.core.config import settings
from app.services.recurring_transaction_service import RecurringTransactionService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.recurring_service = RecurringTransactionService(db)

    def send_recurring_transaction_reminders(
        self,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        reminder_days: List[int] = [7, 3, 1, 0]
    ) -> Dict[str, Any]:
        """Send reminders for upcoming recurring transactions."""
        notifications_sent = []
        failed_notifications = []
        
        # Get users to notify
        if user_id and tenant_id:
            users = [crud.user.get(self.db, id=user_id)]
        else:
            users = crud.user.get_all_active(self.db)
        
        for user in users:
            if not user or not user.email:
                continue
                
            try:
                # Get user's tenant
                user_tenant_id = tenant_id or user.tenant_id
                
                # Get upcoming recurring transactions
                upcoming = self.recurring_service.get_upcoming_recurring_transactions(
                    user_id=user.id,
                    tenant_id=user_tenant_id,
                    days_ahead=max(reminder_days) + 1
                )
                
                # Filter for reminder days
                reminders_to_send = []
                for transaction in upcoming:
                    days_until = transaction["days_until_due"]
                    if days_until in reminder_days:
                        reminders_to_send.append(transaction)
                
                if reminders_to_send:
                    # Send email notification
                    email_sent = self._send_reminder_email(user, reminders_to_send)
                    if email_sent:
                        notifications_sent.append({
                            "user_id": user.id,
                            "email": user.email,
                            "reminder_count": len(reminders_to_send),
                            "reminders": reminders_to_send
                        })
                    else:
                        failed_notifications.append({
                            "user_id": user.id,
                            "email": user.email,
                            "error": "Failed to send email"
                        })
                        
            except Exception as e:
                logger.error(f"Failed to send reminder to user {user.id}: {str(e)}")
                failed_notifications.append({
                    "user_id": user.id,
                    "email": getattr(user, 'email', 'unknown'),
                    "error": str(e)
                })
        
        return {
            "notifications_sent": len(notifications_sent),
            "failed_notifications": len(failed_notifications),
            "details": notifications_sent,
            "errors": failed_notifications
        }

    def _send_reminder_email(self, user: User, reminders: List[Dict[str, Any]]) -> bool:
        """Send reminder email to user."""
        try:
            if not settings.SMTP_HOST or not settings.SMTP_PORT:
                logger.warning("SMTP settings not configured, skipping email")
                return False
            
            # Create email content
            subject = f"Recaller: {len(reminders)} Upcoming Recurring Transaction(s)"
            
            # HTML email body
            html_body = self._generate_reminder_email_html(user, reminders)
            
            # Text email body
            text_body = self._generate_reminder_email_text(user, reminders)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = user.email
            
            # Attach text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            logger.info(f"Reminder email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            return False

    def _generate_reminder_email_html(self, user: User, reminders: List[Dict[str, Any]]) -> str:
        """Generate HTML email body for reminders."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .reminder {{ border: 1px solid #dee2e6; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .due-today {{ border-left: 4px solid #dc3545; }}
                .due-soon {{ border-left: 4px solid #ffc107; }}
                .due-later {{ border-left: 4px solid #28a745; }}
                .amount {{ font-weight: bold; }}
                .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Recurring Transaction Reminders</h2>
            </div>
            <div class="content">
                <p>Hi {getattr(user, 'first_name', None) or 'there'},</p>
                <p>You have {len(reminders)} upcoming recurring transaction(s):</p>
        """
        
        for reminder in reminders:
            days_until = reminder["days_until_due"]
            css_class = "due-today" if days_until == 0 else "due-soon" if days_until <= 3 else "due-later"
            
            due_text = "Due today" if days_until == 0 else f"Due in {days_until} day(s)"
            
            html += f"""
                <div class="reminder {css_class}">
                    <h4>{reminder['description']}</h4>
                    <p><span class="amount">{reminder['currency']} {reminder['amount']}</span> - {reminder['type'].title()}</p>
                    <p><strong>{due_text}</strong> - {reminder['next_due_date']}</p>
                    {f"<p>Category: {reminder['category_name']}</p>" if reminder['category_name'] else ""}
                    {f"<p>Account: {reminder['account_name']}</p>" if reminder['account_name'] else ""}
                </div>
            """
        
        html += """
                <p>You can manage your recurring transactions in your Recaller dashboard.</p>
            </div>
            <div class="footer">
                <p>This is an automated reminder from Recaller. If you no longer wish to receive these notifications, please update your preferences in the app.</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def _generate_reminder_email_text(self, user: User, reminders: List[Dict[str, Any]]) -> str:
        """Generate text email body for reminders."""
        text = f"Hi {getattr(user, 'first_name', None) or 'there'},\n\n"
        text += f"You have {len(reminders)} upcoming recurring transaction(s):\n\n"
        
        for reminder in reminders:
            days_until = reminder["days_until_due"]
            due_text = "Due today" if days_until == 0 else f"Due in {days_until} day(s)"
            
            text += f"• {reminder['description']}\n"
            text += f"  Amount: {reminder['currency']} {reminder['amount']} ({reminder['type'].title()})\n"
            text += f"  {due_text} - {reminder['next_due_date']}\n"
            if reminder['category_name']:
                text += f"  Category: {reminder['category_name']}\n"
            if reminder['account_name']:
                text += f"  Account: {reminder['account_name']}\n"
            text += "\n"
        
        text += "You can manage your recurring transactions in your Recaller dashboard.\n\n"
        text += "This is an automated reminder from Recaller. If you no longer wish to receive these notifications, please update your preferences in the app."
        
        return text
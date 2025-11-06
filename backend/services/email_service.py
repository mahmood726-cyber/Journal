"""
Email service for sending notifications to users.
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'emails'
)

# Initialize Jinja2 environment for templates
template_env = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent.parent / 'templates' / 'emails'))
)


class EmailService:
    """Service for handling email notifications."""

    def __init__(self):
        self.fast_mail = FastMail(conf)

    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send an email using a template.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            template_name: Name of the email template
            context: Context variables for template rendering

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Render template
            template = template_env.get_template(f"{template_name}.html")
            html_content = template.render(**context)

            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype="html"
            )

            # Send email
            await self.fast_mail.send_message(message)
            logger.info(f"Email sent to {recipients}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    # Manuscript-related emails
    async def send_submission_confirmation(self, user_email: str, manuscript_id: str, title: str):
        """Send confirmation email after manuscript submission."""
        return await self.send_email(
            recipients=[user_email],
            subject=f"Submission Confirmation - {manuscript_id}",
            template_name="submission_confirmation",
            context={
                "manuscript_id": manuscript_id,
                "title": title,
                "journal_name": settings.JOURNAL_TITLE,
                "journal_url": str(settings.JOURNAL_URL)
            }
        )

    async def send_editor_new_submission(self, editor_email: str, manuscript_id: str, title: str):
        """Notify editor of new submission."""
        return await self.send_email(
            recipients=[editor_email],
            subject=f"New Submission - {manuscript_id}",
            template_name="editor_new_submission",
            context={
                "manuscript_id": manuscript_id,
                "title": title,
                "journal_name": settings.JOURNAL_TITLE,
                "dashboard_url": f"{settings.JOURNAL_URL}/dashboard"
            }
        )

    # Review-related emails
    async def send_review_invitation(
        self,
        reviewer_email: str,
        reviewer_name: str,
        manuscript_id: str,
        title: str,
        abstract: str,
        due_date: str
    ):
        """Send review invitation to reviewer."""
        return await self.send_email(
            recipients=[reviewer_email],
            subject=f"Invitation to Review - {manuscript_id}",
            template_name="review_invitation",
            context={
                "reviewer_name": reviewer_name,
                "manuscript_id": manuscript_id,
                "title": title,
                "abstract": abstract,
                "due_date": due_date,
                "journal_name": settings.JOURNAL_TITLE,
                "accept_url": f"{settings.JOURNAL_URL}/review/accept",
                "decline_url": f"{settings.JOURNAL_URL}/review/decline"
            }
        )

    async def send_review_reminder(self, reviewer_email: str, reviewer_name: str, manuscript_id: str, due_date: str):
        """Send reminder to reviewer."""
        return await self.send_email(
            recipients=[reviewer_email],
            subject=f"Review Reminder - {manuscript_id}",
            template_name="review_reminder",
            context={
                "reviewer_name": reviewer_name,
                "manuscript_id": manuscript_id,
                "due_date": due_date,
                "journal_name": settings.JOURNAL_TITLE,
                "review_url": f"{settings.JOURNAL_URL}/review/{manuscript_id}"
            }
        )

    async def send_review_complete_notification(
        self,
        reviewer_email: str,
        reviewer_name: str,
        manuscript_id: str
    ):
        """Thank reviewer for completing review."""
        return await self.send_email(
            recipients=[reviewer_email],
            subject=f"Thank You for Your Review - {manuscript_id}",
            template_name="review_complete",
            context={
                "reviewer_name": reviewer_name,
                "manuscript_id": manuscript_id,
                "journal_name": settings.JOURNAL_TITLE
            }
        )

    # Decision emails
    async def send_decision_accept(
        self,
        author_email: str,
        author_name: str,
        manuscript_id: str,
        title: str,
        comments: str
    ):
        """Send acceptance notification to author."""
        return await self.send_email(
            recipients=[author_email],
            subject=f"Manuscript Accepted - {manuscript_id}",
            template_name="decision_accept",
            context={
                "author_name": author_name,
                "manuscript_id": manuscript_id,
                "title": title,
                "comments": comments,
                "journal_name": settings.JOURNAL_TITLE
            }
        )

    async def send_decision_reject(
        self,
        author_email: str,
        author_name: str,
        manuscript_id: str,
        title: str,
        comments: str
    ):
        """Send rejection notification to author."""
        return await self.send_email(
            recipients=[author_email],
            subject=f"Manuscript Decision - {manuscript_id}",
            template_name="decision_reject",
            context={
                "author_name": author_name,
                "manuscript_id": manuscript_id,
                "title": title,
                "comments": comments,
                "journal_name": settings.JOURNAL_TITLE
            }
        )

    async def send_decision_revisions(
        self,
        author_email: str,
        author_name: str,
        manuscript_id: str,
        title: str,
        revision_type: str,
        comments: str,
        due_date: str
    ):
        """Send revisions request to author."""
        return await self.send_email(
            recipients=[author_email],
            subject=f"Revisions Required - {manuscript_id}",
            template_name="decision_revisions",
            context={
                "author_name": author_name,
                "manuscript_id": manuscript_id,
                "title": title,
                "revision_type": revision_type,
                "comments": comments,
                "due_date": due_date,
                "journal_name": settings.JOURNAL_TITLE,
                "submission_url": f"{settings.JOURNAL_URL}/submit/revisions/{manuscript_id}"
            }
        )

    # Publication emails
    async def send_publication_notification(
        self,
        author_email: str,
        author_name: str,
        manuscript_id: str,
        title: str,
        doi: str,
        article_url: str
    ):
        """Notify author that article is published."""
        return await self.send_email(
            recipients=[author_email],
            subject=f"Your Article is Published - {manuscript_id}",
            template_name="publication_notification",
            context={
                "author_name": author_name,
                "manuscript_id": manuscript_id,
                "title": title,
                "doi": doi,
                "article_url": article_url,
                "journal_name": settings.JOURNAL_TITLE
            }
        )

    # General notifications
    async def send_welcome_email(self, user_email: str, user_name: str, role: str):
        """Send welcome email to new user."""
        return await self.send_email(
            recipients=[user_email],
            subject=f"Welcome to {settings.JOURNAL_TITLE}",
            template_name="welcome",
            context={
                "user_name": user_name,
                "role": role,
                "journal_name": settings.JOURNAL_TITLE,
                "dashboard_url": f"{settings.JOURNAL_URL}/dashboard"
            }
        )

    async def send_password_reset(self, user_email: str, user_name: str, reset_token: str):
        """Send password reset email."""
        return await self.send_email(
            recipients=[user_email],
            subject="Password Reset Request",
            template_name="password_reset",
            context={
                "user_name": user_name,
                "reset_url": f"{settings.JOURNAL_URL}/reset-password?token={reset_token}",
                "journal_name": settings.JOURNAL_TITLE
            }
        )


# Create a global instance
email_service = EmailService()

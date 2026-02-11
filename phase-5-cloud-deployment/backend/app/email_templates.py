"""
Email Template System

Provides email template management and rendering.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from string import Template

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template."""

    def __init__(
        self,
        name: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ):
        """Initialize email template."""
        self.name = name
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html

    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Render template with context."""
        subject = Template(self.subject).safe_substitute(context)
        body_text = Template(self.body_text).safe_substitute(context)

        result = {
            "subject": subject,
            "body_text": body_text
        }

        if self.body_html:
            body_html = Template(self.body_html).safe_substitute(context)
            result["body_html"] = body_html

        return result


# Email templates
TODO_REMINDER_TEMPLATE = EmailTemplate(
    name="todo_reminder",
    subject="Reminder: $todo_title",
    body_text="""
Hello $user_name,

This is a reminder about your todo:

Title: $todo_title
Due Date: $due_date
Priority: $priority

View todo: $todo_url

Best regards,
Todo App Team
""",
    body_html="""
<html>
<body>
    <h2>Todo Reminder</h2>
    <p>Hello $user_name,</p>
    <p>This is a reminder about your todo:</p>
    <ul>
        <li><strong>Title:</strong> $todo_title</li>
        <li><strong>Due Date:</strong> $due_date</li>
        <li><strong>Priority:</strong> $priority</li>
    </ul>
    <p><a href="$todo_url">View Todo</a></p>
    <p>Best regards,<br>Todo App Team</p>
</body>
</html>
"""
)

TODO_OVERDUE_TEMPLATE = EmailTemplate(
    name="todo_overdue",
    subject="Overdue: $todo_title",
    body_text="""
Hello $user_name,

Your todo is now overdue:

Title: $todo_title
Due Date: $due_date
Priority: $priority

Please complete it as soon as possible.

View todo: $todo_url

Best regards,
Todo App Team
""",
    body_html="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #d32f2f;">Todo Overdue</h2>
    <p>Hello $user_name,</p>
    <p>Your todo is now overdue:</p>
    <ul>
        <li><strong>Title:</strong> $todo_title</li>
        <li><strong>Due Date:</strong> $due_date</li>
        <li><strong>Priority:</strong> $priority</li>
    </ul>
    <p style="color: #d32f2f;">Please complete it as soon as possible.</p>
    <p><a href="$todo_url" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Todo</a></p>
    <p>Best regards,<br>Todo App Team</p>
</body>
</html>
"""
)

WELCOME_EMAIL_TEMPLATE = EmailTemplate(
    name="welcome_email",
    subject="Welcome to Todo App!",
    body_text="""
Hello $user_name,

Welcome to Todo App! We're excited to have you on board.

Get started by creating your first todo:
$app_url/todos/new

If you have any questions, feel free to contact us.

Best regards,
Todo App Team
""",
    body_html="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h1 style="color: #1976d2;">Welcome to Todo App!</h1>
    <p>Hello $user_name,</p>
    <p>We're excited to have you on board.</p>
    <p>Get started by creating your first todo:</p>
    <p><a href="$app_url/todos/new" style="background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Create Todo</a></p>
    <p>If you have any questions, feel free to contact us.</p>
    <p>Best regards,<br>Todo App Team</p>
</body>
</html>
"""
)

PASSWORD_RESET_TEMPLATE = EmailTemplate(
    name="password_reset",
    subject="Password Reset Request",
    body_text="""
Hello $user_name,

We received a request to reset your password.

Click the link below to reset your password:
$reset_url

This link will expire in $expiry_hours hours.

If you didn't request this, please ignore this email.

Best regards,
Todo App Team
""",
    body_html="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Password Reset Request</h2>
    <p>Hello $user_name,</p>
    <p>We received a request to reset your password.</p>
    <p><a href="$reset_url" style="background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
    <p>This link will expire in $expiry_hours hours.</p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Best regards,<br>Todo App Team</p>
</body>
</html>
"""
)

DAILY_DIGEST_TEMPLATE = EmailTemplate(
    name="daily_digest",
    subject="Your Daily Todo Digest - $date",
    body_text="""
Hello $user_name,

Here's your daily todo digest for $date:

Pending Todos: $pending_count
Completed Today: $completed_count
Overdue: $overdue_count

$todo_list

View all todos: $app_url/todos

Best regards,
Todo App Team
""",
    body_html="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Your Daily Todo Digest</h2>
    <p>Hello $user_name,</p>
    <p>Here's your summary for $date:</p>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>Pending Todos:</strong> $pending_count</p>
        <p><strong>Completed Today:</strong> $completed_count</p>
        <p><strong>Overdue:</strong> $overdue_count</p>
    </div>
    <div>
        $todo_list
    </div>
    <p><a href="$app_url/todos" style="background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View All Todos</a></p>
    <p>Best regards,<br>Todo App Team</p>
</body>
</html>
"""
)


class EmailTemplateManager:
    """Manage email templates."""

    def __init__(self):
        """Initialize template manager."""
        self.templates: Dict[str, EmailTemplate] = {}

    def register(self, template: EmailTemplate):
        """Register template."""
        self.templates[template.name] = template
        logger.info(f"Registered email template: {template.name}")

    def get(self, name: str) -> Optional[EmailTemplate]:
        """Get template by name."""
        return self.templates.get(name)

    def render(self, name: str, context: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Render template."""
        template = self.get(name)
        if not template:
            logger.error(f"Template not found: {name}")
            return None

        return template.render(context)


# Global template manager
email_templates = EmailTemplateManager()

# Register default templates
email_templates.register(TODO_REMINDER_TEMPLATE)
email_templates.register(TODO_OVERDUE_TEMPLATE)
email_templates.register(WELCOME_EMAIL_TEMPLATE)
email_templates.register(PASSWORD_RESET_TEMPLATE)
email_templates.register(DAILY_DIGEST_TEMPLATE)


# Helper functions
def send_todo_reminder(user_name: str, user_email: str, todo_title: str, due_date: str, priority: str, todo_url: str):
    """Send todo reminder email."""
    context = {
        "user_name": user_name,
        "todo_title": todo_title,
        "due_date": due_date,
        "priority": priority,
        "todo_url": todo_url
    }

    email = email_templates.render("todo_reminder", context)
    if email:
        logger.info(f"Sending todo reminder to {user_email}")
        # Send email using email provider
        return email


def send_welcome_email(user_name: str, user_email: str, app_url: str):
    """Send welcome email."""
    context = {
        "user_name": user_name,
        "app_url": app_url
    }

    email = email_templates.render("welcome_email", context)
    if email:
        logger.info(f"Sending welcome email to {user_email}")
        # Send email using email provider
        return email


def send_password_reset(user_name: str, user_email: str, reset_url: str, expiry_hours: int = 24):
    """Send password reset email."""
    context = {
        "user_name": user_name,
        "reset_url": reset_url,
        "expiry_hours": expiry_hours
    }

    email = email_templates.render("password_reset", context)
    if email:
        logger.info(f"Sending password reset to {user_email}")
        # Send email using email provider
        return email

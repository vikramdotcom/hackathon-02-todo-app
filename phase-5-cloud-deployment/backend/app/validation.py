"""
Input Validation and Sanitization

Comprehensive input validation and sanitization utilities.
"""

import re
import logging
from typing import Any, Optional, List, Dict
from datetime import datetime, date
import html

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation error exception."""

    def __init__(self, field: str, message: str):
        """Initialize validation error."""
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class Validator:
    """Input validator."""

    @staticmethod
    def required(value: Any, field: str = "field") -> Any:
        """Validate required field."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(field, "This field is required")
        return value

    @staticmethod
    def string(value: Any, field: str = "field", min_length: int = 0, max_length: int = 10000) -> str:
        """Validate string."""
        if not isinstance(value, str):
            raise ValidationError(field, "Must be a string")

        if len(value) < min_length:
            raise ValidationError(field, f"Must be at least {min_length} characters")

        if len(value) > max_length:
            raise ValidationError(field, f"Must be at most {max_length} characters")

        return value

    @staticmethod
    def integer(value: Any, field: str = "field", min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """Validate integer."""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(field, "Must be an integer")

        if min_value is not None and int_value < min_value:
            raise ValidationError(field, f"Must be at least {min_value}")

        if max_value is not None and int_value > max_value:
            raise ValidationError(field, f"Must be at most {max_value}")

        return int_value

    @staticmethod
    def float_value(value: Any, field: str = "field", min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
        """Validate float."""
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(field, "Must be a number")

        if min_value is not None and float_value < min_value:
            raise ValidationError(field, f"Must be at least {min_value}")

        if max_value is not None and float_value > max_value:
            raise ValidationError(field, f"Must be at most {max_value}")

        return float_value

    @staticmethod
    def boolean(value: Any, field: str = "field") -> bool:
        """Validate boolean."""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            if value.lower() in ["true", "1", "yes"]:
                return True
            elif value.lower() in ["false", "0", "no"]:
                return False

        raise ValidationError(field, "Must be a boolean")

    @staticmethod
    def email(value: str, field: str = "email") -> str:
        """Validate email address."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, value):
            raise ValidationError(field, "Invalid email address")

        return value.lower()

    @staticmethod
    def url(value: str, field: str = "url") -> str:
        """Validate URL."""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'

        if not re.match(pattern, value):
            raise ValidationError(field, "Invalid URL")

        return value

    @staticmethod
    def date_value(value: Any, field: str = "date") -> date:
        """Validate date."""
        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                pass

        raise ValidationError(field, "Invalid date format (use ISO format)")

    @staticmethod
    def datetime_value(value: Any, field: str = "datetime") -> datetime:
        """Validate datetime."""
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass

        raise ValidationError(field, "Invalid datetime format (use ISO format)")

    @staticmethod
    def choice(value: Any, choices: List[Any], field: str = "field") -> Any:
        """Validate choice from list."""
        if value not in choices:
            raise ValidationError(field, f"Must be one of: {', '.join(map(str, choices))}")

        return value

    @staticmethod
    def list_value(value: Any, field: str = "field", min_length: int = 0, max_length: int = 1000) -> List:
        """Validate list."""
        if not isinstance(value, list):
            raise ValidationError(field, "Must be a list")

        if len(value) < min_length:
            raise ValidationError(field, f"Must have at least {min_length} items")

        if len(value) > max_length:
            raise ValidationError(field, f"Must have at most {max_length} items")

        return value

    @staticmethod
    def dict_value(value: Any, field: str = "field") -> Dict:
        """Validate dictionary."""
        if not isinstance(value, dict):
            raise ValidationError(field, "Must be a dictionary")

        return value

    @staticmethod
    def regex(value: str, pattern: str, field: str = "field", message: str = "Invalid format") -> str:
        """Validate against regex pattern."""
        if not re.match(pattern, value):
            raise ValidationError(field, message)

        return value

    @staticmethod
    def uuid(value: str, field: str = "uuid") -> str:
        """Validate UUID."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

        if not re.match(pattern, value.lower()):
            raise ValidationError(field, "Invalid UUID format")

        return value.lower()


class Sanitizer:
    """Input sanitizer."""

    @staticmethod
    def html(value: str) -> str:
        """Sanitize HTML."""
        return html.escape(value)

    @staticmethod
    def sql(value: str) -> str:
        """Sanitize SQL (basic)."""
        # Remove common SQL injection patterns
        dangerous = ["--", ";", "/*", "*/", "xp_", "sp_", "exec", "execute"]

        sanitized = value
        for pattern in dangerous:
            sanitized = sanitized.replace(pattern, "")

        return sanitized

    @staticmethod
    def filename(value: str) -> str:
        """Sanitize filename."""
        # Remove path traversal attempts
        sanitized = value.replace("..", "").replace("/", "").replace("\\", "")

        # Remove special characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', sanitized)

        return sanitized

    @staticmethod
    def strip_tags(value: str) -> str:
        """Strip HTML tags."""
        return re.sub(r'<[^>]+>', '', value)

    @staticmethod
    def normalize_whitespace(value: str) -> str:
        """Normalize whitespace."""
        return ' '.join(value.split())

    @staticmethod
    def truncate(value: str, max_length: int = 255, suffix: str = "...") -> str:
        """Truncate string."""
        if len(value) <= max_length:
            return value

        return value[:max_length - len(suffix)] + suffix


class SchemaValidator:
    """Validate data against schema."""

    @staticmethod
    def validate(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema: Validation schema

        Returns:
            Validated data

        Raises:
            ValidationError: If validation fails
        """
        validated = {}

        for field, rules in schema.items():
            value = data.get(field)

            # Check required
            if rules.get("required", False):
                Validator.required(value, field)

            # Skip validation if value is None and not required
            if value is None:
                if "default" in rules:
                    validated[field] = rules["default"]
                continue

            # Type validation
            field_type = rules.get("type")

            if field_type == "string":
                value = Validator.string(
                    value,
                    field,
                    min_length=rules.get("min_length", 0),
                    max_length=rules.get("max_length", 10000)
                )

            elif field_type == "integer":
                value = Validator.integer(
                    value,
                    field,
                    min_value=rules.get("min_value"),
                    max_value=rules.get("max_value")
                )

            elif field_type == "float":
                value = Validator.float_value(
                    value,
                    field,
                    min_value=rules.get("min_value"),
                    max_value=rules.get("max_value")
                )

            elif field_type == "boolean":
                value = Validator.boolean(value, field)

            elif field_type == "email":
                value = Validator.email(value, field)

            elif field_type == "url":
                value = Validator.url(value, field)

            elif field_type == "date":
                value = Validator.date_value(value, field)

            elif field_type == "datetime":
                value = Validator.datetime_value(value, field)

            elif field_type == "list":
                value = Validator.list_value(
                    value,
                    field,
                    min_length=rules.get("min_length", 0),
                    max_length=rules.get("max_length", 1000)
                )

            elif field_type == "dict":
                value = Validator.dict_value(value, field)

            # Choice validation
            if "choices" in rules:
                value = Validator.choice(value, rules["choices"], field)

            # Regex validation
            if "pattern" in rules:
                value = Validator.regex(
                    value,
                    rules["pattern"],
                    field,
                    rules.get("pattern_message", "Invalid format")
                )

            # Sanitization
            if rules.get("sanitize_html"):
                value = Sanitizer.html(value)

            if rules.get("strip_tags"):
                value = Sanitizer.strip_tags(value)

            if rules.get("normalize_whitespace"):
                value = Sanitizer.normalize_whitespace(value)

            validated[field] = value

        return validated


# Example schemas
TODO_CREATE_SCHEMA = {
    "title": {
        "type": "string",
        "required": True,
        "min_length": 1,
        "max_length": 200,
        "normalize_whitespace": True
    },
    "description": {
        "type": "string",
        "required": False,
        "max_length": 2000,
        "strip_tags": True
    },
    "priority": {
        "type": "string",
        "required": False,
        "choices": ["low", "medium", "high", "urgent"],
        "default": "medium"
    },
    "due_date": {
        "type": "datetime",
        "required": False
    },
    "tags": {
        "type": "list",
        "required": False,
        "max_length": 10
    }
}

USER_REGISTRATION_SCHEMA = {
    "email": {
        "type": "email",
        "required": True
    },
    "password": {
        "type": "string",
        "required": True,
        "min_length": 8,
        "max_length": 128
    },
    "name": {
        "type": "string",
        "required": True,
        "min_length": 1,
        "max_length": 100,
        "normalize_whitespace": True
    }
}

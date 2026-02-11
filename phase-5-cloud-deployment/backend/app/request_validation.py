"""
Request Validation System

Comprehensive request validation with schema support.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationRule:
    """Validation rule."""

    def __init__(self, field: str, rule_type: str, params: Optional[Dict[str, Any]] = None):
        """Initialize validation rule."""
        self.field = field
        self.rule_type = rule_type
        self.params = params or {}

    def validate(self, value: Any) -> bool:
        """Validate value against rule."""
        if self.rule_type == "required":
            return value is not None
        elif self.rule_type == "min_length":
            return len(str(value)) >= self.params.get("length", 0)
        elif self.rule_type == "max_length":
            return len(str(value)) <= self.params.get("length", 100)
        elif self.rule_type == "pattern":
            import re
            return bool(re.match(self.params.get("pattern", ".*"), str(value)))
        return True


class RequestValidator:
    """Validate incoming requests."""

    def __init__(self):
        """Initialize request validator."""
        self.schemas: Dict[str, List[ValidationRule]] = {}

    def register_schema(self, schema_name: str, rules: List[ValidationRule]):
        """Register validation schema."""
        self.schemas[schema_name] = rules

    def validate(self, schema_name: str, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against schema."""
        if schema_name not in self.schemas:
            return True, []

        errors = []
        for rule in self.schemas[schema_name]:
            value = data.get(rule.field)
            if not rule.validate(value):
                errors.append(f"Validation failed for {rule.field}: {rule.rule_type}")

        return len(errors) == 0, errors


request_validator = RequestValidator()

"""
Request/Response Serialization Utilities

Provides utilities for serializing and deserializing API requests and responses.
"""

import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class EnhancedJSONEncoder(json.JSONEncoder):
    """Enhanced JSON encoder with support for additional types."""

    def default(self, obj: Any) -> Any:
        """
        Encode object to JSON-serializable format.

        Args:
            obj: Object to encode

        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, date):
            return obj.isoformat()

        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, BaseModel):
            return obj.model_dump()

        if hasattr(obj, '__dict__'):
            return obj.__dict__

        return super().default(obj)


class Serializer:
    """Serialize and deserialize data."""

    @staticmethod
    def to_json(data: Any, pretty: bool = False) -> str:
        """
        Serialize data to JSON string.

        Args:
            data: Data to serialize
            pretty: Pretty print JSON

        Returns:
            JSON string
        """
        indent = 2 if pretty else None

        return json.dumps(
            data,
            cls=EnhancedJSONEncoder,
            indent=indent,
            ensure_ascii=False
        )

    @staticmethod
    def from_json(json_str: str, model: Optional[Type[T]] = None) -> Any:
        """
        Deserialize JSON string to data.

        Args:
            json_str: JSON string
            model: Optional Pydantic model to parse into

        Returns:
            Deserialized data
        """
        data = json.loads(json_str)

        if model is not None:
            return model.model_validate(data)

        return data

    @staticmethod
    def to_dict(obj: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert Pydantic model to dictionary.

        Args:
            obj: Pydantic model instance
            exclude_none: Exclude None values

        Returns:
            Dictionary representation
        """
        return obj.model_dump(exclude_none=exclude_none)

    @staticmethod
    def from_dict(data: Dict[str, Any], model: Type[T]) -> T:
        """
        Create Pydantic model from dictionary.

        Args:
            data: Dictionary data
            model: Pydantic model class

        Returns:
            Model instance
        """
        return model.model_validate(data)

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """
        Convert snake_case to camelCase.

        Args:
            snake_str: Snake case string

        Returns:
            Camel case string
        """
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """
        Convert camelCase to snake_case.

        Args:
            camel_str: Camel case string

        Returns:
            Snake case string
        """
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

    @staticmethod
    def dict_to_camel_case(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert dictionary keys from snake_case to camelCase.

        Args:
            data: Dictionary with snake_case keys

        Returns:
            Dictionary with camelCase keys
        """
        result = {}

        for key, value in data.items():
            camel_key = Serializer.to_camel_case(key)

            if isinstance(value, dict):
                result[camel_key] = Serializer.dict_to_camel_case(value)
            elif isinstance(value, list):
                result[camel_key] = [
                    Serializer.dict_to_camel_case(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[camel_key] = value

        return result

    @staticmethod
    def dict_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert dictionary keys from camelCase to snake_case.

        Args:
            data: Dictionary with camelCase keys

        Returns:
            Dictionary with snake_case keys
        """
        result = {}

        for key, value in data.items():
            snake_key = Serializer.to_snake_case(key)

            if isinstance(value, dict):
                result[snake_key] = Serializer.dict_to_snake_case(value)
            elif isinstance(value, list):
                result[snake_key] = [
                    Serializer.dict_to_snake_case(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[snake_key] = value

        return result


class ResponseFormatter:
    """Format API responses consistently."""

    @staticmethod
    def success(
        data: Any,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format success response.

        Args:
            data: Response data
            message: Optional success message
            metadata: Optional metadata

        Returns:
            Formatted response
        """
        response = {
            "success": True,
            "data": data
        }

        if message:
            response["message"] = message

        if metadata:
            response["metadata"] = metadata

        return response

    @staticmethod
    def error(
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """
        Format error response.

        Args:
            error_type: Error type identifier
            message: Error message
            details: Optional error details
            status_code: HTTP status code

        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code
            }
        }

        if details:
            response["error"]["details"] = details

        return response

    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format paginated response.

        Args:
            items: List of items
            total: Total number of items
            page: Current page number
            page_size: Items per page
            metadata: Optional metadata

        Returns:
            Formatted paginated response
        """
        total_pages = (total + page_size - 1) // page_size

        response = {
            "success": True,
            "data": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }

        if metadata:
            response["metadata"] = metadata

        return response


class RequestParser:
    """Parse and validate API requests."""

    @staticmethod
    def parse_query_params(
        params: Dict[str, Any],
        allowed_params: List[str]
    ) -> Dict[str, Any]:
        """
        Parse and filter query parameters.

        Args:
            params: Query parameters
            allowed_params: List of allowed parameter names

        Returns:
            Filtered parameters
        """
        return {
            key: value
            for key, value in params.items()
            if key in allowed_params and value is not None
        }

    @staticmethod
    def parse_pagination(
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        default_page: int = 1,
        default_page_size: int = 20,
        max_page_size: int = 100
    ) -> tuple[int, int]:
        """
        Parse pagination parameters.

        Args:
            page: Page number
            page_size: Items per page
            default_page: Default page number
            default_page_size: Default page size
            max_page_size: Maximum page size

        Returns:
            Tuple of (page, page_size)
        """
        page = max(page or default_page, 1)
        page_size = min(
            max(page_size or default_page_size, 1),
            max_page_size
        )

        return page, page_size

    @staticmethod
    def parse_sort(
        sort: Optional[str],
        allowed_fields: List[str],
        default_field: str = "created_at",
        default_order: str = "desc"
    ) -> tuple[str, str]:
        """
        Parse sort parameter.

        Args:
            sort: Sort string (e.g., "created_at:desc")
            allowed_fields: List of allowed sort fields
            default_field: Default sort field
            default_order: Default sort order

        Returns:
            Tuple of (field, order)
        """
        if not sort:
            return default_field, default_order

        parts = sort.split(":")
        field = parts[0] if parts[0] in allowed_fields else default_field
        order = parts[1] if len(parts) > 1 and parts[1] in ["asc", "desc"] else default_order

        return field, order

"""
Error Handling Utilities

Provides custom exceptions and error handling utilities.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class TodoNotFoundError(Exception):
    """Exception raised when a todo is not found."""

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        self.message = f"Todo with id {todo_id} not found"
        super().__init__(self.message)


class RecurrencePatternNotFoundError(Exception):
    """Exception raised when a recurrence pattern is not found."""

    def __init__(self, pattern_id: int):
        self.pattern_id = pattern_id
        self.message = f"Recurrence pattern with id {pattern_id} not found"
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """Exception raised when user is not authorized."""

    def __init__(self, message: str = "Unauthorized access"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class DatabaseError(Exception):
    """Exception raised when database operation fails."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        self.message = message
        super().__init__(f"Database {operation} failed: {message}")


class RateLimitExceededError(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        self.message = f"Rate limit exceeded. Retry after {retry_after} seconds"
        super().__init__(self.message)


class ErrorResponse:
    """Utility class for creating error responses."""

    @staticmethod
    def not_found(
        resource: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 404 Not Found error response.

        Args:
            resource: Resource type (e.g., "todo", "user")
            resource_id: Optional resource ID
            details: Optional additional details

        Returns:
            HTTPException with 404 status
        """
        message = f"{resource.capitalize()} not found"
        if resource_id:
            message = f"{resource.capitalize()} with id {resource_id} not found"

        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_found",
                "message": message,
                "details": details or {}
            }
        )

    @staticmethod
    def bad_request(
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 400 Bad Request error response.

        Args:
            message: Error message
            field: Optional field name that caused the error
            details: Optional additional details

        Returns:
            HTTPException with 400 status
        """
        error_details = details or {}
        if field:
            error_details["field"] = field

        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "bad_request",
                "message": message,
                "details": error_details
            }
        )

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access",
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 401 Unauthorized error response.

        Args:
            message: Error message
            details: Optional additional details

        Returns:
            HTTPException with 401 status
        """
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "unauthorized",
                "message": message,
                "details": details or {}
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 403 Forbidden error response.

        Args:
            message: Error message
            details: Optional additional details

        Returns:
            HTTPException with 403 status
        """
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "forbidden",
                "message": message,
                "details": details or {}
            }
        )

    @staticmethod
    def conflict(
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 409 Conflict error response.

        Args:
            message: Error message
            details: Optional additional details

        Returns:
            HTTPException with 409 status
        """
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "conflict",
                "message": message,
                "details": details or {}
            }
        )

    @staticmethod
    def rate_limit_exceeded(
        retry_after: int,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 429 Too Many Requests error response.

        Args:
            retry_after: Seconds to wait before retrying
            details: Optional additional details

        Returns:
            HTTPException with 429 status
        """
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Retry after {retry_after} seconds",
                "details": details or {}
            },
            headers={"Retry-After": str(retry_after)}
        )

    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 500 Internal Server Error response.

        Args:
            message: Error message
            details: Optional additional details

        Returns:
            HTTPException with 500 status
        """
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_server_error",
                "message": message,
                "details": details or {}
            }
        )

"""
API Middleware for Phase V Backend

Provides request/response middleware for logging, timing, and error handling.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging_config import RequestLogger
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with timing information.

    Adds request_id to each request and logs request/response details.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Record start time
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "duration_ms": duration_ms,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log request
        RequestLogger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id
        )

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add timing information to response headers.

    Useful for performance monitoring and debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add timing headers to response."""
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle unhandled exceptions.

    Provides consistent error responses and logging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and return consistent error responses."""
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                exc_info=True
            )

            # Return generic error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )

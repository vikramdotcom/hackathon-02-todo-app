"""
Request/Response Logging Middleware

Comprehensive logging for HTTP requests and responses.
"""

import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class RequestLogger:
    """Log HTTP requests and responses."""

    def __init__(self):
        """Initialize request logger."""
        self.logs: list[Dict[str, Any]] = []

    def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        query_params: Dict[str, Any],
        headers: Dict[str, str],
        body: Optional[Any] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log incoming request."""
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "request",
            "method": method,
            "path": path,
            "query_params": query_params,
            "headers": self._sanitize_headers(headers),
            "body": self._sanitize_body(body),
            "user_id": user_id,
            "ip_address": ip_address
        }

        self.logs.append(log_entry)

        logger.info(
            f"{method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "user_id": user_id
            }
        )

    def log_response(
        self,
        request_id: str,
        status_code: int,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        duration_ms: float = 0
    ):
        """Log outgoing response."""
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "response",
            "status_code": status_code,
            "headers": self._sanitize_headers(headers),
            "body": self._sanitize_body(body),
            "duration_ms": duration_ms
        }

        self.logs.append(log_entry)

        logger.info(
            f"Response {status_code}",
            extra={
                "request_id": request_id,
                "status_code": status_code,
                "duration_ms": duration_ms
            }
        )

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive headers."""
        sensitive = ["authorization", "cookie", "x-api-key"]
        sanitized = {}

        for key, value in headers.items():
            if key.lower() in sensitive:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_body(self, body: Any) -> Any:
        """Sanitize sensitive body fields."""
        if not body:
            return None

        if isinstance(body, dict):
            sensitive = ["password", "token", "secret", "api_key"]
            sanitized = body.copy()

            for field in sensitive:
                if field in sanitized:
                    sanitized[field] = "***REDACTED***"

            return sanitized

        return str(body)[:1000]  # Truncate large bodies

    def get_logs(
        self,
        request_id: Optional[str] = None,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Get request logs."""
        logs = self.logs

        if request_id:
            logs = [log for log in logs if log["request_id"] == request_id]

        return logs[-limit:]

    def export_logs(self, format: str = "json") -> str:
        """Export logs."""
        if format == "json":
            return json.dumps(self.logs, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


class RequestTracker:
    """Track request metrics."""

    def __init__(self):
        """Initialize request tracker."""
        self.requests: Dict[str, Dict[str, Any]] = {}

    def start_request(self, request_id: str, method: str, path: str):
        """Start tracking request."""
        self.requests[request_id] = {
            "method": method,
            "path": path,
            "start_time": time.time(),
            "end_time": None,
            "duration_ms": None,
            "status_code": None
        }

    def end_request(self, request_id: str, status_code: int):
        """End tracking request."""
        if request_id in self.requests:
            request = self.requests[request_id]
            request["end_time"] = time.time()
            request["duration_ms"] = (request["end_time"] - request["start_time"]) * 1000
            request["status_code"] = status_code

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get request info."""
        return self.requests.get(request_id)

    def get_slow_requests(self, threshold_ms: float = 1000) -> list[Dict[str, Any]]:
        """Get slow requests."""
        slow = []

        for request_id, request in self.requests.items():
            if request["duration_ms"] and request["duration_ms"] > threshold_ms:
                slow.append({
                    "request_id": request_id,
                    **request
                })

        return sorted(slow, key=lambda x: x["duration_ms"], reverse=True)

    def get_error_requests(self) -> list[Dict[str, Any]]:
        """Get error requests."""
        errors = []

        for request_id, request in self.requests.items():
            if request["status_code"] and request["status_code"] >= 400:
                errors.append({
                    "request_id": request_id,
                    **request
                })

        return errors


class AccessLogger:
    """Log API access patterns."""

    def __init__(self):
        """Initialize access logger."""
        self.access_log: list[Dict[str, Any]] = []

    def log_access(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        timestamp: Optional[datetime] = None
    ):
        """Log API access."""
        entry = {
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        }

        self.access_log.append(entry)

    def get_user_activity(self, user_id: int) -> list[Dict[str, Any]]:
        """Get user activity."""
        return [
            entry for entry in self.access_log
            if entry["user_id"] == user_id
        ]

    def get_endpoint_usage(self, endpoint: str) -> int:
        """Get endpoint usage count."""
        return len([
            entry for entry in self.access_log
            if entry["endpoint"] == endpoint
        ])

    def get_popular_endpoints(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get most popular endpoints."""
        endpoint_counts: Dict[str, int] = {}

        for entry in self.access_log:
            endpoint = entry["endpoint"]
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1

        popular = [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in endpoint_counts.items()
        ]

        return sorted(popular, key=lambda x: x["count"], reverse=True)[:limit]


# Global instances
request_logger = RequestLogger()
request_tracker = RequestTracker()
access_logger = AccessLogger()


# Middleware helper
class LoggingMiddleware:
    """Logging middleware for FastAPI."""

    def __init__(self, app):
        """Initialize middleware."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process request with logging."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Extract request info
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()

        # Start tracking
        request_tracker.start_request(request_id, method, path)

        # Log request
        request_logger.log_request(
            request_id=request_id,
            method=method,
            path=path,
            query_params=dict(scope.get("query_string", {})),
            headers=dict(scope.get("headers", [])),
            user_id=scope.get("user_id"),
            ip_address=scope.get("client", [""])[0] if scope.get("client") else None
        )

        # Process request
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration_ms = (time.time() - start_time) * 1000

                # End tracking
                request_tracker.end_request(request_id, status_code)

                # Log response
                request_logger.log_response(
                    request_id=request_id,
                    status_code=status_code,
                    headers=dict(message.get("headers", [])),
                    duration_ms=duration_ms
                )

            await send(message)

        await self.app(scope, receive, send_wrapper)


# Example usage
def log_api_request(method: str, path: str, user_id: int, status_code: int, duration_ms: float):
    """Log API request."""
    request_id = str(uuid.uuid4())

    request_logger.log_request(
        request_id=request_id,
        method=method,
        path=path,
        query_params={},
        headers={},
        user_id=user_id
    )

    request_logger.log_response(
        request_id=request_id,
        status_code=status_code,
        headers={},
        duration_ms=duration_ms
    )

    access_logger.log_access(
        user_id=user_id,
        endpoint=path,
        method=method
    )

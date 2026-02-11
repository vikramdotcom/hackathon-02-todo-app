"""
API Gateway and Routing

Handle API gateway functionality with routing and middleware.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class Route:
    """API route definition."""

    def __init__(
        self,
        path: str,
        method: HTTPMethod,
        handler: Callable,
        middleware: Optional[List[Callable]] = None
    ):
        """Initialize route."""
        self.path = path
        self.method = method
        self.handler = handler
        self.middleware = middleware or []
        self.pattern = self._compile_pattern(path)

    def _compile_pattern(self, path: str) -> re.Pattern:
        """Compile path pattern for matching."""
        # Convert path parameters to regex
        pattern = path
        pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', pattern)
        pattern = f"^{pattern}$"
        return re.compile(pattern)

    def matches(self, path: str, method: str) -> Optional[Dict[str, str]]:
        """Check if route matches path and method."""
        if self.method.value != method:
            return None

        match = self.pattern.match(path)
        if match:
            return match.groupdict()

        return None


class Router:
    """API router."""

    def __init__(self):
        """Initialize router."""
        self.routes: List[Route] = []
        self.global_middleware: List[Callable] = []

    def add_route(
        self,
        path: str,
        method: HTTPMethod,
        handler: Callable,
        middleware: Optional[List[Callable]] = None
    ):
        """Add route."""
        route = Route(path, method, handler, middleware)
        self.routes.append(route)

        logger.info(f"Registered route: {method.value} {path}")

    def add_middleware(self, middleware: Callable):
        """Add global middleware."""
        self.global_middleware.append(middleware)

    def match_route(self, path: str, method: str) -> Optional[tuple[Route, Dict[str, str]]]:
        """Match route for path and method."""
        for route in self.routes:
            params = route.matches(path, method)
            if params is not None:
                return route, params

        return None

    def get(self, path: str, middleware: Optional[List[Callable]] = None):
        """Decorator for GET routes."""
        def decorator(handler: Callable):
            self.add_route(path, HTTPMethod.GET, handler, middleware)
            return handler
        return decorator

    def post(self, path: str, middleware: Optional[List[Callable]] = None):
        """Decorator for POST routes."""
        def decorator(handler: Callable):
            self.add_route(path, HTTPMethod.POST, handler, middleware)
            return handler
        return decorator

    def put(self, path: str, middleware: Optional[List[Callable]] = None):
        """Decorator for PUT routes."""
        def decorator(handler: Callable):
            self.add_route(path, HTTPMethod.PUT, handler, middleware)
            return handler
        return decorator

    def delete(self, path: str, middleware: Optional[List[Callable]] = None):
        """Decorator for DELETE routes."""
        def decorator(handler: Callable):
            self.add_route(path, HTTPMethod.DELETE, handler, middleware)
            return handler
        return decorator


class APIGateway:
    """API Gateway for routing and middleware."""

    def __init__(self):
        """Initialize API gateway."""
        self.routers: Dict[str, Router] = {}
        self.global_middleware: List[Callable] = []

    def create_router(self, prefix: str = "") -> Router:
        """Create router with prefix."""
        router = Router()
        self.routers[prefix] = router
        return router

    def add_middleware(self, middleware: Callable):
        """Add global middleware."""
        self.global_middleware.append(middleware)

    async def handle_request(self, request) -> Any:
        """Handle incoming request."""
        path = request.path
        method = request.method

        # Find matching route
        for prefix, router in self.routers.items():
            if path.startswith(prefix):
                route_path = path[len(prefix):]
                match = router.match_route(route_path, method)

                if match:
                    route, params = match

                    # Execute middleware chain
                    for middleware in self.global_middleware:
                        await middleware(request)

                    for middleware in router.global_middleware:
                        await middleware(request)

                    for middleware in route.middleware:
                        await middleware(request)

                    # Execute handler
                    return await route.handler(request, **params)

        # No route found
        return {"error": "Not found"}, 404


class RateLimitMiddleware:
    """Rate limiting middleware."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limit middleware."""
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, List[datetime]] = {}

    async def __call__(self, request):
        """Apply rate limiting."""
        client_id = self._get_client_id(request)

        # Clean old requests
        now = datetime.utcnow()
        if client_id in self.request_counts:
            self.request_counts[client_id] = [
                ts for ts in self.request_counts[client_id]
                if (now - ts).total_seconds() < 60
            ]

        # Check rate limit
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []

        if len(self.request_counts[client_id]) >= self.requests_per_minute:
            raise Exception("Rate limit exceeded")

        # Record request
        self.request_counts[client_id].append(now)

    def _get_client_id(self, request) -> str:
        """Get client identifier."""
        # Try to get from header
        client_id = request.headers.get("X-Client-ID")
        if client_id:
            return client_id

        # Fall back to IP
        return request.client.host if hasattr(request, "client") else "unknown"


class CORSMiddleware:
    """CORS middleware."""

    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        allow_methods: List[str] = ["*"],
        allow_headers: List[str] = ["*"]
    ):
        """Initialize CORS middleware."""
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers

    async def __call__(self, request):
        """Apply CORS headers."""
        # Add CORS headers to response
        # In production, this would modify the response object
        pass


class AuthMiddleware:
    """Authentication middleware."""

    def __init__(self, auth_service):
        """Initialize auth middleware."""
        self.auth_service = auth_service

    async def __call__(self, request):
        """Verify authentication."""
        # Get token from header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise Exception("Missing authorization header")

        if not auth_header.startswith("Bearer "):
            raise Exception("Invalid authorization header")

        token = auth_header[7:]

        # Verify token
        user = await self.auth_service.verify_token(token)

        if not user:
            raise Exception("Invalid token")

        # Attach user to request
        request.user = user


class LoggingMiddleware:
    """Request logging middleware."""

    async def __call__(self, request):
        """Log request."""
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "client": request.client.host if hasattr(request, "client") else None
            }
        )


class RequestIDMiddleware:
    """Add request ID to requests."""

    async def __call__(self, request):
        """Add request ID."""
        import uuid
        request.request_id = str(uuid.uuid4())


class LoadBalancer:
    """Simple load balancer."""

    def __init__(self, backends: List[str]):
        """Initialize load balancer."""
        self.backends = backends
        self.current_index = 0

    def get_next_backend(self) -> str:
        """Get next backend (round-robin)."""
        backend = self.backends[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.backends)
        return backend


class CircuitBreaker:
    """Circuit breaker for API calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60
    ):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker."""
        if self.state == "open":
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout_seconds:
                    self.state = "half-open"
                else:
                    raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)

            # Reset on success
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise e


class APIVersioning:
    """Handle API versioning."""

    def __init__(self, default_version: str = "v1"):
        """Initialize API versioning."""
        self.default_version = default_version
        self.version_routers: Dict[str, Router] = {}

    def get_version_from_request(self, request) -> str:
        """Extract API version from request."""
        # Try header
        version = request.headers.get("X-API-Version")
        if version:
            return version

        # Try path
        path = request.path
        if path.startswith("/v"):
            parts = path.split("/")
            if len(parts) > 1:
                return parts[1]

        return self.default_version

    def register_version(self, version: str, router: Router):
        """Register router for version."""
        self.version_routers[version] = router


class RequestValidator:
    """Validate incoming requests."""

    def __init__(self, schema: Dict[str, Any]):
        """Initialize request validator."""
        self.schema = schema

    async def __call__(self, request):
        """Validate request."""
        # Validate request body against schema
        # In production, use proper validation library
        pass


class ResponseTransformer:
    """Transform API responses."""

    def __init__(self):
        """Initialize response transformer."""
        pass

    def transform(self, data: Any, format: str = "json") -> Any:
        """Transform response data."""
        if format == "json":
            return data
        elif format == "xml":
            # Convert to XML
            return data
        else:
            return data


# Global instances
api_gateway = APIGateway()
main_router = api_gateway.create_router()
rate_limit_middleware = RateLimitMiddleware()
cors_middleware = CORSMiddleware()
logging_middleware = LoggingMiddleware()
request_id_middleware = RequestIDMiddleware()


# Helper functions
def create_router(prefix: str = "") -> Router:
    """Create new router."""
    return api_gateway.create_router(prefix)


def add_global_middleware(middleware: Callable):
    """Add global middleware."""
    api_gateway.add_middleware(middleware)


# Example usage
@main_router.get("/health")
async def health_check(request):
    """Health check endpoint."""
    return {"status": "healthy"}


@main_router.get("/todos/{todo_id}")
async def get_todo(request, todo_id: str):
    """Get todo by ID."""
    return {"todo_id": todo_id}

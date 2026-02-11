"""
API Documentation Generator

Automatically generates API documentation from code.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class EndpointDoc:
    """API endpoint documentation."""

    def __init__(
        self,
        method: str,
        path: str,
        summary: str,
        description: str = "",
        parameters: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        responses: Optional[Dict[int, Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None
    ):
        """Initialize endpoint documentation."""
        self.method = method
        self.path = path
        self.summary = summary
        self.description = description
        self.parameters = parameters or []
        self.request_body = request_body
        self.responses = responses or {}
        self.tags = tags or []

    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI format."""
        spec = {
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags
        }

        if self.parameters:
            spec["parameters"] = self.parameters

        if self.request_body:
            spec["requestBody"] = self.request_body

        if self.responses:
            spec["responses"] = self.responses

        return spec


class APIDocGenerator:
    """Generate API documentation."""

    def __init__(self, title: str, version: str, description: str = ""):
        """Initialize doc generator."""
        self.title = title
        self.version = version
        self.description = description
        self.endpoints: Dict[str, Dict[str, EndpointDoc]] = {}

    def add_endpoint(self, endpoint: EndpointDoc):
        """Add endpoint documentation."""
        if endpoint.path not in self.endpoints:
            self.endpoints[endpoint.path] = {}

        self.endpoints[endpoint.path][endpoint.method.lower()] = endpoint

    def generate_openapi(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "paths": {}
        }

        for path, methods in self.endpoints.items():
            spec["paths"][path] = {}
            for method, endpoint in methods.items():
                spec["paths"][path][method] = endpoint.to_openapi()

        return spec

    def generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        lines = [
            f"# {self.title}",
            "",
            f"Version: {self.version}",
            "",
            self.description,
            "",
            "## Endpoints",
            ""
        ]

        for path, methods in sorted(self.endpoints.items()):
            for method, endpoint in methods.items():
                lines.extend([
                    f"### {method.upper()} {path}",
                    "",
                    endpoint.summary,
                    "",
                    endpoint.description,
                    ""
                ])

                if endpoint.parameters:
                    lines.append("**Parameters:**")
                    lines.append("")
                    for param in endpoint.parameters:
                        lines.append(f"- `{param['name']}` ({param.get('in', 'query')}): {param.get('description', '')}")
                    lines.append("")

                if endpoint.request_body:
                    lines.append("**Request Body:**")
                    lines.append("")
                    lines.append("```json")
                    lines.append(json.dumps(endpoint.request_body.get("example", {}), indent=2))
                    lines.append("```")
                    lines.append("")

                if endpoint.responses:
                    lines.append("**Responses:**")
                    lines.append("")
                    for status, response in endpoint.responses.items():
                        lines.append(f"- {status}: {response.get('description', '')}")
                    lines.append("")

        return "\n".join(lines)


# Example endpoint documentation
TODO_LIST_DOC = EndpointDoc(
    method="GET",
    path="/api/v2/todos",
    summary="List todos",
    description="Retrieve a list of todos with optional filtering",
    parameters=[
        {
            "name": "completed",
            "in": "query",
            "description": "Filter by completion status",
            "schema": {"type": "boolean"}
        },
        {
            "name": "priority",
            "in": "query",
            "description": "Filter by priority",
            "schema": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
        },
        {
            "name": "limit",
            "in": "query",
            "description": "Maximum results",
            "schema": {"type": "integer", "default": 100}
        }
    ],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "todos": {"type": "array"},
                            "total": {"type": "integer"}
                        }
                    }
                }
            }
        }
    },
    tags=["todos"]
)

TODO_CREATE_DOC = EndpointDoc(
    method="POST",
    path="/api/v2/todos",
    summary="Create todo",
    description="Create a new todo item",
    request_body={
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_date": {"type": "string", "format": "date-time"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "example": {
                    "title": "Complete project",
                    "description": "Finish the Phase V implementation",
                    "priority": "high",
                    "due_date": "2026-02-20T09:00:00Z",
                    "tags": ["work", "important"]
                }
            }
        }
    },
    responses={
        201: {"description": "Todo created successfully"},
        400: {"description": "Invalid request"}
    },
    tags=["todos"]
)


# Generate documentation
def generate_api_docs():
    """Generate API documentation."""
    generator = APIDocGenerator(
        title="Todo App API",
        version="2.0.0",
        description="RESTful API for managing todos with advanced features"
    )

    # Add endpoints
    generator.add_endpoint(TODO_LIST_DOC)
    generator.add_endpoint(TODO_CREATE_DOC)

    # Generate OpenAPI spec
    openapi_spec = generator.generate_openapi()

    # Generate Markdown
    markdown_doc = generator.generate_markdown()

    return {
        "openapi": openapi_spec,
        "markdown": markdown_doc
    }

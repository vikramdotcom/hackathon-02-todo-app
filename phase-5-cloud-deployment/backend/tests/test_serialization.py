"""
Tests for Serialization Utilities
"""

import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from app.serialization import (
    EnhancedJSONEncoder,
    Serializer,
    ResponseFormatter,
    RequestParser
)


class Priority(str, Enum):
    """Test enum."""
    LOW = "low"
    HIGH = "high"


class TodoModel(BaseModel):
    """Test Pydantic model."""
    id: int
    title: str
    completed: bool = False


class TestEnhancedJSONEncoder:
    """Test EnhancedJSONEncoder class."""

    def test_encode_datetime(self):
        """Test encoding datetime objects."""
        dt = datetime(2026, 2, 11, 10, 30, 0)
        result = json.dumps({"timestamp": dt}, cls=EnhancedJSONEncoder)

        assert "2026-02-11T10:30:00" in result

    def test_encode_date(self):
        """Test encoding date objects."""
        d = date(2026, 2, 11)
        result = json.dumps({"date": d}, cls=EnhancedJSONEncoder)

        assert "2026-02-11" in result

    def test_encode_decimal(self):
        """Test encoding Decimal objects."""
        dec = Decimal("123.45")
        result = json.dumps({"amount": dec}, cls=EnhancedJSONEncoder)

        assert "123.45" in result

    def test_encode_enum(self):
        """Test encoding Enum objects."""
        priority = Priority.HIGH
        result = json.dumps({"priority": priority}, cls=EnhancedJSONEncoder)

        assert "high" in result

    def test_encode_pydantic_model(self):
        """Test encoding Pydantic models."""
        todo = TodoModel(id=1, title="Test")
        result = json.dumps({"todo": todo}, cls=EnhancedJSONEncoder)

        assert "Test" in result
        assert "1" in result


class TestSerializer:
    """Test Serializer class."""

    def test_to_json(self):
        """Test serializing to JSON."""
        data = {"id": 1, "title": "Test"}
        result = Serializer.to_json(data)

        assert isinstance(result, str)
        assert "Test" in result

    def test_to_json_pretty(self):
        """Test pretty printing JSON."""
        data = {"id": 1, "title": "Test"}
        result = Serializer.to_json(data, pretty=True)

        assert "\n" in result
        assert "  " in result

    def test_from_json(self):
        """Test deserializing from JSON."""
        json_str = '{"id": 1, "title": "Test"}'
        result = Serializer.from_json(json_str)

        assert result["id"] == 1
        assert result["title"] == "Test"

    def test_from_json_with_model(self):
        """Test deserializing to Pydantic model."""
        json_str = '{"id": 1, "title": "Test", "completed": false}'
        result = Serializer.from_json(json_str, TodoModel)

        assert isinstance(result, TodoModel)
        assert result.id == 1
        assert result.title == "Test"

    def test_to_dict(self):
        """Test converting model to dict."""
        todo = TodoModel(id=1, title="Test")
        result = Serializer.to_dict(todo)

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["title"] == "Test"

    def test_to_dict_exclude_none(self):
        """Test excluding None values."""
        class OptionalModel(BaseModel):
            id: int
            title: str
            description: str = None

        model = OptionalModel(id=1, title="Test")
        result = Serializer.to_dict(model, exclude_none=True)

        assert "description" not in result

    def test_from_dict(self):
        """Test creating model from dict."""
        data = {"id": 1, "title": "Test", "completed": False}
        result = Serializer.from_dict(data, TodoModel)

        assert isinstance(result, TodoModel)
        assert result.id == 1

    def test_to_camel_case(self):
        """Test snake_case to camelCase conversion."""
        assert Serializer.to_camel_case("user_id") == "userId"
        assert Serializer.to_camel_case("created_at") == "createdAt"
        assert Serializer.to_camel_case("is_completed") == "isCompleted"

    def test_to_snake_case(self):
        """Test camelCase to snake_case conversion."""
        assert Serializer.to_snake_case("userId") == "user_id"
        assert Serializer.to_snake_case("createdAt") == "created_at"
        assert Serializer.to_snake_case("isCompleted") == "is_completed"

    def test_dict_to_camel_case(self):
        """Test converting dict keys to camelCase."""
        data = {
            "user_id": 1,
            "created_at": "2026-02-11",
            "is_completed": False
        }
        result = Serializer.dict_to_camel_case(data)

        assert "userId" in result
        assert "createdAt" in result
        assert "isCompleted" in result
        assert "user_id" not in result

    def test_dict_to_camel_case_nested(self):
        """Test converting nested dict keys to camelCase."""
        data = {
            "user_id": 1,
            "user_profile": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
        result = Serializer.dict_to_camel_case(data)

        assert "userId" in result
        assert "userProfile" in result
        assert "firstName" in result["userProfile"]
        assert "lastName" in result["userProfile"]

    def test_dict_to_snake_case(self):
        """Test converting dict keys to snake_case."""
        data = {
            "userId": 1,
            "createdAt": "2026-02-11",
            "isCompleted": False
        }
        result = Serializer.dict_to_snake_case(data)

        assert "user_id" in result
        assert "created_at" in result
        assert "is_completed" in result
        assert "userId" not in result

    def test_dict_to_snake_case_with_list(self):
        """Test converting dict with list values."""
        data = {
            "userId": 1,
            "todoItems": [
                {"itemId": 1, "itemTitle": "Test"}
            ]
        }
        result = Serializer.dict_to_snake_case(data)

        assert "user_id" in result
        assert "todo_items" in result
        assert "item_id" in result["todo_items"][0]


class TestResponseFormatter:
    """Test ResponseFormatter class."""

    def test_success_response(self):
        """Test formatting success response."""
        data = {"id": 1, "title": "Test"}
        result = ResponseFormatter.success(data)

        assert result["success"] is True
        assert result["data"] == data

    def test_success_response_with_message(self):
        """Test success response with message."""
        data = {"id": 1}
        result = ResponseFormatter.success(data, message="Created successfully")

        assert result["message"] == "Created successfully"

    def test_success_response_with_metadata(self):
        """Test success response with metadata."""
        data = {"id": 1}
        metadata = {"version": "2.0.0"}
        result = ResponseFormatter.success(data, metadata=metadata)

        assert result["metadata"] == metadata

    def test_error_response(self):
        """Test formatting error response."""
        result = ResponseFormatter.error(
            "validation_error",
            "Invalid input",
            status_code=400
        )

        assert result["success"] is False
        assert result["error"]["type"] == "validation_error"
        assert result["error"]["message"] == "Invalid input"
        assert result["error"]["status_code"] == 400

    def test_error_response_with_details(self):
        """Test error response with details."""
        details = {"field": "title", "reason": "required"}
        result = ResponseFormatter.error(
            "validation_error",
            "Invalid input",
            details=details
        )

        assert result["error"]["details"] == details

    def test_paginated_response(self):
        """Test formatting paginated response."""
        items = [{"id": 1}, {"id": 2}]
        result = ResponseFormatter.paginated(
            items=items,
            total=10,
            page=1,
            page_size=2
        )

        assert result["success"] is True
        assert result["data"] == items
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 2
        assert result["pagination"]["total_items"] == 10
        assert result["pagination"]["total_pages"] == 5
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_previous"] is False

    def test_paginated_response_last_page(self):
        """Test paginated response on last page."""
        items = [{"id": 9}, {"id": 10}]
        result = ResponseFormatter.paginated(
            items=items,
            total=10,
            page=5,
            page_size=2
        )

        assert result["pagination"]["has_next"] is False
        assert result["pagination"]["has_previous"] is True


class TestRequestParser:
    """Test RequestParser class."""

    def test_parse_query_params(self):
        """Test parsing query parameters."""
        params = {
            "completed": True,
            "priority": "high",
            "invalid": "value"
        }
        allowed = ["completed", "priority"]
        result = RequestParser.parse_query_params(params, allowed)

        assert "completed" in result
        assert "priority" in result
        assert "invalid" not in result

    def test_parse_query_params_exclude_none(self):
        """Test excluding None values."""
        params = {
            "completed": True,
            "priority": None
        }
        allowed = ["completed", "priority"]
        result = RequestParser.parse_query_params(params, allowed)

        assert "completed" in result
        assert "priority" not in result

    def test_parse_pagination_defaults(self):
        """Test pagination with default values."""
        page, page_size = RequestParser.parse_pagination()

        assert page == 1
        assert page_size == 20

    def test_parse_pagination_custom(self):
        """Test pagination with custom values."""
        page, page_size = RequestParser.parse_pagination(page=3, page_size=50)

        assert page == 3
        assert page_size == 50

    def test_parse_pagination_max_limit(self):
        """Test pagination respects max limit."""
        page, page_size = RequestParser.parse_pagination(
            page_size=200,
            max_page_size=100
        )

        assert page_size == 100

    def test_parse_pagination_min_values(self):
        """Test pagination enforces minimum values."""
        page, page_size = RequestParser.parse_pagination(page=0, page_size=0)

        assert page == 1
        assert page_size == 1

    def test_parse_sort_default(self):
        """Test sort with default values."""
        field, order = RequestParser.parse_sort(
            None,
            ["created_at", "title"]
        )

        assert field == "created_at"
        assert order == "desc"

    def test_parse_sort_custom(self):
        """Test sort with custom values."""
        field, order = RequestParser.parse_sort(
            "title:asc",
            ["created_at", "title"]
        )

        assert field == "title"
        assert order == "asc"

    def test_parse_sort_invalid_field(self):
        """Test sort with invalid field falls back to default."""
        field, order = RequestParser.parse_sort(
            "invalid:asc",
            ["created_at", "title"]
        )

        assert field == "created_at"

    def test_parse_sort_invalid_order(self):
        """Test sort with invalid order falls back to default."""
        field, order = RequestParser.parse_sort(
            "title:invalid",
            ["created_at", "title"]
        )

        assert order == "desc"

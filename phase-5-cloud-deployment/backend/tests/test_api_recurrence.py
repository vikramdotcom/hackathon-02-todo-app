"""
Integration Tests for Recurrence Pattern API Endpoints

Tests the complete API flow for recurrence patterns.
"""

import pytest
from datetime import datetime, timedelta


class TestRecurrencePatternAPICreate:
    """Test recurrence pattern creation via API."""

    def test_create_daily_pattern(self, client):
        """Test creating a daily recurrence pattern."""
        response = client.post(
            "/api/v2/recurrence-patterns/",
            json={
                "frequency": "daily",
                "interval": 1,
                "end_condition": "never"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "daily"
        assert data["interval"] == 1
        assert data["end_condition"] == "never"

    def test_create_weekly_pattern_with_days(self, client):
        """Test creating weekly pattern with specific days."""
        response = client.post(
            "/api/v2/recurrence-patterns/",
            json={
                "frequency": "weekly",
                "interval": 1,
                "end_condition": "never",
                "days_of_week": [0, 2, 4]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "weekly"
        assert data["days_of_week"] == [0, 2, 4]

    def test_create_pattern_with_end_after_occurrences(self, client):
        """Test creating pattern that ends after N occurrences."""
        response = client.post(
            "/api/v2/recurrence-patterns/",
            json={
                "frequency": "daily",
                "interval": 1,
                "end_condition": "after_occurrences",
                "end_after_occurrences": 10
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["end_condition"] == "after_occurrences"
        assert data["end_after_occurrences"] == 10


class TestRecurrencePatternAPIRead:
    """Test recurrence pattern retrieval via API."""

    def test_get_pattern_by_id(self, client, sample_recurrence_pattern):
        """Test retrieving pattern by ID."""
        response = client.get(
            f"/api/v2/recurrence-patterns/{sample_recurrence_pattern.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_recurrence_pattern.id
        assert data["frequency"] == sample_recurrence_pattern.frequency.value

    def test_get_nonexistent_pattern(self, client):
        """Test retrieving nonexistent pattern returns 404."""
        response = client.get("/api/v2/recurrence-patterns/99999")
        
        assert response.status_code == 404


class TestRecurrencePatternAPIUpdate:
    """Test recurrence pattern updates via API."""

    def test_update_pattern_interval(self, client, sample_recurrence_pattern):
        """Test updating pattern interval."""
        response = client.patch(
            f"/api/v2/recurrence-patterns/{sample_recurrence_pattern.id}",
            json={"interval": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interval"] == 2


class TestRecurringTodoAPICreate:
    """Test creating recurring todo with inline pattern."""

    def test_create_recurring_todo_with_pattern(self, client):
        """Test creating recurring todo with inline pattern."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        response = client.post(
            "/api/v2/recurrence-patterns/recurring-todo",
            json={
                "todo": {
                    "title": "Weekly Meeting",
                    "description": "Team standup",
                    "priority": "high",
                    "tags": ["work"],
                    "due_date": due_date
                },
                "recurrence_pattern": {
                    "frequency": "weekly",
                    "interval": 1,
                    "end_condition": "never",
                    "days_of_week": [0, 2, 4]
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "todo" in data
        assert "recurrence_pattern" in data
        assert data["todo"]["title"] == "Weekly Meeting"
        assert data["recurrence_pattern"]["frequency"] == "weekly"

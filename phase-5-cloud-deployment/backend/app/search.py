"""
Search and Filtering Utilities

Advanced search and filtering capabilities for todos.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from enum import Enum

logger = logging.getLogger(__name__)


class SearchOperator(str, Enum):
    """Search operators."""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"


class FilterCondition:
    """Filter condition."""

    def __init__(self, field: str, operator: SearchOperator, value: Any):
        """Initialize filter condition."""
        self.field = field
        self.operator = operator
        self.value = value

    def matches(self, item: Dict[str, Any]) -> bool:
        """Check if item matches condition."""
        field_value = item.get(self.field)

        if field_value is None:
            return False

        if self.operator == SearchOperator.EQUALS:
            return field_value == self.value

        elif self.operator == SearchOperator.NOT_EQUALS:
            return field_value != self.value

        elif self.operator == SearchOperator.GREATER_THAN:
            return field_value > self.value

        elif self.operator == SearchOperator.GREATER_THAN_OR_EQUAL:
            return field_value >= self.value

        elif self.operator == SearchOperator.LESS_THAN:
            return field_value < self.value

        elif self.operator == SearchOperator.LESS_THAN_OR_EQUAL:
            return field_value <= self.value

        elif self.operator == SearchOperator.CONTAINS:
            return str(self.value).lower() in str(field_value).lower()

        elif self.operator == SearchOperator.STARTS_WITH:
            return str(field_value).lower().startswith(str(self.value).lower())

        elif self.operator == SearchOperator.ENDS_WITH:
            return str(field_value).lower().endswith(str(self.value).lower())

        elif self.operator == SearchOperator.IN:
            return field_value in self.value

        elif self.operator == SearchOperator.NOT_IN:
            return field_value not in self.value

        elif self.operator == SearchOperator.BETWEEN:
            return self.value[0] <= field_value <= self.value[1]

        return False


class SearchQuery:
    """Search query builder."""

    def __init__(self):
        """Initialize search query."""
        self.conditions: List[FilterCondition] = []
        self.sort_field: Optional[str] = None
        self.sort_order: str = "asc"
        self.limit: Optional[int] = None
        self.offset: int = 0

    def filter(self, field: str, operator: SearchOperator, value: Any) -> 'SearchQuery':
        """Add filter condition."""
        self.conditions.append(FilterCondition(field, operator, value))
        return self

    def sort(self, field: str, order: str = "asc") -> 'SearchQuery':
        """Set sort order."""
        self.sort_field = field
        self.sort_order = order
        return self

    def paginate(self, limit: int, offset: int = 0) -> 'SearchQuery':
        """Set pagination."""
        self.limit = limit
        self.offset = offset
        return self

    def execute(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute search query."""
        # Apply filters
        filtered = data
        for condition in self.conditions:
            filtered = [item for item in filtered if condition.matches(item)]

        # Apply sorting
        if self.sort_field:
            reverse = self.sort_order == "desc"
            filtered.sort(key=lambda x: x.get(self.sort_field, ""), reverse=reverse)

        # Apply pagination
        if self.limit:
            start = self.offset
            end = start + self.limit
            filtered = filtered[start:end]

        return filtered


class FullTextSearch:
    """Full-text search implementation."""

    @staticmethod
    def search(
        data: List[Dict[str, Any]],
        query: str,
        fields: List[str],
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform full-text search.

        Args:
            data: List of items to search
            query: Search query
            fields: Fields to search in
            case_sensitive: Case sensitive search

        Returns:
            Matching items
        """
        if not query:
            return data

        query_lower = query if case_sensitive else query.lower()
        results = []

        for item in data:
            for field in fields:
                field_value = item.get(field, "")
                field_str = str(field_value)

                if not case_sensitive:
                    field_str = field_str.lower()

                if query_lower in field_str:
                    results.append(item)
                    break

        return results

    @staticmethod
    def search_with_ranking(
        data: List[Dict[str, Any]],
        query: str,
        fields: List[str],
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with relevance ranking.

        Args:
            data: List of items to search
            query: Search query
            fields: Fields to search in
            weights: Field weights for ranking

        Returns:
            Ranked results
        """
        if not query:
            return data

        weights = weights or {field: 1.0 for field in fields}
        query_lower = query.lower()
        scored_results = []

        for item in data:
            score = 0.0

            for field in fields:
                field_value = str(item.get(field, "")).lower()
                weight = weights.get(field, 1.0)

                # Exact match
                if query_lower == field_value:
                    score += 10.0 * weight

                # Starts with
                elif field_value.startswith(query_lower):
                    score += 5.0 * weight

                # Contains
                elif query_lower in field_value:
                    score += 2.0 * weight

                # Word match
                words = field_value.split()
                for word in words:
                    if query_lower in word:
                        score += 1.0 * weight

            if score > 0:
                scored_results.append((item, score))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return [item for item, score in scored_results]


class FacetedSearch:
    """Faceted search for filtering."""

    @staticmethod
    def get_facets(
        data: List[Dict[str, Any]],
        facet_fields: List[str]
    ) -> Dict[str, Dict[str, int]]:
        """
        Get facet counts.

        Args:
            data: List of items
            facet_fields: Fields to facet on

        Returns:
            Facet counts
        """
        facets = {}

        for field in facet_fields:
            facets[field] = {}

            for item in data:
                value = item.get(field)

                if value is not None:
                    # Handle list values
                    if isinstance(value, list):
                        for v in value:
                            facets[field][str(v)] = facets[field].get(str(v), 0) + 1
                    else:
                        facets[field][str(value)] = facets[field].get(str(value), 0) + 1

        return facets

    @staticmethod
    def apply_facets(
        data: List[Dict[str, Any]],
        selected_facets: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Apply facet filters.

        Args:
            data: List of items
            selected_facets: Selected facet values

        Returns:
            Filtered items
        """
        filtered = data

        for field, values in selected_facets.items():
            filtered = [
                item for item in filtered
                if str(item.get(field)) in values
            ]

        return filtered


class DateRangeFilter:
    """Date range filtering."""

    @staticmethod
    def filter_by_date_range(
        data: List[Dict[str, Any]],
        field: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter by date range.

        Args:
            data: List of items
            field: Date field name
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Filtered items
        """
        filtered = data

        if start_date:
            filtered = [
                item for item in filtered
                if item.get(field) and item[field] >= start_date
            ]

        if end_date:
            filtered = [
                item for item in filtered
                if item.get(field) and item[field] <= end_date
            ]

        return filtered

    @staticmethod
    def filter_by_relative_date(
        data: List[Dict[str, Any]],
        field: str,
        days: int,
        direction: str = "past"
    ) -> List[Dict[str, Any]]:
        """
        Filter by relative date.

        Args:
            data: List of items
            field: Date field name
            days: Number of days
            direction: "past" or "future"

        Returns:
            Filtered items
        """
        from datetime import timedelta

        today = date.today()

        if direction == "past":
            cutoff_date = today - timedelta(days=days)
            return [
                item for item in data
                if item.get(field) and item[field] >= cutoff_date
            ]
        else:  # future
            cutoff_date = today + timedelta(days=days)
            return [
                item for item in data
                if item.get(field) and item[field] <= cutoff_date
            ]


# Example usage
def search_todos(
    todos: List[Dict[str, Any]],
    query: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    overdue_only: bool = False
) -> List[Dict[str, Any]]:
    """Search todos with filters."""
    search_query = SearchQuery()

    # Text search
    if query:
        todos = FullTextSearch.search(
            todos,
            query,
            fields=["title", "description"]
        )

    # Priority filter
    if priority:
        search_query.filter("priority", SearchOperator.EQUALS, priority)

    # Completed filter
    if completed is not None:
        search_query.filter("completed", SearchOperator.EQUALS, completed)

    # Tags filter
    if tags:
        for tag in tags:
            search_query.filter("tags", SearchOperator.CONTAINS, tag)

    # Overdue filter
    if overdue_only:
        search_query.filter("is_overdue", SearchOperator.EQUALS, True)

    return search_query.execute(todos)

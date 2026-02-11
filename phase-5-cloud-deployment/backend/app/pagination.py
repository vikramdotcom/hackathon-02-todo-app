"""
Pagination Utilities for API Responses

Provides utilities for paginating large result sets.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    page: int = 1
    page_size: int = 20

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20
            }
        }

    def get_offset(self) -> int:
        """Calculate offset from page number."""
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        """Get limit (page size)."""
        return self.page_size


class PageMetadata(BaseModel):
    """Metadata for paginated response."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "total_items": 100,
                "total_pages": 5,
                "has_next": True,
                "has_previous": False
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    metadata: PageMetadata

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Paginator:
    """Utility class for creating paginated responses."""

    @staticmethod
    def paginate(
        items: List[T],
        total_count: int,
        page: int,
        page_size: int
    ) -> PaginatedResponse[T]:
        """
        Create a paginated response.

        Args:
            items: List of items for current page
            total_count: Total number of items across all pages
            page: Current page number (1-indexed)
            page_size: Number of items per page

        Returns:
            PaginatedResponse with items and metadata
        """
        total_pages = ceil(total_count / page_size) if page_size > 0 else 0

        metadata = PageMetadata(
            page=page,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )

        return PaginatedResponse(
            items=items,
            metadata=metadata
        )

    @staticmethod
    def get_page_links(
        base_url: str,
        page: int,
        total_pages: int,
        page_size: int
    ) -> dict:
        """
        Generate pagination links for HATEOAS.

        Args:
            base_url: Base URL for the resource
            page: Current page number
            total_pages: Total number of pages
            page_size: Number of items per page

        Returns:
            Dict with pagination links
        """
        links = {
            "self": f"{base_url}?page={page}&page_size={page_size}",
            "first": f"{base_url}?page=1&page_size={page_size}",
            "last": f"{base_url}?page={total_pages}&page_size={page_size}"
        }

        if page > 1:
            links["previous"] = f"{base_url}?page={page - 1}&page_size={page_size}"

        if page < total_pages:
            links["next"] = f"{base_url}?page={page + 1}&page_size={page_size}"

        return links


def validate_pagination_params(page: int, page_size: int) -> tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.

    Args:
        page: Page number
        page_size: Page size

    Returns:
        Tuple of (is_valid, error_message)
    """
    if page < 1:
        return False, "Page number must be at least 1"

    if page_size < 1:
        return False, "Page size must be at least 1"

    if page_size > 100:
        return False, "Page size cannot exceed 100"

    return True, None

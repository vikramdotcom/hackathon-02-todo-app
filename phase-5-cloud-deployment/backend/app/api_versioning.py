"""
API Versioning Utilities

Provides utilities for managing API versions and deprecation.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, date
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class APIVersion(str, Enum):
    """API version identifiers."""

    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class DeprecationStatus(str, Enum):
    """Deprecation status."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


class VersionInfo:
    """API version information."""

    def __init__(
        self,
        version: APIVersion,
        status: DeprecationStatus = DeprecationStatus.ACTIVE,
        release_date: Optional[date] = None,
        deprecation_date: Optional[date] = None,
        sunset_date: Optional[date] = None,
        changelog: Optional[List[str]] = None
    ):
        """
        Initialize version info.

        Args:
            version: API version
            status: Deprecation status
            release_date: Release date
            deprecation_date: Deprecation date
            sunset_date: Sunset date
            changelog: List of changes
        """
        self.version = version
        self.status = status
        self.release_date = release_date or date.today()
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.changelog = changelog or []

    def is_deprecated(self) -> bool:
        """Check if version is deprecated."""
        return self.status in [DeprecationStatus.DEPRECATED, DeprecationStatus.SUNSET]

    def is_sunset(self) -> bool:
        """Check if version is sunset."""
        return self.status == DeprecationStatus.SUNSET

    def days_until_sunset(self) -> Optional[int]:
        """Get days until sunset."""
        if not self.sunset_date:
            return None

        delta = self.sunset_date - date.today()
        return max(0, delta.days)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "status": self.status,
            "release_date": self.release_date.isoformat(),
            "deprecation_date": self.deprecation_date.isoformat() if self.deprecation_date else None,
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
            "days_until_sunset": self.days_until_sunset(),
            "changelog": self.changelog
        }


class VersionManager:
    """Manage API versions."""

    def __init__(self):
        """Initialize version manager."""
        self.versions: Dict[APIVersion, VersionInfo] = {}
        self.default_version: Optional[APIVersion] = None

    def register_version(self, version_info: VersionInfo):
        """
        Register API version.

        Args:
            version_info: Version information
        """
        self.versions[version_info.version] = version_info

        # Set as default if first version
        if self.default_version is None:
            self.default_version = version_info.version

        logger.info(
            f"Registered API version {version_info.version}",
            extra={
                "version": version_info.version,
                "status": version_info.status
            }
        )

    def get_version(self, version: APIVersion) -> Optional[VersionInfo]:
        """
        Get version information.

        Args:
            version: API version

        Returns:
            Version info or None
        """
        return self.versions.get(version)

    def get_latest_version(self) -> Optional[VersionInfo]:
        """
        Get latest active version.

        Returns:
            Latest version info
        """
        active_versions = [
            v for v in self.versions.values()
            if v.status == DeprecationStatus.ACTIVE
        ]

        if not active_versions:
            return None

        # Sort by release date descending
        active_versions.sort(key=lambda v: v.release_date, reverse=True)

        return active_versions[0]

    def list_versions(
        self,
        include_deprecated: bool = True,
        include_sunset: bool = False
    ) -> List[VersionInfo]:
        """
        List API versions.

        Args:
            include_deprecated: Include deprecated versions
            include_sunset: Include sunset versions

        Returns:
            List of version info
        """
        versions = list(self.versions.values())

        if not include_deprecated:
            versions = [v for v in versions if v.status != DeprecationStatus.DEPRECATED]

        if not include_sunset:
            versions = [v for v in versions if v.status != DeprecationStatus.SUNSET]

        # Sort by release date descending
        versions.sort(key=lambda v: v.release_date, reverse=True)

        return versions

    def deprecate_version(
        self,
        version: APIVersion,
        deprecation_date: Optional[date] = None,
        sunset_date: Optional[date] = None
    ):
        """
        Deprecate API version.

        Args:
            version: API version
            deprecation_date: Deprecation date
            sunset_date: Sunset date
        """
        version_info = self.versions.get(version)

        if not version_info:
            raise ValueError(f"Version {version} not found")

        version_info.status = DeprecationStatus.DEPRECATED
        version_info.deprecation_date = deprecation_date or date.today()
        version_info.sunset_date = sunset_date

        logger.warning(
            f"Deprecated API version {version}",
            extra={
                "version": version,
                "deprecation_date": version_info.deprecation_date.isoformat(),
                "sunset_date": version_info.sunset_date.isoformat() if sunset_date else None
            }
        )

    def sunset_version(self, version: APIVersion):
        """
        Sunset API version.

        Args:
            version: API version
        """
        version_info = self.versions.get(version)

        if not version_info:
            raise ValueError(f"Version {version} not found")

        version_info.status = DeprecationStatus.SUNSET

        logger.error(
            f"Sunset API version {version}",
            extra={"version": version}
        )


# Global version manager
version_manager = VersionManager()


# Decorators
def versioned(version: APIVersion):
    """
    Decorator to mark endpoint with version.

    Args:
        version: API version

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if version is sunset
            version_info = version_manager.get_version(version)

            if version_info and version_info.is_sunset():
                raise ValueError(f"API version {version} is no longer available")

            # Add deprecation warning if deprecated
            if version_info and version_info.is_deprecated():
                logger.warning(
                    f"Using deprecated API version {version}",
                    extra={
                        "version": version,
                        "days_until_sunset": version_info.days_until_sunset()
                    }
                )

            return await func(*args, **kwargs)

        # Store version metadata
        wrapper._api_version = version

        return wrapper
    return decorator


def deprecated(
    message: str,
    sunset_date: Optional[date] = None,
    alternative: Optional[str] = None
):
    """
    Decorator to mark endpoint as deprecated.

    Args:
        message: Deprecation message
        sunset_date: Sunset date
        alternative: Alternative endpoint

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Log deprecation warning
            logger.warning(
                f"Deprecated endpoint called: {func.__name__}",
                extra={
                    "endpoint": func.__name__,
                    "message": message,
                    "sunset_date": sunset_date.isoformat() if sunset_date else None,
                    "alternative": alternative
                }
            )

            return await func(*args, **kwargs)

        # Store deprecation metadata
        wrapper._deprecated = True
        wrapper._deprecation_message = message
        wrapper._sunset_date = sunset_date
        wrapper._alternative = alternative

        return wrapper
    return decorator


# Version negotiation
class VersionNegotiator:
    """Negotiate API version from request."""

    @staticmethod
    def from_header(headers: Dict[str, str]) -> Optional[APIVersion]:
        """
        Extract version from Accept header.

        Args:
            headers: Request headers

        Returns:
            API version or None
        """
        accept = headers.get("accept", "")

        # Parse Accept header for version
        # Example: application/vnd.api+json; version=2
        if "version=" in accept:
            version_str = accept.split("version=")[1].split(";")[0].strip()
            try:
                return APIVersion(f"v{version_str}")
            except ValueError:
                pass

        return None

    @staticmethod
    def from_path(path: str) -> Optional[APIVersion]:
        """
        Extract version from URL path.

        Args:
            path: Request path

        Returns:
            API version or None
        """
        # Example: /api/v2/todos
        parts = path.split("/")

        for part in parts:
            if part.startswith("v") and part[1:].isdigit():
                try:
                    return APIVersion(part)
                except ValueError:
                    pass

        return None

    @staticmethod
    def from_query(query_params: Dict[str, str]) -> Optional[APIVersion]:
        """
        Extract version from query parameter.

        Args:
            query_params: Query parameters

        Returns:
            API version or None
        """
        version_str = query_params.get("version") or query_params.get("api_version")

        if version_str:
            try:
                if not version_str.startswith("v"):
                    version_str = f"v{version_str}"
                return APIVersion(version_str)
            except ValueError:
                pass

        return None

    @staticmethod
    def negotiate(
        headers: Dict[str, str],
        path: str,
        query_params: Dict[str, str]
    ) -> APIVersion:
        """
        Negotiate API version from request.

        Args:
            headers: Request headers
            path: Request path
            query_params: Query parameters

        Returns:
            Negotiated API version
        """
        # Try path first (most explicit)
        version = VersionNegotiator.from_path(path)
        if version:
            return version

        # Try header
        version = VersionNegotiator.from_header(headers)
        if version:
            return version

        # Try query parameter
        version = VersionNegotiator.from_query(query_params)
        if version:
            return version

        # Return default version
        latest = version_manager.get_latest_version()
        if latest:
            return latest.version

        # Fallback to v1
        return APIVersion.V1


# Setup default versions
def setup_versions():
    """Setup default API versions."""

    # V1 - Deprecated
    version_manager.register_version(VersionInfo(
        version=APIVersion.V1,
        status=DeprecationStatus.DEPRECATED,
        release_date=date(2025, 1, 1),
        deprecation_date=date(2025, 6, 1),
        sunset_date=date(2026, 1, 1),
        changelog=[
            "Initial API release",
            "Basic CRUD operations"
        ]
    ))

    # V2 - Active
    version_manager.register_version(VersionInfo(
        version=APIVersion.V2,
        status=DeprecationStatus.ACTIVE,
        release_date=date(2025, 6, 1),
        changelog=[
            "Added recurrence patterns",
            "Added due dates and priorities",
            "Added tags and reminders",
            "Improved search functionality"
        ]
    ))

    # V3 - Future
    version_manager.register_version(VersionInfo(
        version=APIVersion.V3,
        status=DeprecationStatus.ACTIVE,
        release_date=date(2026, 1, 1),
        changelog=[
            "GraphQL support",
            "Real-time subscriptions",
            "Advanced filtering",
            "Batch operations"
        ]
    ))

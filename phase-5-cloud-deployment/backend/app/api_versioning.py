"""
API Versioning System

Manage multiple API versions with backward compatibility.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class VersionStatus(str, Enum):
    """API version status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


class APIVersion:
    """API version entity."""

    def __init__(self, version: str, status: VersionStatus = VersionStatus.ACTIVE):
        """Initialize API version."""
        self.version = version
        self.status = status
        self.endpoints: Dict[str, Callable] = {}
        self.created_at = datetime.utcnow()
        self.deprecated_at: Optional[datetime] = None
        self.sunset_at: Optional[datetime] = None

    def register_endpoint(self, path: str, handler: Callable):
        """Register endpoint."""
        self.endpoints[path] = handler

    def get_endpoint(self, path: str) -> Optional[Callable]:
        """Get endpoint handler."""
        return self.endpoints.get(path)


class APIVersionManager:
    """Manage API versions."""

    def __init__(self):
        """Initialize API version manager."""
        self.versions: Dict[str, APIVersion] = {}
        self.default_version: Optional[str] = None

    def register_version(self, version: str, status: VersionStatus = VersionStatus.ACTIVE):
        """Register API version."""
        api_version = APIVersion(version, status)
        self.versions[version] = api_version

        if not self.default_version:
            self.default_version = version

        logger.info(f"API version registered: {version}")

    def get_version(self, version: Optional[str] = None) -> Optional[APIVersion]:
        """Get API version."""
        if not version:
            version = self.default_version

        return self.versions.get(version)

    def deprecate_version(self, version: str):
        """Deprecate API version."""
        if version in self.versions:
            self.versions[version].status = VersionStatus.DEPRECATED
            self.versions[version].deprecated_at = datetime.utcnow()
            logger.warning(f"API version deprecated: {version}")


# Global instance
api_version_manager = APIVersionManager()

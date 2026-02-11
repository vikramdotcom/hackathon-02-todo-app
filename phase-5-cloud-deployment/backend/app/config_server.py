"""
Configuration Server

Centralized configuration management for microservices.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigServer:
    """Centralized configuration server."""

    def __init__(self):
        """Initialize config server."""
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.versions: Dict[str, int] = {}

    def set_config(self, service_name: str, config: Dict[str, Any]):
        """Set configuration for service."""
        self.configs[service_name] = config
        self.versions[service_name] = self.versions.get(service_name, 0) + 1
        logger.info(f"Config updated: {service_name} (v{self.versions[service_name]})")

    def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for service."""
        return self.configs.get(service_name)

    def get_version(self, service_name: str) -> int:
        """Get config version."""
        return self.versions.get(service_name, 0)


config_server = ConfigServer()

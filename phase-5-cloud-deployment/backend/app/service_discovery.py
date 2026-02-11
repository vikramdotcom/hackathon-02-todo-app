"""
Service Discovery System

Automatic service registration and discovery.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ServiceInstance:
    """Service instance."""

    def __init__(self, service_name: str, host: str, port: int, metadata: Optional[Dict[str, Any]] = None):
        """Initialize service instance."""
        self.service_name = service_name
        self.host = host
        self.port = port
        self.metadata = metadata or {}
        self.registered_at = datetime.utcnow()
        self.last_heartbeat = self.registered_at
        self.healthy = True

    def heartbeat(self):
        """Update heartbeat."""
        self.last_heartbeat = datetime.utcnow()
        self.healthy = True

    def is_expired(self, timeout_seconds: int = 30) -> bool:
        """Check if instance is expired."""
        elapsed = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return elapsed > timeout_seconds


class ServiceRegistry:
    """Service registry for discovery."""

    def __init__(self):
        """Initialize service registry."""
        self.services: Dict[str, List[ServiceInstance]] = {}

    def register(self, service_name: str, host: str, port: int, metadata: Optional[Dict[str, Any]] = None):
        """Register service instance."""
        instance = ServiceInstance(service_name, host, port, metadata)
        
        if service_name not in self.services:
            self.services[service_name] = []
        
        self.services[service_name].append(instance)
        logger.info(f"Service registered: {service_name} at {host}:{port}")

    def deregister(self, service_name: str, host: str, port: int):
        """Deregister service instance."""
        if service_name in self.services:
            self.services[service_name] = [
                i for i in self.services[service_name]
                if not (i.host == host and i.port == port)
            ]
            logger.info(f"Service deregistered: {service_name} at {host}:{port}")

    def discover(self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances."""
        if service_name not in self.services:
            return []
        
        # Remove expired instances
        self.services[service_name] = [
            i for i in self.services[service_name]
            if not i.is_expired()
        ]
        
        return [i for i in self.services[service_name] if i.healthy]


service_registry = ServiceRegistry()

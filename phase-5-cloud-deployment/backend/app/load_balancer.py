"""
Load Balancer Implementation

Distribute traffic across multiple backend instances.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class Backend:
    """Backend server instance."""

    def __init__(self, host: str, port: int, weight: int = 1):
        """Initialize backend."""
        self.host = host
        self.port = port
        self.weight = weight
        self.healthy = True
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0

    def get_url(self) -> str:
        """Get backend URL."""
        return f"http://{self.host}:{self.port}"


class LoadBalancer:
    """Load balancer with multiple strategies."""

    def __init__(self, strategy: str = "round_robin"):
        """Initialize load balancer."""
        self.strategy = strategy
        self.backends: List[Backend] = []
        self.current_index = 0

    def add_backend(self, host: str, port: int, weight: int = 1):
        """Add backend server."""
        backend = Backend(host, port, weight)
        self.backends.append(backend)
        logger.info(f"Backend added: {host}:{port}")

    def get_next_backend(self) -> Optional[Backend]:
        """Get next backend based on strategy."""
        healthy_backends = [b for b in self.backends if b.healthy]

        if not healthy_backends:
            return None

        if self.strategy == "round_robin":
            return self._round_robin(healthy_backends)
        elif self.strategy == "least_connections":
            return self._least_connections(healthy_backends)
        elif self.strategy == "weighted":
            return self._weighted(healthy_backends)
        elif self.strategy == "random":
            return self._random(healthy_backends)

        return healthy_backends[0]

    def _round_robin(self, backends: List[Backend]) -> Backend:
        """Round robin selection."""
        backend = backends[self.current_index % len(backends)]
        self.current_index += 1
        return backend

    def _least_connections(self, backends: List[Backend]) -> Backend:
        """Least connections selection."""
        return min(backends, key=lambda b: b.active_connections)

    def _weighted(self, backends: List[Backend]) -> Backend:
        """Weighted random selection."""
        total_weight = sum(b.weight for b in backends)
        rand = random.randint(1, total_weight)
        
        cumulative = 0
        for backend in backends:
            cumulative += backend.weight
            if rand <= cumulative:
                return backend
        
        return backends[0]

    def _random(self, backends: List[Backend]) -> Backend:
        """Random selection."""
        return random.choice(backends)


load_balancer = LoadBalancer()

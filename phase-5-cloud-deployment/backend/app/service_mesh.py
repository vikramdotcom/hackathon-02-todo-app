"""
Service Mesh Integration

Integrate with service mesh for advanced networking features.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TrafficPolicy(str, Enum):
    """Traffic routing policies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_conn"
    RANDOM = "random"
    WEIGHTED = "weighted"


class ServiceEndpoint:
    """Service endpoint definition."""

    def __init__(
        self,
        host: str,
        port: int,
        weight: int = 1,
        healthy: bool = True
    ):
        """Initialize service endpoint."""
        self.host = host
        self.port = port
        self.weight = weight
        self.healthy = healthy
        self.last_health_check: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "weight": self.weight,
            "healthy": self.healthy,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }


class ServiceRegistry:
    """Service registry for service discovery."""

    def __init__(self):
        """Initialize service registry."""
        self.services: Dict[str, List[ServiceEndpoint]] = {}

    def register_service(
        self,
        service_name: str,
        endpoint: ServiceEndpoint
    ):
        """Register service endpoint."""
        if service_name not in self.services:
            self.services[service_name] = []

        self.services[service_name].append(endpoint)

        logger.info(
            f"Registered service: {service_name}",
            extra={
                "service": service_name,
                "host": endpoint.host,
                "port": endpoint.port
            }
        )

    def deregister_service(
        self,
        service_name: str,
        host: str,
        port: int
    ):
        """Deregister service endpoint."""
        if service_name in self.services:
            self.services[service_name] = [
                ep for ep in self.services[service_name]
                if not (ep.host == host and ep.port == port)
            ]

            logger.info(f"Deregistered service: {service_name} ({host}:{port})")

    def get_service_endpoints(
        self,
        service_name: str,
        healthy_only: bool = True
    ) -> List[ServiceEndpoint]:
        """Get service endpoints."""
        endpoints = self.services.get(service_name, [])

        if healthy_only:
            endpoints = [ep for ep in endpoints if ep.healthy]

        return endpoints

    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self.services.keys())


class TrafficRouter:
    """Route traffic between service instances."""

    def __init__(self, policy: TrafficPolicy = TrafficPolicy.ROUND_ROBIN):
        """Initialize traffic router."""
        self.policy = policy
        self.current_index: Dict[str, int] = {}

    def select_endpoint(
        self,
        service_name: str,
        endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Select endpoint based on policy."""
        if not endpoints:
            return None

        if self.policy == TrafficPolicy.ROUND_ROBIN:
            return self._round_robin(service_name, endpoints)
        elif self.policy == TrafficPolicy.WEIGHTED:
            return self._weighted(endpoints)
        elif self.policy == TrafficPolicy.RANDOM:
            return self._random(endpoints)
        else:
            return endpoints[0]

    def _round_robin(
        self,
        service_name: str,
        endpoints: List[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """Round-robin selection."""
        if service_name not in self.current_index:
            self.current_index[service_name] = 0

        index = self.current_index[service_name]
        endpoint = endpoints[index]

        self.current_index[service_name] = (index + 1) % len(endpoints)

        return endpoint

    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted selection."""
        import random

        total_weight = sum(ep.weight for ep in endpoints)
        rand_weight = random.randint(1, total_weight)

        cumulative = 0
        for endpoint in endpoints:
            cumulative += endpoint.weight
            if rand_weight <= cumulative:
                return endpoint

        return endpoints[-1]

    def _random(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Random selection."""
        import random
        return random.choice(endpoints)


class RetryPolicy:
    """Retry policy for failed requests."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_on_status: List[int] = [500, 502, 503, 504]
    ):
        """Initialize retry policy."""
        self.max_retries = max_retries
        self.retry_on_status = retry_on_status

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Check if request should be retried."""
        return (
            attempt < self.max_retries and
            status_code in self.retry_on_status
        )


class TimeoutPolicy:
    """Timeout policy for requests."""

    def __init__(
        self,
        connect_timeout_ms: int = 5000,
        request_timeout_ms: int = 30000
    ):
        """Initialize timeout policy."""
        self.connect_timeout_ms = connect_timeout_ms
        self.request_timeout_ms = request_timeout_ms


class MutualTLS:
    """Mutual TLS configuration."""

    def __init__(
        self,
        cert_path: str,
        key_path: str,
        ca_path: str
    ):
        """Initialize mTLS configuration."""
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path

    def get_ssl_context(self):
        """Get SSL context for mTLS."""
        import ssl

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.cert_path, self.key_path)
        context.load_verify_locations(self.ca_path)

        return context


class ServiceMeshProxy:
    """Service mesh sidecar proxy."""

    def __init__(
        self,
        service_name: str,
        service_registry: ServiceRegistry,
        traffic_router: TrafficRouter
    ):
        """Initialize service mesh proxy."""
        self.service_name = service_name
        self.service_registry = service_registry
        self.traffic_router = traffic_router
        self.retry_policy = RetryPolicy()
        self.timeout_policy = TimeoutPolicy()

    async def call_service(
        self,
        target_service: str,
        method: str,
        path: str,
        **kwargs
    ) -> Any:
        """Call another service through mesh."""
        endpoints = self.service_registry.get_service_endpoints(target_service)

        if not endpoints:
            raise Exception(f"No healthy endpoints for service: {target_service}")

        attempt = 0
        last_error = None

        while attempt < self.retry_policy.max_retries:
            endpoint = self.traffic_router.select_endpoint(target_service, endpoints)

            if not endpoint:
                raise Exception(f"No endpoint selected for service: {target_service}")

            try:
                # Make request to endpoint
                url = f"http://{endpoint.host}:{endpoint.port}{path}"

                logger.info(
                    f"Calling service: {target_service}",
                    extra={
                        "target": target_service,
                        "endpoint": f"{endpoint.host}:{endpoint.port}",
                        "attempt": attempt + 1
                    }
                )

                # In production, use actual HTTP client
                # For now, return mock response
                return {"status": "success"}

            except Exception as e:
                last_error = e
                attempt += 1

                logger.warning(
                    f"Service call failed: {target_service}",
                    extra={
                        "target": target_service,
                        "attempt": attempt,
                        "error": str(e)
                    }
                )

        raise Exception(f"Service call failed after {attempt} attempts: {last_error}")


class TrafficSplitting:
    """Traffic splitting for canary deployments."""

    def __init__(self):
        """Initialize traffic splitting."""
        self.splits: Dict[str, Dict[str, float]] = {}

    def configure_split(
        self,
        service_name: str,
        version_weights: Dict[str, float]
    ):
        """Configure traffic split."""
        # Validate weights sum to 1.0
        total = sum(version_weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.splits[service_name] = version_weights

        logger.info(
            f"Configured traffic split for {service_name}",
            extra={"service": service_name, "weights": version_weights}
        )

    def select_version(self, service_name: str) -> Optional[str]:
        """Select version based on weights."""
        if service_name not in self.splits:
            return None

        import random
        rand = random.random()

        cumulative = 0.0
        for version, weight in self.splits[service_name].items():
            cumulative += weight
            if rand <= cumulative:
                return version

        return None


class FaultInjection:
    """Fault injection for chaos testing."""

    def __init__(self):
        """Initialize fault injection."""
        self.fault_rules: List[Dict[str, Any]] = []

    def add_fault_rule(
        self,
        service_name: str,
        fault_type: str,
        percentage: float,
        config: Dict[str, Any]
    ):
        """Add fault injection rule."""
        rule = {
            "service": service_name,
            "type": fault_type,
            "percentage": percentage,
            "config": config
        }

        self.fault_rules.append(rule)

        logger.info(
            f"Added fault injection rule for {service_name}",
            extra={"service": service_name, "type": fault_type}
        )

    def should_inject_fault(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Check if fault should be injected."""
        import random

        for rule in self.fault_rules:
            if rule["service"] == service_name:
                if random.random() < rule["percentage"]:
                    return rule

        return None


class ObservabilityCollector:
    """Collect observability data from mesh."""

    def __init__(self):
        """Initialize observability collector."""
        self.metrics: List[Dict[str, Any]] = []

    def record_request(
        self,
        source_service: str,
        target_service: str,
        duration_ms: float,
        status_code: int
    ):
        """Record service-to-service request."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": source_service,
            "target": target_service,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "success": status_code < 400
        }

        self.metrics.append(metric)

    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for service."""
        service_metrics = [
            m for m in self.metrics
            if m["source"] == service_name or m["target"] == service_name
        ]

        if not service_metrics:
            return {}

        total_requests = len(service_metrics)
        successful = sum(1 for m in service_metrics if m["success"])
        durations = [m["duration_ms"] for m in service_metrics]

        return {
            "total_requests": total_requests,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "p95_duration_ms": self._percentile(durations, 95) if durations else 0
        }

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


class ServiceMeshConfig:
    """Service mesh configuration."""

    def __init__(self):
        """Initialize service mesh config."""
        self.config: Dict[str, Any] = {
            "mtls_enabled": True,
            "tracing_enabled": True,
            "metrics_enabled": True,
            "access_logging": True,
            "default_timeout_ms": 30000,
            "default_retries": 3
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value


# Global instances
service_registry = ServiceRegistry()
traffic_router = TrafficRouter()
traffic_splitting = TrafficSplitting()
fault_injection = FaultInjection()
observability_collector = ObservabilityCollector()
service_mesh_config = ServiceMeshConfig()


# Helper functions
def register_service(service_name: str, host: str, port: int, weight: int = 1):
    """Register service."""
    endpoint = ServiceEndpoint(host, port, weight)
    service_registry.register_service(service_name, endpoint)


def get_service_endpoint(service_name: str) -> Optional[ServiceEndpoint]:
    """Get service endpoint."""
    endpoints = service_registry.get_service_endpoints(service_name)
    return traffic_router.select_endpoint(service_name, endpoints)


def configure_canary_deployment(
    service_name: str,
    stable_weight: float,
    canary_weight: float
):
    """Configure canary deployment."""
    traffic_splitting.configure_split(service_name, {
        "stable": stable_weight,
        "canary": canary_weight
    })

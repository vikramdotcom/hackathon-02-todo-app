"""
Container Orchestration Utilities

Utilities for managing containerized applications.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContainerStatus(str, Enum):
    """Container status."""
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class Container:
    """Container entity."""

    def __init__(
        self,
        container_id: str,
        image: str,
        name: str,
        status: ContainerStatus = ContainerStatus.PENDING
    ):
        """Initialize container."""
        self.container_id = container_id
        self.image = image
        self.name = name
        self.status = status
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.ports: Dict[int, int] = {}
        self.environment: Dict[str, str] = {}
        self.labels: Dict[str, str] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "container_id": self.container_id,
            "image": self.image,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "ports": self.ports,
            "environment": self.environment,
            "labels": self.labels
        }


class Pod:
    """Kubernetes pod entity."""

    def __init__(
        self,
        pod_id: str,
        name: str,
        namespace: str = "default"
    ):
        """Initialize pod."""
        self.pod_id = pod_id
        self.name = name
        self.namespace = namespace
        self.containers: List[Container] = []
        self.status = ContainerStatus.PENDING
        self.node: Optional[str] = None
        self.created_at = datetime.utcnow()

    def add_container(self, container: Container):
        """Add container to pod."""
        self.containers.append(container)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pod_id": self.pod_id,
            "name": self.name,
            "namespace": self.namespace,
            "status": self.status.value,
            "node": self.node,
            "containers": [c.to_dict() for c in self.containers],
            "created_at": self.created_at.isoformat()
        }


class Deployment:
    """Kubernetes deployment entity."""

    def __init__(
        self,
        name: str,
        namespace: str,
        replicas: int = 1
    ):
        """Initialize deployment."""
        self.name = name
        self.namespace = namespace
        self.replicas = replicas
        self.pods: List[Pod] = []
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

    def scale(self, replicas: int):
        """Scale deployment."""
        self.replicas = replicas
        self.updated_at = datetime.utcnow()

        logger.info(
            f"Scaled deployment: {self.name}",
            extra={"deployment": self.name, "replicas": replicas}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "replicas": self.replicas,
            "pods": len(self.pods),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Service:
    """Kubernetes service entity."""

    def __init__(
        self,
        name: str,
        namespace: str,
        service_type: str = "ClusterIP"
    ):
        """Initialize service."""
        self.name = name
        self.namespace = namespace
        self.service_type = service_type
        self.ports: List[Dict[str, Any]] = []
        self.selector: Dict[str, str] = {}
        self.cluster_ip: Optional[str] = None

    def add_port(self, port: int, target_port: int, protocol: str = "TCP"):
        """Add port mapping."""
        self.ports.append({
            "port": port,
            "target_port": target_port,
            "protocol": protocol
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "type": self.service_type,
            "ports": self.ports,
            "selector": self.selector,
            "cluster_ip": self.cluster_ip
        }


class ContainerOrchestrator:
    """Container orchestration manager."""

    def __init__(self):
        """Initialize container orchestrator."""
        self.containers: Dict[str, Container] = {}
        self.pods: Dict[str, Pod] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.services: Dict[str, Service] = {}

    def create_container(
        self,
        image: str,
        name: str,
        environment: Optional[Dict[str, str]] = None,
        ports: Optional[Dict[int, int]] = None
    ) -> Container:
        """Create container."""
        import uuid
        container_id = str(uuid.uuid4())

        container = Container(container_id, image, name)

        if environment:
            container.environment = environment

        if ports:
            container.ports = ports

        self.containers[container_id] = container

        logger.info(
            f"Created container: {name}",
            extra={"container_id": container_id, "image": image}
        )

        return container

    def start_container(self, container_id: str):
        """Start container."""
        if container_id not in self.containers:
            raise ValueError(f"Container not found: {container_id}")

        container = self.containers[container_id]
        container.status = ContainerStatus.RUNNING
        container.started_at = datetime.utcnow()

        logger.info(f"Started container: {container.name}")

    def stop_container(self, container_id: str):
        """Stop container."""
        if container_id not in self.containers:
            raise ValueError(f"Container not found: {container_id}")

        container = self.containers[container_id]
        container.status = ContainerStatus.STOPPED
        container.stopped_at = datetime.utcnow()

        logger.info(f"Stopped container: {container.name}")

    def create_deployment(
        self,
        name: str,
        namespace: str,
        image: str,
        replicas: int = 1
    ) -> Deployment:
        """Create deployment."""
        deployment = Deployment(name, namespace, replicas)
        self.deployments[name] = deployment

        logger.info(
            f"Created deployment: {name}",
            extra={"deployment": name, "replicas": replicas}
        )

        return deployment

    def scale_deployment(self, name: str, replicas: int):
        """Scale deployment."""
        if name not in self.deployments:
            raise ValueError(f"Deployment not found: {name}")

        self.deployments[name].scale(replicas)

    def create_service(
        self,
        name: str,
        namespace: str,
        service_type: str = "ClusterIP"
    ) -> Service:
        """Create service."""
        service = Service(name, namespace, service_type)
        self.services[name] = service

        logger.info(f"Created service: {name}")

        return service

    def list_containers(self) -> List[Dict[str, Any]]:
        """List all containers."""
        return [c.to_dict() for c in self.containers.values()]

    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments."""
        return [d.to_dict() for d in self.deployments.values()]


class HealthChecker:
    """Health check for containers."""

    def __init__(self):
        """Initialize health checker."""
        self.health_checks: Dict[str, Dict[str, Any]] = {}

    def register_health_check(
        self,
        container_id: str,
        endpoint: str,
        interval_seconds: int = 30
    ):
        """Register health check."""
        self.health_checks[container_id] = {
            "endpoint": endpoint,
            "interval_seconds": interval_seconds,
            "last_check": None,
            "healthy": True
        }

    async def check_health(self, container_id: str) -> bool:
        """Check container health."""
        if container_id not in self.health_checks:
            return True

        # In production, make actual HTTP request to health endpoint
        health_check = self.health_checks[container_id]
        health_check["last_check"] = datetime.utcnow()

        return health_check["healthy"]


class ResourceQuota:
    """Resource quota management."""

    def __init__(self):
        """Initialize resource quota."""
        self.quotas: Dict[str, Dict[str, Any]] = {}

    def set_quota(
        self,
        namespace: str,
        cpu_limit: str,
        memory_limit: str,
        pod_limit: int
    ):
        """Set resource quota for namespace."""
        self.quotas[namespace] = {
            "cpu_limit": cpu_limit,
            "memory_limit": memory_limit,
            "pod_limit": pod_limit
        }

        logger.info(f"Set resource quota for namespace: {namespace}")

    def check_quota(self, namespace: str, resource: str, amount: float) -> bool:
        """Check if resource usage is within quota."""
        if namespace not in self.quotas:
            return True

        # In production, check actual resource usage
        return True


class AutoScaler:
    """Horizontal pod autoscaler."""

    def __init__(self, orchestrator: ContainerOrchestrator):
        """Initialize autoscaler."""
        self.orchestrator = orchestrator
        self.scaling_policies: Dict[str, Dict[str, Any]] = {}

    def configure_autoscaling(
        self,
        deployment_name: str,
        min_replicas: int,
        max_replicas: int,
        target_cpu_percent: int = 80
    ):
        """Configure autoscaling for deployment."""
        self.scaling_policies[deployment_name] = {
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "target_cpu_percent": target_cpu_percent
        }

        logger.info(
            f"Configured autoscaling for {deployment_name}",
            extra={
                "deployment": deployment_name,
                "min": min_replicas,
                "max": max_replicas
            }
        )

    async def evaluate_scaling(self, deployment_name: str, current_cpu_percent: int):
        """Evaluate if scaling is needed."""
        if deployment_name not in self.scaling_policies:
            return

        policy = self.scaling_policies[deployment_name]
        deployment = self.orchestrator.deployments.get(deployment_name)

        if not deployment:
            return

        current_replicas = deployment.replicas

        # Scale up if CPU usage is high
        if current_cpu_percent > policy["target_cpu_percent"]:
            new_replicas = min(current_replicas + 1, policy["max_replicas"])
            if new_replicas > current_replicas:
                self.orchestrator.scale_deployment(deployment_name, new_replicas)

        # Scale down if CPU usage is low
        elif current_cpu_percent < policy["target_cpu_percent"] * 0.5:
            new_replicas = max(current_replicas - 1, policy["min_replicas"])
            if new_replicas < current_replicas:
                self.orchestrator.scale_deployment(deployment_name, new_replicas)


class ConfigMapManager:
    """Manage configuration maps."""

    def __init__(self):
        """Initialize config map manager."""
        self.config_maps: Dict[str, Dict[str, str]] = {}

    def create_config_map(self, name: str, data: Dict[str, str]):
        """Create config map."""
        self.config_maps[name] = data
        logger.info(f"Created config map: {name}")

    def get_config_map(self, name: str) -> Optional[Dict[str, str]]:
        """Get config map."""
        return self.config_maps.get(name)

    def update_config_map(self, name: str, data: Dict[str, str]):
        """Update config map."""
        if name in self.config_maps:
            self.config_maps[name].update(data)
            logger.info(f"Updated config map: {name}")


class SecretManager:
    """Manage secrets."""

    def __init__(self):
        """Initialize secret manager."""
        self.secrets: Dict[str, Dict[str, str]] = {}

    def create_secret(self, name: str, data: Dict[str, str]):
        """Create secret."""
        # In production, encrypt secrets
        self.secrets[name] = data
        logger.info(f"Created secret: {name}")

    def get_secret(self, name: str) -> Optional[Dict[str, str]]:
        """Get secret."""
        return self.secrets.get(name)


class NetworkPolicy:
    """Network policy for pod communication."""

    def __init__(self):
        """Initialize network policy."""
        self.policies: List[Dict[str, Any]] = []

    def add_policy(
        self,
        name: str,
        pod_selector: Dict[str, str],
        ingress_rules: List[Dict[str, Any]]
    ):
        """Add network policy."""
        policy = {
            "name": name,
            "pod_selector": pod_selector,
            "ingress_rules": ingress_rules
        }

        self.policies.append(policy)
        logger.info(f"Added network policy: {name}")


# Global instances
container_orchestrator = ContainerOrchestrator()
health_checker = HealthChecker()
resource_quota = ResourceQuota()
auto_scaler = AutoScaler(container_orchestrator)
config_map_manager = ConfigMapManager()
secret_manager = SecretManager()
network_policy = NetworkPolicy()


# Helper functions
def create_container(
    image: str,
    name: str,
    environment: Optional[Dict[str, str]] = None
) -> Container:
    """Create container."""
    return container_orchestrator.create_container(image, name, environment)


def create_deployment(
    name: str,
    image: str,
    replicas: int = 1,
    namespace: str = "default"
) -> Deployment:
    """Create deployment."""
    return container_orchestrator.create_deployment(name, namespace, image, replicas)


def scale_deployment(name: str, replicas: int):
    """Scale deployment."""
    container_orchestrator.scale_deployment(name, replicas)

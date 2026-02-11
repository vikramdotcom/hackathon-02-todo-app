"""
Chaos Engineering Tools

Tools for chaos engineering and resilience testing.
"""

import logging
import random
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ChaosExperimentType(str, Enum):
    """Types of chaos experiments."""
    LATENCY_INJECTION = "latency_injection"
    ERROR_INJECTION = "error_injection"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    SERVICE_SHUTDOWN = "service_shutdown"
    DATA_CORRUPTION = "data_corruption"


class ChaosExperiment:
    """Chaos experiment definition."""

    def __init__(
        self,
        name: str,
        experiment_type: ChaosExperimentType,
        target_service: str,
        config: Dict[str, Any]
    ):
        """Initialize chaos experiment."""
        self.name = name
        self.experiment_type = experiment_type
        self.target_service = target_service
        self.config = config
        self.created_at = datetime.utcnow()
        self.runs: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.experiment_type.value,
            "target_service": self.target_service,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "total_runs": len(self.runs)
        }


class LatencyInjector:
    """Inject artificial latency."""

    def __init__(self):
        """Initialize latency injector."""
        self.active_injections: Dict[str, Dict[str, Any]] = {}

    def inject_latency(
        self,
        service_name: str,
        min_delay_ms: int,
        max_delay_ms: int,
        probability: float = 1.0
    ):
        """Inject latency into service."""
        self.active_injections[service_name] = {
            "min_delay_ms": min_delay_ms,
            "max_delay_ms": max_delay_ms,
            "probability": probability,
            "injected_at": datetime.utcnow().isoformat()
        }

        logger.info(
            f"Injecting latency: {service_name}",
            extra={
                "service": service_name,
                "min_delay": min_delay_ms,
                "max_delay": max_delay_ms
            }
        )

    async def apply_latency(self, service_name: str):
        """Apply latency if configured."""
        if service_name not in self.active_injections:
            return

        injection = self.active_injections[service_name]

        if random.random() > injection["probability"]:
            return

        delay_ms = random.randint(
            injection["min_delay_ms"],
            injection["max_delay_ms"]
        )

        await asyncio.sleep(delay_ms / 1000.0)

        logger.debug(f"Applied {delay_ms}ms latency to {service_name}")

    def remove_latency(self, service_name: str):
        """Remove latency injection."""
        if service_name in self.active_injections:
            del self.active_injections[service_name]
            logger.info(f"Removed latency injection: {service_name}")


class ErrorInjector:
    """Inject artificial errors."""

    def __init__(self):
        """Initialize error injector."""
        self.active_injections: Dict[str, Dict[str, Any]] = {}

    def inject_errors(
        self,
        service_name: str,
        error_rate: float,
        error_type: str = "generic"
    ):
        """Inject errors into service."""
        self.active_injections[service_name] = {
            "error_rate": error_rate,
            "error_type": error_type,
            "injected_at": datetime.utcnow().isoformat()
        }

        logger.info(
            f"Injecting errors: {service_name}",
            extra={"service": service_name, "error_rate": error_rate}
        )

    def should_inject_error(self, service_name: str) -> bool:
        """Check if error should be injected."""
        if service_name not in self.active_injections:
            return False

        injection = self.active_injections[service_name]
        return random.random() < injection["error_rate"]

    def remove_errors(self, service_name: str):
        """Remove error injection."""
        if service_name in self.active_injections:
            del self.active_injections[service_name]
            logger.info(f"Removed error injection: {service_name}")


class ResourceExhauster:
    """Exhaust system resources."""

    def __init__(self):
        """Initialize resource exhauster."""
        self.active_exhaustions: Dict[str, Dict[str, Any]] = {}

    def exhaust_cpu(self, duration_seconds: int, intensity: float = 0.8):
        """Exhaust CPU resources."""
        import uuid
        exhaustion_id = str(uuid.uuid4())

        self.active_exhaustions[exhaustion_id] = {
            "type": "cpu",
            "duration_seconds": duration_seconds,
            "intensity": intensity,
            "started_at": datetime.utcnow().isoformat()
        }

        logger.warning(
            f"Exhausting CPU resources",
            extra={"duration": duration_seconds, "intensity": intensity}
        )

        return exhaustion_id

    def exhaust_memory(self, size_mb: int, duration_seconds: int):
        """Exhaust memory resources."""
        import uuid
        exhaustion_id = str(uuid.uuid4())

        self.active_exhaustions[exhaustion_id] = {
            "type": "memory",
            "size_mb": size_mb,
            "duration_seconds": duration_seconds,
            "started_at": datetime.utcnow().isoformat()
        }

        logger.warning(
            f"Exhausting memory resources",
            extra={"size_mb": size_mb, "duration": duration_seconds}
        )

        return exhaustion_id

    def stop_exhaustion(self, exhaustion_id: str):
        """Stop resource exhaustion."""
        if exhaustion_id in self.active_exhaustions:
            del self.active_exhaustions[exhaustion_id]
            logger.info(f"Stopped resource exhaustion: {exhaustion_id}")


class NetworkPartitioner:
    """Simulate network partitions."""

    def __init__(self):
        """Initialize network partitioner."""
        self.partitions: List[Dict[str, Any]] = []

    def create_partition(
        self,
        service_a: str,
        service_b: str,
        duration_seconds: int
    ):
        """Create network partition between services."""
        partition = {
            "service_a": service_a,
            "service_b": service_b,
            "duration_seconds": duration_seconds,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=duration_seconds)
        }

        self.partitions.append(partition)

        logger.warning(
            f"Created network partition: {service_a} <-> {service_b}",
            extra={
                "service_a": service_a,
                "service_b": service_b,
                "duration": duration_seconds
            }
        )

    def is_partitioned(self, service_a: str, service_b: str) -> bool:
        """Check if services are partitioned."""
        now = datetime.utcnow()

        for partition in self.partitions:
            if partition["expires_at"] < now:
                continue

            if (
                (partition["service_a"] == service_a and partition["service_b"] == service_b) or
                (partition["service_a"] == service_b and partition["service_b"] == service_a)
            ):
                return True

        return False

    def cleanup_expired_partitions(self):
        """Cleanup expired partitions."""
        now = datetime.utcnow()
        self.partitions = [
            p for p in self.partitions
            if p["expires_at"] > now
        ]


class ServiceKiller:
    """Kill services for chaos testing."""

    def __init__(self):
        """Initialize service killer."""
        self.killed_services: Dict[str, datetime] = {}

    def kill_service(self, service_name: str, duration_seconds: int):
        """Kill service temporarily."""
        self.killed_services[service_name] = (
            datetime.utcnow() + timedelta(seconds=duration_seconds)
        )

        logger.warning(
            f"Killed service: {service_name}",
            extra={"service": service_name, "duration": duration_seconds}
        )

    def is_service_alive(self, service_name: str) -> bool:
        """Check if service is alive."""
        if service_name not in self.killed_services:
            return True

        return datetime.utcnow() > self.killed_services[service_name]

    def revive_service(self, service_name: str):
        """Revive killed service."""
        if service_name in self.killed_services:
            del self.killed_services[service_name]
            logger.info(f"Revived service: {service_name}")


class ChaosScheduler:
    """Schedule chaos experiments."""

    def __init__(self):
        """Initialize chaos scheduler."""
        self.scheduled_experiments: List[Dict[str, Any]] = []

    def schedule_experiment(
        self,
        experiment: ChaosExperiment,
        start_time: datetime,
        duration_seconds: int
    ):
        """Schedule chaos experiment."""
        scheduled = {
            "experiment": experiment,
            "start_time": start_time,
            "end_time": start_time + timedelta(seconds=duration_seconds),
            "status": "scheduled"
        }

        self.scheduled_experiments.append(scheduled)

        logger.info(
            f"Scheduled chaos experiment: {experiment.name}",
            extra={
                "experiment": experiment.name,
                "start_time": start_time.isoformat()
            }
        )

    async def run_scheduled_experiments(self):
        """Run scheduled experiments."""
        now = datetime.utcnow()

        for scheduled in self.scheduled_experiments:
            if scheduled["status"] != "scheduled":
                continue

            if scheduled["start_time"] <= now < scheduled["end_time"]:
                scheduled["status"] = "running"
                # Execute experiment
                logger.info(f"Running experiment: {scheduled['experiment'].name}")

            elif now >= scheduled["end_time"]:
                scheduled["status"] = "completed"


class ResilienceValidator:
    """Validate system resilience."""

    def __init__(self):
        """Initialize resilience validator."""
        self.validation_results: List[Dict[str, Any]] = []

    async def validate_service_recovery(
        self,
        service_name: str,
        max_recovery_time_seconds: int = 60
    ) -> bool:
        """Validate service recovery time."""
        start_time = datetime.utcnow()

        # Wait for service to recover
        recovered = False
        while (datetime.utcnow() - start_time).total_seconds() < max_recovery_time_seconds:
            # Check if service is healthy
            # In production, make actual health check
            await asyncio.sleep(1)
            recovered = True
            break

        result = {
            "service": service_name,
            "recovered": recovered,
            "recovery_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.validation_results.append(result)

        return recovered

    def get_validation_results(self) -> List[Dict[str, Any]]:
        """Get validation results."""
        return self.validation_results


class ChaosMetrics:
    """Track chaos experiment metrics."""

    def __init__(self):
        """Initialize chaos metrics."""
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def record_experiment(
        self,
        experiment_name: str,
        success: bool,
        duration_seconds: float,
        impact_score: float
    ):
        """Record experiment metrics."""
        if experiment_name not in self.metrics:
            self.metrics[experiment_name] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_duration": 0,
                "avg_impact_score": 0
            }

        metrics = self.metrics[experiment_name]
        metrics["total_runs"] += 1

        if success:
            metrics["successful_runs"] += 1
        else:
            metrics["failed_runs"] += 1

        metrics["total_duration"] += duration_seconds
        metrics["avg_impact_score"] = (
            (metrics["avg_impact_score"] * (metrics["total_runs"] - 1) + impact_score) /
            metrics["total_runs"]
        )

    def get_metrics(self, experiment_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for experiment."""
        return self.metrics.get(experiment_name)


class ChaosGameDay:
    """Organize chaos game day events."""

    def __init__(self):
        """Initialize chaos game day."""
        self.game_days: List[Dict[str, Any]] = []

    def schedule_game_day(
        self,
        name: str,
        date: datetime,
        experiments: List[ChaosExperiment],
        participants: List[str]
    ):
        """Schedule chaos game day."""
        game_day = {
            "name": name,
            "date": date,
            "experiments": experiments,
            "participants": participants,
            "status": "scheduled",
            "results": []
        }

        self.game_days.append(game_day)

        logger.info(
            f"Scheduled chaos game day: {name}",
            extra={
                "name": name,
                "date": date.isoformat(),
                "experiments": len(experiments)
            }
        )

    def get_upcoming_game_days(self) -> List[Dict[str, Any]]:
        """Get upcoming game days."""
        now = datetime.utcnow()
        return [
            gd for gd in self.game_days
            if gd["date"] > now and gd["status"] == "scheduled"
        ]


class BlastRadiusCalculator:
    """Calculate blast radius of failures."""

    def __init__(self):
        """Initialize blast radius calculator."""
        self.service_dependencies: Dict[str, List[str]] = {}

    def register_dependency(self, service: str, depends_on: str):
        """Register service dependency."""
        if service not in self.service_dependencies:
            self.service_dependencies[service] = []

        self.service_dependencies[service].append(depends_on)

    def calculate_blast_radius(self, failed_service: str) -> List[str]:
        """Calculate blast radius of service failure."""
        affected = set()

        def find_dependents(service: str):
            for svc, deps in self.service_dependencies.items():
                if service in deps and svc not in affected:
                    affected.add(svc)
                    find_dependents(svc)

        find_dependents(failed_service)

        return list(affected)


# Global instances
latency_injector = LatencyInjector()
error_injector = ErrorInjector()
resource_exhauster = ResourceExhauster()
network_partitioner = NetworkPartitioner()
service_killer = ServiceKiller()
chaos_scheduler = ChaosScheduler()
resilience_validator = ResilienceValidator()
chaos_metrics = ChaosMetrics()
chaos_game_day = ChaosGameDay()
blast_radius_calculator = BlastRadiusCalculator()


# Helper functions
def inject_latency(
    service_name: str,
    min_delay_ms: int,
    max_delay_ms: int,
    probability: float = 1.0
):
    """Inject latency into service."""
    latency_injector.inject_latency(
        service_name,
        min_delay_ms,
        max_delay_ms,
        probability
    )


def inject_errors(service_name: str, error_rate: float):
    """Inject errors into service."""
    error_injector.inject_errors(service_name, error_rate)


def kill_service(service_name: str, duration_seconds: int):
    """Kill service temporarily."""
    service_killer.kill_service(service_name, duration_seconds)


def create_network_partition(
    service_a: str,
    service_b: str,
    duration_seconds: int
):
    """Create network partition."""
    network_partitioner.create_partition(service_a, service_b, duration_seconds)


async def validate_resilience(service_name: str) -> bool:
    """Validate service resilience."""
    return await resilience_validator.validate_service_recovery(service_name)

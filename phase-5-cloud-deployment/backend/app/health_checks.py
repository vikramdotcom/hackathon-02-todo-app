"""
Health Check System

Comprehensive health checks for all system components.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status types."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check."""

    def __init__(self, name: str, check_func, timeout: int = 5):
        """Initialize health check."""
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_check: Optional[datetime] = None
        self.last_status: Optional[HealthStatus] = None
        self.last_error: Optional[str] = None

    async def run(self) -> Dict[str, Any]:
        """Run health check."""
        try:
            result = await asyncio.wait_for(
                self.check_func(),
                timeout=self.timeout
            )

            self.last_check = datetime.utcnow()
            self.last_status = HealthStatus.HEALTHY
            self.last_error = None

            return {
                "name": self.name,
                "status": HealthStatus.HEALTHY,
                "timestamp": self.last_check.isoformat(),
                "details": result
            }

        except asyncio.TimeoutError:
            self.last_check = datetime.utcnow()
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = f"Timeout after {self.timeout}s"

            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY,
                "timestamp": self.last_check.isoformat(),
                "error": self.last_error
            }

        except Exception as e:
            self.last_check = datetime.utcnow()
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = str(e)

            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY,
                "timestamp": self.last_check.isoformat(),
                "error": self.last_error
            }


class HealthCheckRegistry:
    """Registry for health checks."""

    def __init__(self):
        """Initialize registry."""
        self.checks: Dict[str, HealthCheck] = {}

    def register(self, check: HealthCheck):
        """Register health check."""
        self.checks[check.name] = check
        logger.info(f"Registered health check: {check.name}")

    def unregister(self, name: str):
        """Unregister health check."""
        if name in self.checks:
            del self.checks[name]
            logger.info(f"Unregistered health check: {name}")

    async def run_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = await asyncio.gather(
            *[check.run() for check in self.checks.values()],
            return_exceptions=True
        )

        check_results = []
        overall_status = HealthStatus.HEALTHY

        for result in results:
            if isinstance(result, Exception):
                check_results.append({
                    "name": "unknown",
                    "status": HealthStatus.UNHEALTHY,
                    "error": str(result)
                })
                overall_status = HealthStatus.UNHEALTHY
            else:
                check_results.append(result)
                if result["status"] == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result["status"] == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": check_results
        }

    async def run_check(self, name: str) -> Optional[Dict[str, Any]]:
        """Run specific health check."""
        check = self.checks.get(name)
        if check:
            return await check.run()
        return None


# Global registry
health_registry = HealthCheckRegistry()


# Health check implementations
async def check_database():
    """Check database connectivity."""
    # Simulate database check
    await asyncio.sleep(0.1)
    return {"connected": True, "pool_size": 10}


async def check_redis():
    """Check Redis connectivity."""
    # Simulate Redis check
    await asyncio.sleep(0.1)
    return {"connected": True, "ping": "pong"}


async def check_kafka():
    """Check Kafka connectivity."""
    # Simulate Kafka check
    await asyncio.sleep(0.1)
    return {"connected": True, "brokers": 1}


async def check_disk_space():
    """Check disk space."""
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_percent = (free / total) * 100

    return {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
        "free_percent": round(free_percent, 2)
    }


async def check_memory():
    """Check memory usage."""
    import psutil
    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
        "percent_used": memory.percent
    }


# Register default checks
health_registry.register(HealthCheck("database", check_database))
health_registry.register(HealthCheck("redis", check_redis))
health_registry.register(HealthCheck("kafka", check_kafka))
health_registry.register(HealthCheck("disk", check_disk_space))
health_registry.register(HealthCheck("memory", check_memory))

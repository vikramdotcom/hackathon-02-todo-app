"""
Health Check Utilities

Provides health check functions for various system components.
"""

import logging
from typing import Dict, Any
from sqlmodel import Session, text
from app.database import get_db_context

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check utilities for system components."""

    @staticmethod
    def check_database() -> Dict[str, Any]:
        """
        Check database connectivity and health.

        Returns:
            Dict with status and details
        """
        try:
            with get_db_context() as db:
                # Execute simple query
                result = db.exec(text("SELECT 1")).first()

                if result:
                    return {
                        "status": "healthy",
                        "message": "Database connection successful",
                        "details": {
                            "connected": True,
                            "query_successful": True
                        }
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": "Database query failed",
                        "details": {
                            "connected": True,
                            "query_successful": False
                        }
                    }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "details": {
                    "connected": False,
                    "error": str(e)
                }
            }

    @staticmethod
    def check_disk_space() -> Dict[str, Any]:
        """
        Check available disk space.

        Returns:
            Dict with status and details
        """
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")

            # Convert to GB
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            free_gb = free / (1024 ** 3)
            usage_percent = (used / total) * 100

            # Consider unhealthy if less than 10% free space
            status = "healthy" if usage_percent < 90 else "unhealthy"

            return {
                "status": status,
                "message": f"Disk usage: {usage_percent:.1f}%",
                "details": {
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "usage_percent": round(usage_percent, 2)
                }
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Disk space check failed: {str(e)}",
                "details": {"error": str(e)}
            }

    @staticmethod
    def check_memory() -> Dict[str, Any]:
        """
        Check memory usage.

        Returns:
            Dict with status and details
        """
        try:
            import psutil

            memory = psutil.virtual_memory()

            # Consider unhealthy if more than 90% used
            status = "healthy" if memory.percent < 90 else "unhealthy"

            return {
                "status": status,
                "message": f"Memory usage: {memory.percent}%",
                "details": {
                    "total_gb": round(memory.total / (1024 ** 3), 2),
                    "available_gb": round(memory.available / (1024 ** 3), 2),
                    "used_gb": round(memory.used / (1024 ** 3), 2),
                    "usage_percent": memory.percent
                }
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not installed",
                "details": {"error": "psutil package required"}
            }
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Memory check failed: {str(e)}",
                "details": {"error": str(e)}
            }

    @staticmethod
    def check_all() -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Dict with overall status and component details
        """
        checks = {
            "database": HealthChecker.check_database(),
            "disk": HealthChecker.check_disk_space(),
            "memory": HealthChecker.check_memory()
        }

        # Determine overall status
        statuses = [check["status"] for check in checks.values()]

        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "timestamp": None,  # Will be set by caller
            "checks": checks
        }

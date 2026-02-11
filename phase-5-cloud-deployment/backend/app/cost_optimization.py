"""
Cost Optimization and Resource Management

Monitor and optimize cloud resource costs.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Cloud resource types."""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SERVERLESS = "serverless"


class CostMetric:
    """Cost metric for a resource."""

    def __init__(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cost: float,
        currency: str = "USD"
    ):
        """Initialize cost metric."""
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.cost = cost
        self.currency = currency
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "cost": self.cost,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat()
        }


class CostTracker:
    """Track cloud resource costs."""

    def __init__(self):
        """Initialize cost tracker."""
        self.metrics: List[CostMetric] = []
        self.budgets: Dict[str, float] = {}

    def record_cost(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cost: float
    ):
        """Record resource cost."""
        metric = CostMetric(resource_id, resource_type, cost)
        self.metrics.append(metric)

        logger.info(
            f"Recorded cost: {resource_id}",
            extra={
                "resource": resource_id,
                "type": resource_type.value,
                "cost": cost
            }
        )

    def set_budget(self, category: str, amount: float):
        """Set budget for category."""
        self.budgets[category] = amount
        logger.info(f"Set budget for {category}: ${amount}")

    def get_total_cost(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """Get total cost for period."""
        total = 0.0

        for metric in self.metrics:
            if start_date and metric.timestamp < start_date:
                continue
            if end_date and metric.timestamp > end_date:
                continue

            total += metric.cost

        return total

    def get_cost_by_type(
        self,
        resource_type: ResourceType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """Get cost by resource type."""
        total = 0.0

        for metric in self.metrics:
            if metric.resource_type != resource_type:
                continue

            if start_date and metric.timestamp < start_date:
                continue
            if end_date and metric.timestamp > end_date:
                continue

            total += metric.cost

        return total

    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by resource type."""
        breakdown = {}

        for resource_type in ResourceType:
            cost = self.get_cost_by_type(resource_type)
            if cost > 0:
                breakdown[resource_type.value] = cost

        return breakdown

    def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Check for budget alerts."""
        alerts = []

        for category, budget in self.budgets.items():
            # Get current month costs
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            current_cost = self.get_total_cost(start_date=start_of_month)

            if current_cost > budget * 0.8:  # 80% threshold
                alerts.append({
                    "category": category,
                    "budget": budget,
                    "current_cost": current_cost,
                    "percentage": (current_cost / budget) * 100,
                    "severity": "high" if current_cost > budget else "medium"
                })

        return alerts


class ResourceOptimizer:
    """Optimize resource usage and costs."""

    def __init__(self):
        """Initialize resource optimizer."""
        self.recommendations: List[Dict[str, Any]] = []

    def analyze_idle_resources(
        self,
        resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze idle resources."""
        idle_resources = []

        for resource in resources:
            utilization = resource.get("utilization", 0)

            if utilization < 10:  # Less than 10% utilization
                idle_resources.append({
                    "resource_id": resource["id"],
                    "type": resource["type"],
                    "utilization": utilization,
                    "recommendation": "Consider terminating or downsizing",
                    "potential_savings": resource.get("cost", 0) * 0.9
                })

        return idle_resources

    def analyze_oversized_resources(
        self,
        resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze oversized resources."""
        oversized = []

        for resource in resources:
            utilization = resource.get("utilization", 0)
            size = resource.get("size", "")

            if utilization < 50 and "large" in size.lower():
                oversized.append({
                    "resource_id": resource["id"],
                    "type": resource["type"],
                    "current_size": size,
                    "utilization": utilization,
                    "recommendation": "Downsize to smaller instance",
                    "potential_savings": resource.get("cost", 0) * 0.5
                })

        return oversized

    def recommend_reserved_instances(
        self,
        resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recommend reserved instances."""
        recommendations = []

        for resource in resources:
            if resource.get("type") == "compute":
                uptime_days = resource.get("uptime_days", 0)

                if uptime_days > 300:  # Running for most of the year
                    recommendations.append({
                        "resource_id": resource["id"],
                        "recommendation": "Convert to reserved instance",
                        "potential_savings": resource.get("cost", 0) * 0.3,
                        "commitment": "1 year"
                    })

        return recommendations

    def generate_optimization_report(
        self,
        resources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate optimization report."""
        idle = self.analyze_idle_resources(resources)
        oversized = self.analyze_oversized_resources(resources)
        reserved = self.recommend_reserved_instances(resources)

        total_potential_savings = (
            sum(r["potential_savings"] for r in idle) +
            sum(r["potential_savings"] for r in oversized) +
            sum(r["potential_savings"] for r in reserved)
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_resources": len(resources),
            "idle_resources": len(idle),
            "oversized_resources": len(oversized),
            "reserved_instance_opportunities": len(reserved),
            "total_potential_savings": total_potential_savings,
            "recommendations": {
                "idle": idle,
                "oversized": oversized,
                "reserved_instances": reserved
            }
        }


class RightSizingAnalyzer:
    """Analyze and recommend right-sizing."""

    def __init__(self):
        """Initialize right-sizing analyzer."""
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}

    def record_metrics(
        self,
        resource_id: str,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float
    ):
        """Record resource metrics."""
        if resource_id not in self.metrics:
            self.metrics[resource_id] = []

        self.metrics[resource_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage
        })

    def analyze_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Analyze resource for right-sizing."""
        if resource_id not in self.metrics or not self.metrics[resource_id]:
            return None

        metrics = self.metrics[resource_id]

        # Calculate averages
        avg_cpu = sum(m["cpu_usage"] for m in metrics) / len(metrics)
        avg_memory = sum(m["memory_usage"] for m in metrics) / len(metrics)
        avg_disk = sum(m["disk_usage"] for m in metrics) / len(metrics)

        # Determine recommendation
        recommendation = "current_size"

        if avg_cpu < 20 and avg_memory < 20:
            recommendation = "downsize"
        elif avg_cpu > 80 or avg_memory > 80:
            recommendation = "upsize"

        return {
            "resource_id": resource_id,
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory,
            "avg_disk_usage": avg_disk,
            "recommendation": recommendation,
            "confidence": "high" if len(metrics) > 100 else "medium"
        }


class SpotInstanceManager:
    """Manage spot instances for cost savings."""

    def __init__(self):
        """Initialize spot instance manager."""
        self.spot_instances: Dict[str, Dict[str, Any]] = {}

    def request_spot_instance(
        self,
        instance_type: str,
        max_price: float,
        availability_zone: str
    ) -> str:
        """Request spot instance."""
        import uuid
        request_id = str(uuid.uuid4())

        self.spot_instances[request_id] = {
            "instance_type": instance_type,
            "max_price": max_price,
            "availability_zone": availability_zone,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(
            f"Requested spot instance: {instance_type}",
            extra={
                "request_id": request_id,
                "instance_type": instance_type,
                "max_price": max_price
            }
        )

        return request_id

    def get_spot_price_history(
        self,
        instance_type: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get spot price history."""
        # In production, fetch from cloud provider API
        return []

    def calculate_savings(
        self,
        on_demand_price: float,
        spot_price: float,
        hours: int
    ) -> float:
        """Calculate spot instance savings."""
        on_demand_cost = on_demand_price * hours
        spot_cost = spot_price * hours
        return on_demand_cost - spot_cost


class StorageOptimizer:
    """Optimize storage costs."""

    def __init__(self):
        """Initialize storage optimizer."""
        pass

    def analyze_storage_tiers(
        self,
        storage_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze storage tier optimization."""
        recommendations = []

        for obj in storage_objects:
            last_accessed = datetime.fromisoformat(obj.get("last_accessed", datetime.utcnow().isoformat()))
            days_since_access = (datetime.utcnow() - last_accessed).days

            if days_since_access > 90:
                recommendations.append({
                    "object_id": obj["id"],
                    "current_tier": obj.get("tier", "standard"),
                    "recommended_tier": "glacier",
                    "days_since_access": days_since_access,
                    "potential_savings": obj.get("size_gb", 0) * 0.004 * 12  # Monthly savings
                })
            elif days_since_access > 30:
                recommendations.append({
                    "object_id": obj["id"],
                    "current_tier": obj.get("tier", "standard"),
                    "recommended_tier": "infrequent_access",
                    "days_since_access": days_since_access,
                    "potential_savings": obj.get("size_gb", 0) * 0.01 * 12
                })

        return recommendations

    def identify_duplicate_data(
        self,
        storage_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify duplicate data."""
        checksums = {}
        duplicates = []

        for obj in storage_objects:
            checksum = obj.get("checksum")
            if not checksum:
                continue

            if checksum in checksums:
                duplicates.append({
                    "object_id": obj["id"],
                    "duplicate_of": checksums[checksum],
                    "size_gb": obj.get("size_gb", 0),
                    "potential_savings": obj.get("size_gb", 0) * 0.023 * 12
                })
            else:
                checksums[checksum] = obj["id"]

        return duplicates


class CostAnomalyDetector:
    """Detect cost anomalies."""

    def __init__(self):
        """Initialize cost anomaly detector."""
        self.baseline_costs: Dict[str, float] = {}

    def set_baseline(self, category: str, cost: float):
        """Set baseline cost."""
        self.baseline_costs[category] = cost

    def detect_anomalies(
        self,
        current_costs: Dict[str, float],
        threshold_percent: float = 50
    ) -> List[Dict[str, Any]]:
        """Detect cost anomalies."""
        anomalies = []

        for category, current_cost in current_costs.items():
            if category not in self.baseline_costs:
                continue

            baseline = self.baseline_costs[category]
            if baseline == 0:
                continue

            percent_change = ((current_cost - baseline) / baseline) * 100

            if abs(percent_change) > threshold_percent:
                anomalies.append({
                    "category": category,
                    "baseline_cost": baseline,
                    "current_cost": current_cost,
                    "percent_change": percent_change,
                    "severity": "high" if abs(percent_change) > 100 else "medium"
                })

        return anomalies


# Global instances
cost_tracker = CostTracker()
resource_optimizer = ResourceOptimizer()
right_sizing_analyzer = RightSizingAnalyzer()
spot_instance_manager = SpotInstanceManager()
storage_optimizer = StorageOptimizer()
cost_anomaly_detector = CostAnomalyDetector()


# Helper functions
def record_cost(resource_id: str, resource_type: ResourceType, cost: float):
    """Record resource cost."""
    cost_tracker.record_cost(resource_id, resource_type, cost)


def get_cost_breakdown() -> Dict[str, float]:
    """Get cost breakdown."""
    return cost_tracker.get_cost_breakdown()


def generate_optimization_report(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate optimization report."""
    return resource_optimizer.generate_optimization_report(resources)


def check_budget_alerts() -> List[Dict[str, Any]]:
    """Check budget alerts."""
    return cost_tracker.check_budget_alerts()

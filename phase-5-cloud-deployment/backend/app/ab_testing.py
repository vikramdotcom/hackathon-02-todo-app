"""
A/B Testing Framework

Manage experiments, variants, and statistical analysis.
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import random

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class Variant:
    """Experiment variant."""

    def __init__(
        self,
        name: str,
        weight: float,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize variant."""
        self.name = name
        self.weight = weight
        self.config = config or {}
        self.impressions = 0
        self.conversions = 0

    def record_impression(self):
        """Record impression."""
        self.impressions += 1

    def record_conversion(self):
        """Record conversion."""
        self.conversions += 1

    def get_conversion_rate(self) -> float:
        """Get conversion rate."""
        if self.impressions == 0:
            return 0.0
        return self.conversions / self.impressions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "weight": self.weight,
            "config": self.config,
            "impressions": self.impressions,
            "conversions": self.conversions,
            "conversion_rate": self.get_conversion_rate()
        }


class Experiment:
    """A/B test experiment."""

    def __init__(
        self,
        name: str,
        description: str,
        variants: List[Variant],
        status: ExperimentStatus = ExperimentStatus.DRAFT
    ):
        """Initialize experiment."""
        self.name = name
        self.description = description
        self.variants = {v.name: v for v in variants}
        self.status = status
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Validate weights sum to 1.0
        total_weight = sum(v.weight for v in variants)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Variant weights must sum to 1.0, got {total_weight}")

    def start(self):
        """Start experiment."""
        self.status = ExperimentStatus.RUNNING
        self.started_at = datetime.utcnow()
        logger.info(f"Started experiment: {self.name}")

    def pause(self):
        """Pause experiment."""
        self.status = ExperimentStatus.PAUSED
        logger.info(f"Paused experiment: {self.name}")

    def complete(self):
        """Complete experiment."""
        self.status = ExperimentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        logger.info(f"Completed experiment: {self.name}")

    def assign_variant(self, user_id: int) -> Variant:
        """Assign variant to user."""
        # Use consistent hashing for stable assignment
        hash_input = f"{self.name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        random_value = (hash_value % 10000) / 10000.0

        # Select variant based on weights
        cumulative_weight = 0.0
        for variant in self.variants.values():
            cumulative_weight += variant.weight
            if random_value <= cumulative_weight:
                return variant

        # Fallback to first variant
        return list(self.variants.values())[0]

    def record_impression(self, variant_name: str):
        """Record impression for variant."""
        if variant_name in self.variants:
            self.variants[variant_name].record_impression()

    def record_conversion(self, variant_name: str):
        """Record conversion for variant."""
        if variant_name in self.variants:
            self.variants[variant_name].record_conversion()

    def get_results(self) -> Dict[str, Any]:
        """Get experiment results."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "variants": [v.to_dict() for v in self.variants.values()],
            "winner": self.get_winner()
        }

    def get_winner(self) -> Optional[str]:
        """Get winning variant."""
        if self.status != ExperimentStatus.COMPLETED:
            return None

        # Simple winner selection based on conversion rate
        best_variant = max(
            self.variants.values(),
            key=lambda v: v.get_conversion_rate()
        )

        return best_variant.name if best_variant.impressions > 0 else None

    def calculate_statistical_significance(self) -> Dict[str, float]:
        """Calculate statistical significance between variants."""
        # Simplified chi-square test
        # In production, use proper statistical libraries
        results = {}

        variants_list = list(self.variants.values())
        if len(variants_list) < 2:
            return results

        control = variants_list[0]
        for variant in variants_list[1:]:
            # Calculate z-score
            p1 = control.get_conversion_rate()
            p2 = variant.get_conversion_rate()
            n1 = control.impressions
            n2 = variant.impressions

            if n1 == 0 or n2 == 0:
                results[f"{control.name}_vs_{variant.name}"] = 0.0
                continue

            p_pool = (control.conversions + variant.conversions) / (n1 + n2)
            se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5

            if se == 0:
                results[f"{control.name}_vs_{variant.name}"] = 0.0
            else:
                z_score = abs(p1 - p2) / se
                results[f"{control.name}_vs_{variant.name}"] = z_score

        return results


class ABTestManager:
    """Manage A/B tests."""

    def __init__(self):
        """Initialize A/B test manager."""
        self.experiments: Dict[str, Experiment] = {}
        self.user_assignments: Dict[int, Dict[str, str]] = {}

    def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[Variant]
    ) -> Experiment:
        """Create experiment."""
        experiment = Experiment(name, description, variants)
        self.experiments[name] = experiment

        logger.info(
            f"Created experiment: {name}",
            extra={"experiment": name, "variants": len(variants)}
        )

        return experiment

    def get_experiment(self, name: str) -> Optional[Experiment]:
        """Get experiment."""
        return self.experiments.get(name)

    def start_experiment(self, name: str):
        """Start experiment."""
        if name in self.experiments:
            self.experiments[name].start()

    def pause_experiment(self, name: str):
        """Pause experiment."""
        if name in self.experiments:
            self.experiments[name].pause()

    def complete_experiment(self, name: str):
        """Complete experiment."""
        if name in self.experiments:
            self.experiments[name].complete()

    def get_variant(self, experiment_name: str, user_id: int) -> Optional[Variant]:
        """Get variant for user."""
        experiment = self.experiments.get(experiment_name)

        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None

        # Check if user already assigned
        if user_id in self.user_assignments:
            if experiment_name in self.user_assignments[user_id]:
                variant_name = self.user_assignments[user_id][experiment_name]
                return experiment.variants.get(variant_name)

        # Assign new variant
        variant = experiment.assign_variant(user_id)

        # Store assignment
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        self.user_assignments[user_id][experiment_name] = variant.name

        # Record impression
        experiment.record_impression(variant.name)

        logger.info(
            f"Assigned variant: {variant.name}",
            extra={
                "experiment": experiment_name,
                "user_id": user_id,
                "variant": variant.name
            }
        )

        return variant

    def track_conversion(self, experiment_name: str, user_id: int):
        """Track conversion for user."""
        experiment = self.experiments.get(experiment_name)

        if not experiment:
            return

        # Get user's assigned variant
        if user_id in self.user_assignments:
            if experiment_name in self.user_assignments[user_id]:
                variant_name = self.user_assignments[user_id][experiment_name]
                experiment.record_conversion(variant_name)

                logger.info(
                    f"Tracked conversion",
                    extra={
                        "experiment": experiment_name,
                        "user_id": user_id,
                        "variant": variant_name
                    }
                )

    def get_results(self, experiment_name: str) -> Optional[Dict[str, Any]]:
        """Get experiment results."""
        experiment = self.experiments.get(experiment_name)
        return experiment.get_results() if experiment else None

    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments."""
        return [
            {
                "name": exp.name,
                "description": exp.description,
                "status": exp.status.value,
                "variants": len(exp.variants)
            }
            for exp in self.experiments.values()
        ]


# Global A/B test manager
ab_test_manager = ABTestManager()


# Helper functions
def create_ab_test(
    name: str,
    description: str,
    control_config: Dict[str, Any],
    treatment_config: Dict[str, Any],
    split: float = 0.5
) -> Experiment:
    """Create simple A/B test."""
    variants = [
        Variant("control", 1 - split, control_config),
        Variant("treatment", split, treatment_config)
    ]

    return ab_test_manager.create_experiment(name, description, variants)


def get_variant_for_user(experiment_name: str, user_id: int) -> Optional[Dict[str, Any]]:
    """Get variant config for user."""
    variant = ab_test_manager.get_variant(experiment_name, user_id)
    return variant.config if variant else None


def track_conversion(experiment_name: str, user_id: int):
    """Track conversion."""
    ab_test_manager.track_conversion(experiment_name, user_id)

"""
Feature Flag System

Control feature rollout with dynamic flags.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FeatureFlagStatus(str, Enum):
    """Feature flag status."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    CONDITIONAL = "conditional"


class FeatureFlag:
    """Feature flag entity."""

    def __init__(
        self,
        name: str,
        status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
        description: str = ""
    ):
        """Initialize feature flag."""
        self.name = name
        self.status = status
        self.description = description
        self.rollout_percentage = 0.0
        self.user_whitelist: List[str] = []
        self.user_blacklist: List[str] = []
        self.conditions: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

    def is_enabled_for_user(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if flag is enabled for user."""
        if self.status == FeatureFlagStatus.DISABLED:
            return False

        if self.status == FeatureFlagStatus.ENABLED:
            return True

        # Check blacklist
        if user_id in self.user_blacklist:
            return False

        # Check whitelist
        if user_id in self.user_whitelist:
            return True

        # Check rollout percentage
        if self.rollout_percentage > 0:
            user_hash = hash(user_id) % 100
            if user_hash < self.rollout_percentage:
                return True

        # Check conditions
        if context and self.conditions:
            return self._evaluate_conditions(context)

        return False

    def _evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate conditions."""
        for key, value in self.conditions.items():
            if key not in context or context[key] != value:
                return False
        return True


class FeatureFlagManager:
    """Manage feature flags."""

    def __init__(self):
        """Initialize feature flag manager."""
        self.flags: Dict[str, FeatureFlag] = {}

    def create_flag(
        self,
        name: str,
        status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
        description: str = ""
    ) -> FeatureFlag:
        """Create feature flag."""
        flag = FeatureFlag(name, status, description)
        self.flags[name] = flag
        logger.info(f"Feature flag created: {name}")
        return flag

    def is_enabled(
        self,
        flag_name: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if feature is enabled."""
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]
        return flag.is_enabled_for_user(user_id, context)

    def set_rollout_percentage(self, flag_name: str, percentage: float):
        """Set rollout percentage."""
        if flag_name in self.flags:
            self.flags[flag_name].rollout_percentage = percentage
            logger.info(f"Rollout percentage set: {flag_name} = {percentage}%")


# Global instance
feature_flag_manager = FeatureFlagManager()

"""
Feature Flags System

Provides feature flag management for gradual rollouts and A/B testing.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class FeatureFlagStrategy(str, Enum):
    """Feature flag evaluation strategies."""

    BOOLEAN = "boolean"  # Simple on/off
    PERCENTAGE = "percentage"  # Percentage rollout
    USER_LIST = "user_list"  # Specific user IDs
    ATTRIBUTE = "attribute"  # Based on user attributes


class FeatureFlag:
    """Feature flag definition."""

    def __init__(
        self,
        name: str,
        enabled: bool = False,
        strategy: FeatureFlagStrategy = FeatureFlagStrategy.BOOLEAN,
        config: Optional[Dict[str, Any]] = None,
        description: str = ""
    ):
        """
        Initialize feature flag.

        Args:
            name: Flag name
            enabled: Default enabled state
            strategy: Evaluation strategy
            config: Strategy-specific configuration
            description: Flag description
        """
        self.name = name
        self.enabled = enabled
        self.strategy = strategy
        self.config = config or {}
        self.description = description
        self.created_at = datetime.utcnow()

    def evaluate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Evaluate flag for given context.

        Args:
            context: Evaluation context (user_id, attributes, etc.)

        Returns:
            True if feature is enabled
        """
        if not self.enabled:
            return False

        context = context or {}

        if self.strategy == FeatureFlagStrategy.BOOLEAN:
            return True

        elif self.strategy == FeatureFlagStrategy.PERCENTAGE:
            return self._evaluate_percentage(context)

        elif self.strategy == FeatureFlagStrategy.USER_LIST:
            return self._evaluate_user_list(context)

        elif self.strategy == FeatureFlagStrategy.ATTRIBUTE:
            return self._evaluate_attribute(context)

        return False

    def _evaluate_percentage(self, context: Dict[str, Any]) -> bool:
        """Evaluate percentage-based rollout."""
        percentage = self.config.get("percentage", 0)
        user_id = context.get("user_id")

        if not user_id:
            return False

        # Consistent hash-based distribution
        import hashlib
        hash_value = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
        bucket = hash_value % 100

        return bucket < percentage

    def _evaluate_user_list(self, context: Dict[str, Any]) -> bool:
        """Evaluate user list strategy."""
        allowed_users = self.config.get("user_ids", [])
        user_id = context.get("user_id")

        return user_id in allowed_users

    def _evaluate_attribute(self, context: Dict[str, Any]) -> bool:
        """Evaluate attribute-based strategy."""
        required_attributes = self.config.get("attributes", {})

        for key, expected_value in required_attributes.items():
            actual_value = context.get(key)

            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True


class FeatureFlagManager:
    """Manage feature flags."""

    def __init__(self):
        """Initialize feature flag manager."""
        self.flags: Dict[str, FeatureFlag] = {}
        self.listeners: List[Callable] = []

    def register(self, flag: FeatureFlag):
        """
        Register a feature flag.

        Args:
            flag: FeatureFlag instance
        """
        self.flags[flag.name] = flag
        logger.info(f"Registered feature flag: {flag.name}")

        self._notify_listeners("register", flag.name)

    def unregister(self, flag_name: str):
        """
        Unregister a feature flag.

        Args:
            flag_name: Flag name
        """
        if flag_name in self.flags:
            del self.flags[flag_name]
            logger.info(f"Unregistered feature flag: {flag_name}")

            self._notify_listeners("unregister", flag_name)

    def is_enabled(
        self,
        flag_name: str,
        context: Optional[Dict[str, Any]] = None,
        default: bool = False
    ) -> bool:
        """
        Check if feature flag is enabled.

        Args:
            flag_name: Flag name
            context: Evaluation context
            default: Default value if flag not found

        Returns:
            True if feature is enabled
        """
        flag = self.flags.get(flag_name)

        if flag is None:
            logger.warning(f"Feature flag not found: {flag_name}")
            return default

        result = flag.evaluate(context)

        logger.debug(
            f"Feature flag evaluated: {flag_name}",
            extra={
                "flag": flag_name,
                "result": result,
                "context": context
            }
        )

        return result

    def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """
        Get feature flag by name.

        Args:
            flag_name: Flag name

        Returns:
            FeatureFlag instance or None
        """
        return self.flags.get(flag_name)

    def list_flags(self) -> List[Dict[str, Any]]:
        """
        List all feature flags.

        Returns:
            List of flag information
        """
        return [
            {
                "name": flag.name,
                "enabled": flag.enabled,
                "strategy": flag.strategy,
                "description": flag.description
            }
            for flag in self.flags.values()
        ]

    def update_flag(
        self,
        flag_name: str,
        enabled: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Update feature flag configuration.

        Args:
            flag_name: Flag name
            enabled: New enabled state
            config: New configuration
        """
        flag = self.flags.get(flag_name)

        if flag is None:
            raise ValueError(f"Feature flag not found: {flag_name}")

        if enabled is not None:
            flag.enabled = enabled

        if config is not None:
            flag.config.update(config)

        logger.info(f"Updated feature flag: {flag_name}")

        self._notify_listeners("update", flag_name)

    def add_listener(self, listener: Callable):
        """
        Add change listener.

        Args:
            listener: Callback function
        """
        self.listeners.append(listener)

    def _notify_listeners(self, event: str, flag_name: str):
        """Notify listeners of flag changes."""
        for listener in self.listeners:
            try:
                listener(event, flag_name)
            except Exception as e:
                logger.error(f"Error in flag listener: {e}", exc_info=True)


# Global feature flag manager
feature_flags = FeatureFlagManager()


# Decorator for feature-gated functions
def feature_gate(flag_name: str, default: bool = False):
    """
    Decorator to gate function execution behind feature flag.

    Args:
        flag_name: Feature flag name
        default: Default value if flag not found

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Try to extract context from kwargs
            context = kwargs.get("context")

            if feature_flags.is_enabled(flag_name, context, default):
                return func(*args, **kwargs)
            else:
                logger.info(f"Feature gated: {func.__name__} (flag: {flag_name})")
                return None

        return wrapper
    return decorator


# Example feature flags
def register_default_flags():
    """Register default feature flags."""

    # New API version
    feature_flags.register(FeatureFlag(
        name="api_v3",
        enabled=False,
        strategy=FeatureFlagStrategy.PERCENTAGE,
        config={"percentage": 10},
        description="Enable API v3 endpoints"
    ))

    # Advanced search
    feature_flags.register(FeatureFlag(
        name="advanced_search",
        enabled=True,
        strategy=FeatureFlagStrategy.BOOLEAN,
        description="Enable advanced search features"
    ))

    # Beta features for specific users
    feature_flags.register(FeatureFlag(
        name="beta_features",
        enabled=True,
        strategy=FeatureFlagStrategy.USER_LIST,
        config={"user_ids": [1, 2, 3]},
        description="Beta features for selected users"
    ))

    # Premium features
    feature_flags.register(FeatureFlag(
        name="premium_features",
        enabled=True,
        strategy=FeatureFlagStrategy.ATTRIBUTE,
        config={"attributes": {"subscription": "premium"}},
        description="Premium subscription features"
    ))


# Example usage
@feature_gate("advanced_search", default=False)
def perform_advanced_search(query: str, context: Optional[Dict[str, Any]] = None):
    """Perform advanced search (feature gated)."""
    return f"Advanced search for: {query}"

"""
Tests for Feature Flags System
"""

import pytest
from app.feature_flags import (
    FeatureFlag,
    FeatureFlagStrategy,
    FeatureFlagManager,
    feature_gate,
    feature_flags
)


class TestFeatureFlag:
    """Test FeatureFlag class."""

    def test_flag_initialization(self):
        """Test feature flag initialization."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.BOOLEAN,
            description="Test feature"
        )

        assert flag.name == "test_feature"
        assert flag.enabled is True
        assert flag.strategy == FeatureFlagStrategy.BOOLEAN
        assert flag.description == "Test feature"

    def test_boolean_strategy_enabled(self):
        """Test boolean strategy when enabled."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.BOOLEAN
        )

        assert flag.evaluate() is True

    def test_boolean_strategy_disabled(self):
        """Test boolean strategy when disabled."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=False,
            strategy=FeatureFlagStrategy.BOOLEAN
        )

        assert flag.evaluate() is False

    def test_percentage_strategy(self):
        """Test percentage-based rollout."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50}
        )

        # Test with specific user IDs
        context1 = {"user_id": 1}
        context2 = {"user_id": 2}

        # Results should be consistent for same user
        result1a = flag.evaluate(context1)
        result1b = flag.evaluate(context1)
        assert result1a == result1b

        # Different users may have different results
        result2 = flag.evaluate(context2)
        assert isinstance(result2, bool)

    def test_percentage_strategy_no_user_id(self):
        """Test percentage strategy without user_id."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50}
        )

        result = flag.evaluate({})
        assert result is False

    def test_percentage_strategy_zero_percent(self):
        """Test 0% rollout."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 0}
        )

        context = {"user_id": 1}
        assert flag.evaluate(context) is False

    def test_percentage_strategy_hundred_percent(self):
        """Test 100% rollout."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )

        context = {"user_id": 1}
        assert flag.evaluate(context) is True

    def test_user_list_strategy_allowed(self):
        """Test user list strategy with allowed user."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"user_ids": [1, 2, 3]}
        )

        context = {"user_id": 1}
        assert flag.evaluate(context) is True

    def test_user_list_strategy_not_allowed(self):
        """Test user list strategy with non-allowed user."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"user_ids": [1, 2, 3]}
        )

        context = {"user_id": 999}
        assert flag.evaluate(context) is False

    def test_attribute_strategy_match(self):
        """Test attribute strategy with matching attributes."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.ATTRIBUTE,
            config={"attributes": {"subscription": "premium"}}
        )

        context = {"subscription": "premium"}
        assert flag.evaluate(context) is True

    def test_attribute_strategy_no_match(self):
        """Test attribute strategy with non-matching attributes."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.ATTRIBUTE,
            config={"attributes": {"subscription": "premium"}}
        )

        context = {"subscription": "free"}
        assert flag.evaluate(context) is False

    def test_attribute_strategy_multiple_attributes(self):
        """Test attribute strategy with multiple attributes."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.ATTRIBUTE,
            config={
                "attributes": {
                    "subscription": "premium",
                    "region": "us"
                }
            }
        )

        # All attributes match
        context1 = {"subscription": "premium", "region": "us"}
        assert flag.evaluate(context1) is True

        # One attribute doesn't match
        context2 = {"subscription": "premium", "region": "eu"}
        assert flag.evaluate(context2) is False

    def test_attribute_strategy_list_values(self):
        """Test attribute strategy with list of allowed values."""
        flag = FeatureFlag(
            name="test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.ATTRIBUTE,
            config={"attributes": {"region": ["us", "eu", "asia"]}}
        )

        context1 = {"region": "us"}
        assert flag.evaluate(context1) is True

        context2 = {"region": "africa"}
        assert flag.evaluate(context2) is False


class TestFeatureFlagManager:
    """Test FeatureFlagManager class."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = FeatureFlagManager()

        assert manager.flags == {}
        assert manager.listeners == []

    def test_register_flag(self):
        """Test registering a flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=True)

        manager.register(flag)

        assert "test_feature" in manager.flags
        assert manager.flags["test_feature"] == flag

    def test_unregister_flag(self):
        """Test unregistering a flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=True)

        manager.register(flag)
        manager.unregister("test_feature")

        assert "test_feature" not in manager.flags

    def test_is_enabled_true(self):
        """Test checking if flag is enabled."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=True)
        manager.register(flag)

        assert manager.is_enabled("test_feature") is True

    def test_is_enabled_false(self):
        """Test checking if flag is disabled."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=False)
        manager.register(flag)

        assert manager.is_enabled("test_feature") is False

    def test_is_enabled_not_found(self):
        """Test checking non-existent flag."""
        manager = FeatureFlagManager()

        assert manager.is_enabled("nonexistent", default=False) is False
        assert manager.is_enabled("nonexistent", default=True) is True

    def test_is_enabled_with_context(self):
        """Test checking flag with context."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(
            "test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"user_ids": [1, 2, 3]}
        )
        manager.register(flag)

        context1 = {"user_id": 1}
        assert manager.is_enabled("test_feature", context1) is True

        context2 = {"user_id": 999}
        assert manager.is_enabled("test_feature", context2) is False

    def test_get_flag(self):
        """Test getting flag by name."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=True)
        manager.register(flag)

        retrieved = manager.get_flag("test_feature")

        assert retrieved == flag

    def test_get_flag_not_found(self):
        """Test getting non-existent flag."""
        manager = FeatureFlagManager()

        assert manager.get_flag("nonexistent") is None

    def test_list_flags(self):
        """Test listing all flags."""
        manager = FeatureFlagManager()

        flag1 = FeatureFlag("feature1", enabled=True, description="Feature 1")
        flag2 = FeatureFlag("feature2", enabled=False, description="Feature 2")

        manager.register(flag1)
        manager.register(flag2)

        flags = manager.list_flags()

        assert len(flags) == 2
        assert any(f["name"] == "feature1" for f in flags)
        assert any(f["name"] == "feature2" for f in flags)

    def test_update_flag_enabled(self):
        """Test updating flag enabled state."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=False)
        manager.register(flag)

        manager.update_flag("test_feature", enabled=True)

        assert manager.flags["test_feature"].enabled is True

    def test_update_flag_config(self):
        """Test updating flag configuration."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(
            "test_feature",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 10}
        )
        manager.register(flag)

        manager.update_flag("test_feature", config={"percentage": 50})

        assert manager.flags["test_feature"].config["percentage"] == 50

    def test_update_flag_not_found(self):
        """Test updating non-existent flag."""
        manager = FeatureFlagManager()

        with pytest.raises(ValueError):
            manager.update_flag("nonexistent", enabled=True)

    def test_add_listener(self):
        """Test adding change listener."""
        manager = FeatureFlagManager()
        called = []

        def listener(event, flag_name):
            called.append((event, flag_name))

        manager.add_listener(listener)

        flag = FeatureFlag("test_feature", enabled=True)
        manager.register(flag)

        assert len(called) == 1
        assert called[0] == ("register", "test_feature")

    def test_listener_on_update(self):
        """Test listener called on update."""
        manager = FeatureFlagManager()
        called = []

        def listener(event, flag_name):
            called.append((event, flag_name))

        manager.add_listener(listener)

        flag = FeatureFlag("test_feature", enabled=False)
        manager.register(flag)
        manager.update_flag("test_feature", enabled=True)

        assert len(called) == 2
        assert called[1] == ("update", "test_feature")

    def test_listener_on_unregister(self):
        """Test listener called on unregister."""
        manager = FeatureFlagManager()
        called = []

        def listener(event, flag_name):
            called.append((event, flag_name))

        manager.add_listener(listener)

        flag = FeatureFlag("test_feature", enabled=True)
        manager.register(flag)
        manager.unregister("test_feature")

        assert len(called) == 2
        assert called[1] == ("unregister", "test_feature")


class TestFeatureGateDecorator:
    """Test feature_gate decorator."""

    def test_feature_gate_enabled(self):
        """Test decorator with enabled flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=True)
        manager.register(flag)

        @feature_gate("test_feature")
        def test_function():
            return "executed"

        # Temporarily replace global manager
        import app.feature_flags as ff_module
        original_manager = ff_module.feature_flags
        ff_module.feature_flags = manager

        try:
            result = test_function()
            assert result == "executed"
        finally:
            ff_module.feature_flags = original_manager

    def test_feature_gate_disabled(self):
        """Test decorator with disabled flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag("test_feature", enabled=False)
        manager.register(flag)

        @feature_gate("test_feature")
        def test_function():
            return "executed"

        import app.feature_flags as ff_module
        original_manager = ff_module.feature_flags
        ff_module.feature_flags = manager

        try:
            result = test_function()
            assert result is None
        finally:
            ff_module.feature_flags = original_manager

    def test_feature_gate_with_default(self):
        """Test decorator with default value."""
        manager = FeatureFlagManager()

        @feature_gate("nonexistent_feature", default=True)
        def test_function():
            return "executed"

        import app.feature_flags as ff_module
        original_manager = ff_module.feature_flags
        ff_module.feature_flags = manager

        try:
            result = test_function()
            assert result == "executed"
        finally:
            ff_module.feature_flags = original_manager


class TestFeatureFlagStrategy:
    """Test FeatureFlagStrategy enum."""

    def test_strategies_exist(self):
        """Test that all strategies exist."""
        assert hasattr(FeatureFlagStrategy, "BOOLEAN")
        assert hasattr(FeatureFlagStrategy, "PERCENTAGE")
        assert hasattr(FeatureFlagStrategy, "USER_LIST")
        assert hasattr(FeatureFlagStrategy, "ATTRIBUTE")

    def test_strategy_values(self):
        """Test strategy string values."""
        assert FeatureFlagStrategy.BOOLEAN == "boolean"
        assert FeatureFlagStrategy.PERCENTAGE == "percentage"
        assert FeatureFlagStrategy.USER_LIST == "user_list"
        assert FeatureFlagStrategy.ATTRIBUTE == "attribute"

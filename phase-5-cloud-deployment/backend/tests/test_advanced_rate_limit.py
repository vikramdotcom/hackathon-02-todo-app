"""
Tests for Advanced Rate Limiting System
"""

import pytest
import time
from app.advanced_rate_limit import (
    TokenBucket,
    RateLimiter,
    RateLimitConfig,
    RateLimitManager,
    RateLimitTier,
    TIER_CONFIGS
)


class TestTokenBucket:
    """Test TokenBucket class."""

    def test_bucket_initialization(self):
        """Test token bucket initialization."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10

    def test_consume_tokens_success(self):
        """Test consuming tokens successfully."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        result = bucket.consume(5)

        assert result is True
        assert bucket.tokens == 5

    def test_consume_tokens_insufficient(self):
        """Test consuming tokens when insufficient."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        result = bucket.consume(15)

        assert result is False
        assert bucket.tokens == 10

    def test_refill_tokens(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=2.0)

        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0

        # Wait for refill
        time.sleep(1.0)

        # Should have refilled ~2 tokens
        available = bucket.get_available_tokens()
        assert available >= 1

    def test_refill_cap_at_capacity(self):
        """Test refill doesn't exceed capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=5.0)

        # Wait for refill
        time.sleep(5.0)

        # Should cap at capacity
        assert bucket.get_available_tokens() == 10

    def test_get_wait_time_no_wait(self):
        """Test wait time when tokens available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        wait_time = bucket.get_wait_time(5)

        assert wait_time == 0.0

    def test_get_wait_time_with_wait(self):
        """Test wait time when tokens needed."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Consume all tokens
        bucket.consume(10)

        # Need to wait for refill
        wait_time = bucket.get_wait_time(5)

        assert wait_time > 0

    def test_get_available_tokens(self):
        """Test getting available tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        bucket.consume(3)

        available = bucket.get_available_tokens()

        assert available == 7


class TestRateLimitConfig:
    """Test RateLimitConfig class."""

    def test_config_initialization(self):
        """Test config initialization."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )

        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_size == 10

    def test_config_default_values(self):
        """Test config default values."""
        config = RateLimitConfig()

        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_size == 10


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_limiter_initialization(self):
        """Test limiter initialization."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )

        limiter = RateLimiter(config)

        assert limiter.config == config
        assert limiter.minute_bucket is not None
        assert limiter.hour_bucket is not None
        assert limiter.day_bucket is not None
        assert limiter.burst_bucket is not None

    def test_check_limit_allowed(self):
        """Test check limit when allowed."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )

        limiter = RateLimiter(config)

        allowed, retry_after = limiter.check_limit()

        assert allowed is True
        assert retry_after is None

    def test_check_limit_burst_exceeded(self):
        """Test check limit when burst exceeded."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=2
        )

        limiter = RateLimiter(config)

        # Consume burst
        limiter.check_limit()
        limiter.check_limit()

        # Should be rate limited
        allowed, retry_after = limiter.check_limit()

        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0

    def test_get_limits(self):
        """Test getting current limits."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )

        limiter = RateLimiter(config)

        limits = limiter.get_limits()

        assert "minute" in limits
        assert "hour" in limits
        assert "day" in limits
        assert "burst" in limits

        assert limits["minute"]["limit"] == 60
        assert limits["hour"]["limit"] == 1000
        assert limits["day"]["limit"] == 10000
        assert limits["burst"]["limit"] == 10


class TestRateLimitManager:
    """Test RateLimitManager class."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = RateLimitManager()

        assert manager.user_limiters == {}
        assert manager.endpoint_limiters == {}
        assert manager.user_tiers == {}

    def test_set_user_tier(self):
        """Test setting user tier."""
        manager = RateLimitManager()

        manager.set_user_tier(123, RateLimitTier.PREMIUM)

        assert manager.user_tiers[123] == RateLimitTier.PREMIUM
        assert 123 in manager.user_limiters

    def test_get_user_limiter_default(self):
        """Test getting user limiter with default tier."""
        manager = RateLimitManager()

        limiter = manager.get_user_limiter(123)

        assert limiter is not None
        assert manager.user_tiers[123] == RateLimitTier.FREE

    def test_get_user_limiter_existing(self):
        """Test getting existing user limiter."""
        manager = RateLimitManager()

        manager.set_user_tier(123, RateLimitTier.PREMIUM)
        limiter1 = manager.get_user_limiter(123)
        limiter2 = manager.get_user_limiter(123)

        assert limiter1 == limiter2

    def test_check_user_limit_allowed(self):
        """Test checking user limit when allowed."""
        manager = RateLimitManager()

        manager.set_user_tier(123, RateLimitTier.PREMIUM)

        allowed, retry_after = manager.check_user_limit(123)

        assert allowed is True
        assert retry_after is None

    def test_check_user_limit_exceeded(self):
        """Test checking user limit when exceeded."""
        manager = RateLimitManager()

        # Set very low limits
        config = RateLimitConfig(
            requests_per_minute=1,
            requests_per_hour=1,
            requests_per_day=1,
            burst_size=1
        )

        manager.user_limiters[123] = RateLimiter(config)

        # First request allowed
        allowed1, _ = manager.check_user_limit(123)
        assert allowed1 is True

        # Second request should be rate limited
        allowed2, retry_after = manager.check_user_limit(123)
        assert allowed2 is False
        assert retry_after is not None

    def test_get_user_limits(self):
        """Test getting user limits."""
        manager = RateLimitManager()

        manager.set_user_tier(123, RateLimitTier.BASIC)

        limits = manager.get_user_limits(123)

        assert "minute" in limits
        assert "hour" in limits
        assert "day" in limits
        assert "burst" in limits

    def test_register_endpoint_limit(self):
        """Test registering endpoint limit."""
        manager = RateLimitManager()

        config = RateLimitConfig(requests_per_minute=30)

        manager.register_endpoint_limit("/api/search", config)

        assert "/api/search" in manager.endpoint_limiters

    def test_check_endpoint_limit_no_limit(self):
        """Test checking endpoint with no limit."""
        manager = RateLimitManager()

        allowed, retry_after = manager.check_endpoint_limit("/api/todos")

        assert allowed is True
        assert retry_after is None

    def test_check_endpoint_limit_with_limit(self):
        """Test checking endpoint with limit."""
        manager = RateLimitManager()

        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )

        manager.register_endpoint_limit("/api/search", config)

        allowed, retry_after = manager.check_endpoint_limit("/api/search")

        assert allowed is True
        assert retry_after is None


class TestRateLimitTier:
    """Test RateLimitTier enum."""

    def test_tiers_exist(self):
        """Test that all tiers exist."""
        assert hasattr(RateLimitTier, "FREE")
        assert hasattr(RateLimitTier, "BASIC")
        assert hasattr(RateLimitTier, "PREMIUM")
        assert hasattr(RateLimitTier, "ENTERPRISE")

    def test_tier_values(self):
        """Test tier string values."""
        assert RateLimitTier.FREE == "free"
        assert RateLimitTier.BASIC == "basic"
        assert RateLimitTier.PREMIUM == "premium"
        assert RateLimitTier.ENTERPRISE == "enterprise"


class TestTierConfigs:
    """Test tier configurations."""

    def test_all_tiers_have_configs(self):
        """Test that all tiers have configurations."""
        for tier in RateLimitTier:
            assert tier in TIER_CONFIGS

    def test_free_tier_config(self):
        """Test free tier configuration."""
        config = TIER_CONFIGS[RateLimitTier.FREE]

        assert config.requests_per_minute == 10
        assert config.requests_per_hour == 100
        assert config.requests_per_day == 1000
        assert config.burst_size == 5

    def test_basic_tier_config(self):
        """Test basic tier configuration."""
        config = TIER_CONFIGS[RateLimitTier.BASIC]

        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.requests_per_day == 10000
        assert config.burst_size == 10

    def test_premium_tier_config(self):
        """Test premium tier configuration."""
        config = TIER_CONFIGS[RateLimitTier.PREMIUM]

        assert config.requests_per_minute == 300
        assert config.requests_per_hour == 5000
        assert config.requests_per_day == 50000
        assert config.burst_size == 50

    def test_enterprise_tier_config(self):
        """Test enterprise tier configuration."""
        config = TIER_CONFIGS[RateLimitTier.ENTERPRISE]

        assert config.requests_per_minute == 1000
        assert config.requests_per_hour == 20000
        assert config.requests_per_day == 200000
        assert config.burst_size == 100

    def test_tier_hierarchy(self):
        """Test that higher tiers have higher limits."""
        free = TIER_CONFIGS[RateLimitTier.FREE]
        basic = TIER_CONFIGS[RateLimitTier.BASIC]
        premium = TIER_CONFIGS[RateLimitTier.PREMIUM]
        enterprise = TIER_CONFIGS[RateLimitTier.ENTERPRISE]

        # Check minute limits
        assert free.requests_per_minute < basic.requests_per_minute
        assert basic.requests_per_minute < premium.requests_per_minute
        assert premium.requests_per_minute < enterprise.requests_per_minute

        # Check hour limits
        assert free.requests_per_hour < basic.requests_per_hour
        assert basic.requests_per_hour < premium.requests_per_hour
        assert premium.requests_per_hour < enterprise.requests_per_hour

        # Check day limits
        assert free.requests_per_day < basic.requests_per_day
        assert basic.requests_per_day < premium.requests_per_day
        assert premium.requests_per_day < enterprise.requests_per_day

        # Check burst sizes
        assert free.burst_size < basic.burst_size
        assert basic.burst_size < premium.burst_size
        assert premium.burst_size < enterprise.burst_size

"""
Distributed Caching System

Implement distributed caching with multiple backends.
"""

import logging
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


class CacheBackend:
    """Base cache backend interface."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache."""
        raise NotImplementedError

    async def delete(self, key: str):
        """Delete value from cache."""
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        raise NotImplementedError

    async def clear(self):
        """Clear all cache entries."""
        raise NotImplementedError


class InMemoryCacheBackend(CacheBackend):
    """In-memory cache backend."""

    def __init__(self):
        """Initialize in-memory cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None

        entry = self.cache[key]

        # Check expiration
        if entry["expires_at"] and datetime.utcnow() > entry["expires_at"]:
            del self.cache[key]
            return None

        return entry["value"]

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache."""
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }

    async def delete(self, key: str):
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None

    async def clear(self):
        """Clear all cache entries."""
        self.cache.clear()


class RedisCacheBackend(CacheBackend):
    """Redis cache backend."""

    def __init__(self, redis_client):
        """Initialize Redis cache."""
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache."""
        try:
            serialized = pickle.dumps(value)
            if ttl_seconds:
                await self.redis.setex(key, ttl_seconds, serialized)
            else:
                await self.redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        """Delete value from cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def clear(self):
        """Clear all cache entries."""
        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class CacheManager:
    """Manage distributed cache."""

    def __init__(self, backend: CacheBackend):
        """Initialize cache manager."""
        self.backend = backend
        self.default_ttl = 3600  # 1 hour
        self.hit_count = 0
        self.miss_count = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.backend.get(key)

        if value is not None:
            self.hit_count += 1
            logger.debug(f"Cache hit: {key}")
        else:
            self.miss_count += 1
            logger.debug(f"Cache miss: {key}")

        return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ):
        """Set value in cache."""
        ttl = ttl_seconds or self.default_ttl
        await self.backend.set(key, value, ttl)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    async def delete(self, key: str):
        """Delete value from cache."""
        await self.backend.delete(key)
        logger.debug(f"Cache delete: {key}")

    async def get_or_set(
        self,
        key: str,
        factory_func,
        ttl_seconds: Optional[int] = None
    ) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)

        if value is not None:
            return value

        # Generate value
        value = await factory_func()

        # Store in cache
        await self.set(key, value, ttl_seconds)

        return value

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.hit_count + self.miss_count
        }


class CacheKeyBuilder:
    """Build cache keys."""

    @staticmethod
    def build_key(prefix: str, *args, **kwargs) -> str:
        """Build cache key from components."""
        parts = [prefix]
        parts.extend(str(arg) for arg in args)
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(parts)

    @staticmethod
    def hash_key(data: str) -> str:
        """Hash data to create cache key."""
        return hashlib.md5(data.encode()).hexdigest()


class CacheInvalidator:
    """Invalidate cache entries."""

    def __init__(self, cache_manager: CacheManager):
        """Initialize cache invalidator."""
        self.cache_manager = cache_manager
        self.invalidation_patterns: Dict[str, List[str]] = {}

    def register_pattern(self, event_type: str, cache_keys: List[str]):
        """Register invalidation pattern."""
        self.invalidation_patterns[event_type] = cache_keys

    async def invalidate_on_event(self, event_type: str):
        """Invalidate cache on event."""
        if event_type not in self.invalidation_patterns:
            return

        keys = self.invalidation_patterns[event_type]
        for key in keys:
            await self.cache_manager.delete(key)

        logger.info(
            f"Invalidated {len(keys)} cache keys for event: {event_type}"
        )


class CacheWarmer:
    """Warm up cache with frequently accessed data."""

    def __init__(self, cache_manager: CacheManager):
        """Initialize cache warmer."""
        self.cache_manager = cache_manager
        self.warmup_tasks: List[Dict[str, Any]] = []

    def register_warmup_task(
        self,
        key: str,
        factory_func,
        ttl_seconds: Optional[int] = None
    ):
        """Register cache warmup task."""
        self.warmup_tasks.append({
            "key": key,
            "factory_func": factory_func,
            "ttl_seconds": ttl_seconds
        })

    async def warmup(self):
        """Execute cache warmup."""
        logger.info(f"Starting cache warmup ({len(self.warmup_tasks)} tasks)")

        for task in self.warmup_tasks:
            try:
                value = await task["factory_func"]()
                await self.cache_manager.set(
                    task["key"],
                    value,
                    task["ttl_seconds"]
                )
            except Exception as e:
                logger.error(f"Cache warmup failed for {task['key']}: {e}")

        logger.info("Cache warmup completed")


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(self, cache_manager: CacheManager):
        """Initialize cache decorator."""
        self.cache_manager = cache_manager

    def cached(
        self,
        key_prefix: str,
        ttl_seconds: Optional[int] = None
    ):
        """Cache decorator."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Build cache key
                key_parts = [key_prefix]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

                # Try to get from cache
                cached_value = await self.cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function
                result = await func(*args, **kwargs)

                # Store in cache
                await self.cache_manager.set(cache_key, result, ttl_seconds)

                return result

            return wrapper
        return decorator


class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (Redis)."""

    def __init__(
        self,
        l1_backend: CacheBackend,
        l2_backend: CacheBackend
    ):
        """Initialize multi-level cache."""
        self.l1 = l1_backend
        self.l2 = l2_backend

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 first, then L2)."""
        # Try L1
        value = await self.l1.get(key)
        if value is not None:
            logger.debug(f"L1 cache hit: {key}")
            return value

        # Try L2
        value = await self.l2.get(key)
        if value is not None:
            logger.debug(f"L2 cache hit: {key}")
            # Promote to L1
            await self.l1.set(key, value)
            return value

        logger.debug(f"Cache miss: {key}")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ):
        """Set value in both cache levels."""
        await self.l1.set(key, value, ttl_seconds)
        await self.l2.set(key, value, ttl_seconds)

    async def delete(self, key: str):
        """Delete value from both cache levels."""
        await self.l1.delete(key)
        await self.l2.delete(key)


class CacheMonitor:
    """Monitor cache performance."""

    def __init__(self):
        """Initialize cache monitor."""
        self.metrics: Dict[str, List[float]] = {
            "get_latency": [],
            "set_latency": [],
            "hit_rate": []
        }

    def record_get_latency(self, latency_ms: float):
        """Record get operation latency."""
        self.metrics["get_latency"].append(latency_ms)

    def record_set_latency(self, latency_ms: float):
        """Record set operation latency."""
        self.metrics["set_latency"].append(latency_ms)

    def record_hit_rate(self, hit_rate: float):
        """Record hit rate."""
        self.metrics["hit_rate"].append(hit_rate)

    def get_average_latency(self, operation: str) -> float:
        """Get average latency for operation."""
        latencies = self.metrics.get(f"{operation}_latency", [])
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "avg_get_latency_ms": self.get_average_latency("get"),
            "avg_set_latency_ms": self.get_average_latency("set"),
            "avg_hit_rate": (
                sum(self.metrics["hit_rate"]) / len(self.metrics["hit_rate"])
                if self.metrics["hit_rate"] else 0.0
            )
        }


# Global instances
in_memory_backend = InMemoryCacheBackend()
cache_manager = CacheManager(in_memory_backend)
cache_key_builder = CacheKeyBuilder()
cache_invalidator = CacheInvalidator(cache_manager)
cache_warmer = CacheWarmer(cache_manager)
cache_decorator = CacheDecorator(cache_manager)
cache_monitor = CacheMonitor()


# Helper functions
async def get_cached(key: str) -> Optional[Any]:
    """Get value from cache."""
    return await cache_manager.get(key)


async def set_cached(key: str, value: Any, ttl_seconds: Optional[int] = None):
    """Set value in cache."""
    await cache_manager.set(key, value, ttl_seconds)


async def delete_cached(key: str):
    """Delete value from cache."""
    await cache_manager.delete(key)


def build_cache_key(prefix: str, *args, **kwargs) -> str:
    """Build cache key."""
    return cache_key_builder.build_key(prefix, *args, **kwargs)


# Example usage
async def get_user_cached(user_id: int):
    """Get user with caching."""
    cache_key = build_cache_key("user", user_id)
    return await cache_manager.get_or_set(
        cache_key,
        lambda: fetch_user_from_db(user_id),
        ttl_seconds=300
    )


async def fetch_user_from_db(user_id: int):
    """Fetch user from database."""
    # In production, query actual database
    return {"id": user_id, "name": "User"}

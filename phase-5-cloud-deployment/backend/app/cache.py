"""
Cache Utilities for Phase V Backend

Provides caching functionality for improved performance.
"""

import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple in-memory cache implementation.

    For production, consider using Redis or Memcached.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of items to store
        """
        self._cache = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            self._hits += 1
            logger.debug(f"Cache hit: {key}")
            return self._cache[key]
        else:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (not implemented in simple cache)
        """
        # Implement simple LRU eviction if cache is full
        if len(self._cache) >= self._max_size:
            # Remove oldest item (first item in dict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"Cache eviction: {oldest_key}")

        self._cache[key] = value
        logger.debug(f"Cache set: {key}")

    def delete(self, key: str):
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache delete: {key}")

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2)
        }


# Global cache instance
cache = SimpleCache(max_size=1000)


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Example:
        @cache_result(ttl=60, key_prefix="user")
        def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            # Add args to key
            for arg in args:
                key_parts.append(str(arg))

            # Add kwargs to key (sorted for consistency)
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")

            # Create hash of key parts
            key_string = ":".join(key_parts)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache(key_prefix: str = ""):
    """
    Invalidate cache entries with given prefix.

    Args:
        key_prefix: Prefix of cache keys to invalidate

    Note: This is a simplified implementation. For production,
    use a proper cache invalidation strategy.
    """
    if not key_prefix:
        cache.clear()
    else:
        # In a real implementation, you'd track keys by prefix
        logger.warning("Prefix-based cache invalidation not fully implemented")
        cache.clear()

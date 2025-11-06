"""
Redis caching utilities for ultra-fast API responses.
"""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis
from core.config import settings

# Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            max_connections=50,
        )
    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from function arguments.

    Args:
        prefix: Cache key prefix (e.g., "manuscripts", "users")
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Create a deterministic string from args and kwargs
    key_parts = [prefix]

    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(str(arg.id))
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        if k not in ['db', 'session', 'request']:  # Skip non-cacheable params
            key_parts.append(f"{k}={v}")

    # Hash if key is too long
    key_str = ":".join(key_parts)
    if len(key_str) > 200:
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    return key_str


async def get_cached(key: str) -> Optional[Any]:
    """
    Get cached value.

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found/expired
    """
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        # Cache miss is not critical
        return None


async def set_cached(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set cached value.

    Args:
        key: Cache key
        value: Value to cache (must be JSON serializable)
        ttl: Time to live in seconds (default: 5 minutes)

    Returns:
        True if cached successfully
    """
    try:
        client = await get_redis()
        serialized = json.dumps(value)
        await client.setex(key, ttl, serialized)
        return True
    except Exception:
        # Cache write failure is not critical
        return False


async def delete_cached(pattern: str) -> int:
    """
    Delete cached values by pattern.

    Args:
        pattern: Key pattern (e.g., "manuscripts:*")

    Returns:
        Number of keys deleted
    """
    try:
        client = await get_redis()
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            return await client.delete(*keys)
        return 0
    except Exception:
        return 0


def cached(prefix: str, ttl: int = 300, key_builder: Optional[Callable] = None):
    """
    Decorator for caching function results in Redis.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Optional custom function to build cache key

    Example:
        @cached("manuscripts", ttl=600)
        async def get_manuscript(manuscript_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await set_cached(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


class CacheManager:
    """Cache manager for invalidating related caches."""

    @staticmethod
    async def invalidate_manuscript(manuscript_id: int):
        """Invalidate all caches related to a manuscript."""
        await delete_cached(f"manuscript:{manuscript_id}:*")
        await delete_cached(f"manuscripts:*")
        await delete_cached("featured-articles:*")
        await delete_cached("published-articles:*")

    @staticmethod
    async def invalidate_user(user_id: int):
        """Invalidate all caches related to a user."""
        await delete_cached(f"user:{user_id}:*")
        await delete_cached(f"users:*")

    @staticmethod
    async def invalidate_reviews(manuscript_id: int):
        """Invalidate review caches."""
        await delete_cached(f"manuscript:{manuscript_id}:reviews:*")
        await delete_cached(f"reviews:*")

    @staticmethod
    async def invalidate_all():
        """Clear all caches (use with caution)."""
        client = await get_redis()
        await client.flushdb()

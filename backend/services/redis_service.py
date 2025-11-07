"""
Redis Service

Provides Redis integration for:
- Caching (A/B test assignments, user profiles, analytics)
- Real-time features (WebSocket sessions, live metrics)
- Rate limiting
- Session management
"""
import redis
import json
from typing import Any, Optional, List
from datetime import timedelta
import pickle

class RedisService:
    """Redis service for caching and real-time features."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We'll handle encoding
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self.redis_str_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,  # For string operations
            socket_connect_timeout=5,
            socket_timeout=5
        )

    def ping(self) -> bool:
        """Check if Redis is available."""
        try:
            return self.redis_client.ping()
        except redis.ConnectionError:
            return False

    # ==================== A/B Testing Cache ====================

    def cache_ab_test_assignment(self, user_id: str, test_id: str, variant_id: str, ttl: int = 86400 * 30):
        """
        Cache A/B test assignment for 30 days.

        Args:
            user_id: User identifier
            test_id: Test identifier
            variant_id: Variant identifier
            ttl: Time to live in seconds (default 30 days)
        """
        key = f"ab:assignment:{user_id}:{test_id}"
        self.redis_str_client.setex(key, ttl, variant_id)

    def get_ab_test_assignment(self, user_id: str, test_id: str) -> Optional[str]:
        """Get cached A/B test assignment."""
        key = f"ab:assignment:{user_id}:{test_id}"
        return self.redis_str_client.get(key)

    def cache_ab_test_config(self, test_id: str, config: dict, ttl: int = 3600):
        """Cache A/B test configuration for 1 hour."""
        key = f"ab:config:{test_id}"
        self.redis_str_client.setex(key, ttl, json.dumps(config))

    def get_ab_test_config(self, test_id: str) -> Optional[dict]:
        """Get cached A/B test configuration."""
        key = f"ab:config:{test_id}"
        data = self.redis_str_client.get(key)
        return json.loads(data) if data else None

    def increment_ab_exposure(self, test_id: str, variant_id: str) -> int:
        """Increment exposure count for variant (for real-time stats)."""
        key = f"ab:exposures:{test_id}:{variant_id}"
        return self.redis_client.incr(key)

    def increment_ab_conversion(self, test_id: str, variant_id: str, metric_id: str) -> int:
        """Increment conversion count for variant and metric."""
        key = f"ab:conversions:{test_id}:{variant_id}:{metric_id}"
        return self.redis_client.incr(key)

    def get_ab_stats(self, test_id: str) -> dict:
        """Get real-time A/B test statistics."""
        pattern = f"ab:*:{test_id}:*"
        keys = self.redis_client.keys(pattern)

        stats = {"exposures": {}, "conversions": {}}

        for key in keys:
            key_str = key.decode() if isinstance(key, bytes) else key
            value = self.redis_client.get(key)

            if "exposures" in key_str:
                variant_id = key_str.split(":")[-1]
                stats["exposures"][variant_id] = int(value) if value else 0
            elif "conversions" in key_str:
                parts = key_str.split(":")
                variant_id = parts[-2]
                metric_id = parts[-1]
                if variant_id not in stats["conversions"]:
                    stats["conversions"][variant_id] = {}
                stats["conversions"][variant_id][metric_id] = int(value) if value else 0

        return stats

    # ==================== Personalization Cache ====================

    def cache_user_profile(self, user_id: str, profile: dict, ttl: int = 3600):
        """Cache user profile for 1 hour."""
        key = f"profile:{user_id}"
        self.redis_client.setex(key, ttl, pickle.dumps(profile))

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Get cached user profile."""
        key = f"profile:{user_id}"
        data = self.redis_client.get(key)
        return pickle.loads(data) if data else None

    def cache_recommendations(self, user_id: str, recommendations: List[dict], ttl: int = 1800):
        """Cache recommendations for 30 minutes."""
        key = f"recommendations:{user_id}"
        self.redis_str_client.setex(key, ttl, json.dumps(recommendations))

    def get_recommendations(self, user_id: str) -> Optional[List[dict]]:
        """Get cached recommendations."""
        key = f"recommendations:{user_id}"
        data = self.redis_str_client.get(key)
        return json.loads(data) if data else None

    def add_to_reading_history(self, user_id: str, article_id: str, metadata: dict):
        """Add article to user's reading history (using sorted set by timestamp)."""
        key = f"history:{user_id}"
        score = metadata.get("viewed_at", 0)  # Unix timestamp
        value = json.dumps({"article_id": article_id, **metadata})
        self.redis_str_client.zadd(key, {value: score})

        # Keep only last 100 items
        self.redis_client.zremrangebyrank(key, 0, -101)

    def get_reading_history(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get user's recent reading history."""
        key = f"history:{user_id}"
        items = self.redis_str_client.zrevrange(key, 0, limit - 1)
        return [json.loads(item) for item in items] if items else []

    def update_user_interest(self, user_id: str, topic: str, weight: float):
        """Update user interest weight (using hash)."""
        key = f"interests:{user_id}"
        self.redis_client.hset(key, topic, weight)

        # Set expiration to 90 days
        self.redis_client.expire(key, 86400 * 90)

    def get_user_interests(self, user_id: str) -> dict:
        """Get all user interests."""
        key = f"interests:{user_id}"
        data = self.redis_client.hgetall(key)

        if not data:
            return {}

        return {
            k.decode() if isinstance(k, bytes) else k: float(v.decode() if isinstance(v, bytes) else v)
            for k, v in data.items()
        }

    # ==================== Analytics Cache ====================

    def cache_analytics_dashboard(self, data: dict, date_range: str, ttl: int = 300):
        """Cache analytics dashboard data for 5 minutes."""
        key = f"analytics:dashboard:{date_range}"
        self.redis_str_client.setex(key, ttl, json.dumps(data))

    def get_analytics_dashboard(self, date_range: str) -> Optional[dict]:
        """Get cached analytics dashboard."""
        key = f"analytics:dashboard:{date_range}"
        data = self.redis_str_client.get(key)
        return json.loads(data) if data else None

    def increment_article_view(self, article_id: str):
        """Increment article view count (for real-time stats)."""
        key = f"views:article:{article_id}"
        return self.redis_client.incr(key)

    def increment_article_download(self, article_id: str):
        """Increment article download count."""
        key = f"downloads:article:{article_id}"
        return self.redis_client.incr(key)

    def get_article_stats(self, article_id: str) -> dict:
        """Get real-time article statistics."""
        views = self.redis_client.get(f"views:article:{article_id}")
        downloads = self.redis_client.get(f"downloads:article:{article_id}")

        return {
            "views": int(views) if views else 0,
            "downloads": int(downloads) if downloads else 0
        }

    def track_active_user(self, user_id: str, ttl: int = 300):
        """Track active user (5-minute window)."""
        key = "active_users"
        self.redis_str_client.setex(f"active:{user_id}", ttl, "1")
        return self.redis_client.sadd(key, user_id)

    def get_active_users_count(self) -> int:
        """Get count of active users."""
        # Clean up expired users first
        active_users = self.redis_client.smembers("active_users")
        valid_count = 0

        for user in active_users:
            user_id = user.decode() if isinstance(user, bytes) else user
            if self.redis_str_client.exists(f"active:{user_id}"):
                valid_count += 1
            else:
                # Remove expired user from set
                self.redis_client.srem("active_users", user_id)

        return valid_count

    def add_to_trending(self, article_id: str, score: float):
        """Add article to trending list with score."""
        key = "trending:articles"
        self.redis_client.zadd(key, {article_id: score})

        # Keep only top 100
        self.redis_client.zremrangebyrank(key, 0, -101)

        # Expire after 24 hours
        self.redis_client.expire(key, 86400)

    def get_trending_articles(self, limit: int = 10) -> List[str]:
        """Get trending articles."""
        key = "trending:articles"
        articles = self.redis_client.zrevrange(key, 0, limit - 1)
        return [a.decode() if isinstance(a, bytes) else a for a in articles]

    # ==================== WebSocket Session Management ====================

    def register_websocket_connection(self, user_id: str, connection_id: str, ttl: int = 3600):
        """Register WebSocket connection for user."""
        key = f"ws:user:{user_id}"
        self.redis_str_client.setex(key, ttl, connection_id)

    def get_websocket_connection(self, user_id: str) -> Optional[str]:
        """Get WebSocket connection ID for user."""
        key = f"ws:user:{user_id}"
        return self.redis_str_client.get(key)

    def remove_websocket_connection(self, user_id: str):
        """Remove WebSocket connection."""
        key = f"ws:user:{user_id}"
        self.redis_client.delete(key)

    def publish_notification(self, channel: str, message: dict):
        """Publish notification to channel (for pub/sub)."""
        self.redis_str_client.publish(channel, json.dumps(message))

    def subscribe_to_channel(self, channel: str):
        """Subscribe to channel (returns pubsub object)."""
        pubsub = self.redis_str_client.pubsub()
        pubsub.subscribe(channel)
        return pubsub

    # ==================== Rate Limiting ====================

    def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if rate limit is exceeded.

        Args:
            key: Rate limit key (e.g., "api:user:123")
            limit: Maximum number of requests
            window: Time window in seconds

        Returns:
            True if under limit, False if exceeded
        """
        current = self.redis_client.incr(key)

        if current == 1:
            # First request, set expiration
            self.redis_client.expire(key, window)

        return current <= limit

    def get_rate_limit_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in current window."""
        current = self.redis_client.get(key)
        if not current:
            return limit

        return max(0, limit - int(current))

    # ==================== Session Storage ====================

    def save_session(self, session_id: str, data: dict, ttl: int = 86400):
        """Save session data (24-hour default)."""
        key = f"session:{session_id}"
        self.redis_client.setex(key, ttl, pickle.dumps(data))

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = f"session:{session_id}"
        data = self.redis_client.get(key)
        return pickle.loads(data) if data else None

    def delete_session(self, session_id: str):
        """Delete session."""
        key = f"session:{session_id}"
        self.redis_client.delete(key)

    def extend_session(self, session_id: str, ttl: int = 86400):
        """Extend session expiration."""
        key = f"session:{session_id}"
        self.redis_client.expire(key, ttl)

    # ==================== Cache Invalidation ====================

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        keys = self.redis_client.keys(pattern)
        if keys:
            return self.redis_client.delete(*keys)
        return 0

    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached data for user."""
        patterns = [
            f"profile:{user_id}",
            f"recommendations:{user_id}",
            f"interests:{user_id}",
            f"history:{user_id}",
            f"active:{user_id}"
        ]

        for pattern in patterns:
            self.redis_client.delete(pattern)

    def clear_all(self):
        """Clear all Redis data (use with caution!)."""
        self.redis_client.flushdb()

    # ==================== Health Check ====================

    def health_check(self) -> dict:
        """Get Redis health information."""
        try:
            info = self.redis_client.info()
            return {
                "status": "healthy",
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_days": info.get("uptime_in_days")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_redis_service = None


def get_redis_service() -> RedisService:
    """Get Redis service instance."""
    global _redis_service

    if _redis_service is None:
        # Default configuration - override with environment variables
        import os
        _redis_service = RedisService(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD")
        )

    return _redis_service


# Export for convenience
redis_service = get_redis_service()

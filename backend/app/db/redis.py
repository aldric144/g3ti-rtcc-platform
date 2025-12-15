"""
Redis connection manager for the G3TI RTCC-UIP Backend.

This module provides connection management for Redis, used for:
- Session caching
- Rate limiting data
- Real-time event pub/sub
- Background task queuing (Celery broker)
- Temporary data storage
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis
from redis.exceptions import AuthenticationError
from redis.exceptions import ConnectionError as RedisConnError

from app.core.config import settings
from app.core.exceptions import RedisConnectionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """
    Manages Redis connections and provides caching/pub-sub methods.

    This class implements the singleton pattern to ensure only one client
    instance is created per application lifecycle.

    Usage:
        manager = RedisManager()
        await manager.connect()

        await manager.set("key", "value", expire=3600)
        value = await manager.get("key")

        await manager.close()
    """

    _instance: "RedisManager | None" = None
    _client: redis.Redis | None = None
    _pubsub: redis.client.PubSub | None = None

    def __new__(cls) -> "RedisManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """
        Establish connection to Redis.

        Raises:
            RedisConnectionError: If connection fails
        """
        if self._client is not None:
            return

        try:
            self._client = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )

            # Verify connectivity
            await self._client.ping()

            logger.info("redis_connected", url=settings.redis_url)

        except AuthenticationError as e:
            logger.error("redis_auth_error", error=str(e))
            raise RedisConnectionError(f"Redis authentication failed: {e}") from e
        except RedisConnError as e:
            logger.error("redis_connection_error", error=str(e))
            raise RedisConnectionError(f"Failed to connect to Redis: {e}") from e
        except Exception as e:
            logger.error("redis_error", error=str(e))
            raise RedisConnectionError(f"Redis error: {e}") from e

    async def close(self) -> None:
        """Close the Redis client connection."""
        if self._pubsub is not None:
            await self._pubsub.close()
            self._pubsub = None

        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("redis_disconnected")

    @property
    def client(self) -> redis.Redis:
        """
        Get the Redis client.

        Returns:
            Redis: The Redis client

        Raises:
            RedisConnectionError: If client is not connected
        """
        if self._client is None:
            raise RedisConnectionError("Redis client not initialized. Call connect() first.")
        return self._client

    async def health_check(self) -> bool:
        """
        Check Redis connection health.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if self._client is None:
                return False
            await self._client.ping()
            return True
        except Exception as e:
            logger.warning("redis_health_check_failed", error=str(e))
            return False

    # Key-Value Operations

    async def get(self, key: str) -> str | None:
        """
        Get a value by key.

        Args:
            key: Cache key

        Returns:
            str or None: Cached value if exists
        """
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> bool:
        """
        Set a key-value pair.

        Args:
            key: Cache key
            value: Value to store
            expire: Optional expiration time in seconds

        Returns:
            bool: True if set successfully
        """
        if expire:
            return await self.client.setex(key, expire, value)
        return await self.client.set(key, value)

    async def delete(self, key: str) -> int:
        """
        Delete a key.

        Args:
            key: Cache key

        Returns:
            int: Number of keys deleted
        """
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists
        """
        return await self.client.exists(key) > 0

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on a key.

        Args:
            key: Cache key
            seconds: Expiration time in seconds

        Returns:
            bool: True if expiration was set
        """
        return await self.client.expire(key, seconds)

    # JSON Operations

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        """
        Get a JSON value by key.

        Args:
            key: Cache key

        Returns:
            dict, list, or None: Parsed JSON value if exists
        """
        value = await self.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set_json(
        self, key: str, value: dict[str, Any] | list[Any], expire: int | None = None
    ) -> bool:
        """
        Set a JSON value.

        Args:
            key: Cache key
            value: Value to store (will be JSON serialized)
            expire: Optional expiration time in seconds

        Returns:
            bool: True if set successfully
        """
        return await self.set(key, json.dumps(value), expire)

    # Hash Operations

    async def hget(self, name: str, key: str) -> str | None:
        """
        Get a hash field value.

        Args:
            name: Hash name
            key: Field key

        Returns:
            str or None: Field value if exists
        """
        return await self.client.hget(name, key)

    async def hset(self, name: str, key: str, value: str) -> int:
        """
        Set a hash field value.

        Args:
            name: Hash name
            key: Field key
            value: Field value

        Returns:
            int: 1 if new field, 0 if updated
        """
        return await self.client.hset(name, key, value)

    async def hgetall(self, name: str) -> dict[str, str]:
        """
        Get all hash fields.

        Args:
            name: Hash name

        Returns:
            dict: All field-value pairs
        """
        return await self.client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        """
        Delete hash fields.

        Args:
            name: Hash name
            keys: Field keys to delete

        Returns:
            int: Number of fields deleted
        """
        return await self.client.hdel(name, *keys)

    # Set Operations

    async def sadd(self, name: str, *values: str) -> int:
        """
        Add members to a set.

        Args:
            name: Set name
            values: Values to add

        Returns:
            int: Number of members added
        """
        return await self.client.sadd(name, *values)

    async def srem(self, name: str, *values: str) -> int:
        """
        Remove members from a set.

        Args:
            name: Set name
            values: Values to remove

        Returns:
            int: Number of members removed
        """
        return await self.client.srem(name, *values)

    async def smembers(self, name: str) -> set[str]:
        """
        Get all members of a set.

        Args:
            name: Set name

        Returns:
            set: All members
        """
        return await self.client.smembers(name)

    async def sismember(self, name: str, value: str) -> bool:
        """
        Check if value is a member of set.

        Args:
            name: Set name
            value: Value to check

        Returns:
            bool: True if member
        """
        return await self.client.sismember(name, value)

    # Pub/Sub Operations

    async def publish(self, channel: str, message: str) -> int:
        """
        Publish a message to a channel.

        Args:
            channel: Channel name
            message: Message to publish

        Returns:
            int: Number of subscribers that received the message
        """
        return await self.client.publish(channel, message)

    async def publish_json(self, channel: str, message: dict[str, Any]) -> int:
        """
        Publish a JSON message to a channel.

        Args:
            channel: Channel name
            message: Message to publish (will be JSON serialized)

        Returns:
            int: Number of subscribers that received the message
        """
        return await self.publish(channel, json.dumps(message))

    async def subscribe(self, *channels: str) -> redis.client.PubSub:
        """
        Subscribe to channels.

        Args:
            channels: Channel names to subscribe to

        Returns:
            PubSub: Pub/Sub client for receiving messages
        """
        if self._pubsub is None:
            self._pubsub = self.client.pubsub()

        await self._pubsub.subscribe(*channels)
        return self._pubsub

    async def unsubscribe(self, *channels: str) -> None:
        """
        Unsubscribe from channels.

        Args:
            channels: Channel names to unsubscribe from
        """
        if self._pubsub is not None:
            await self._pubsub.unsubscribe(*channels)

    # Rate Limiting

    async def rate_limit_check(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.

        Args:
            key: Rate limit key (e.g., user ID or IP)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        import time

        now = time.time()
        window_start = now - window_seconds

        pipe = self.client.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiration
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[2]

        is_allowed = request_count <= max_requests
        remaining = max(0, max_requests - request_count)

        return is_allowed, remaining


# Global Redis manager instance
_redis_manager: RedisManager | None = None


async def get_redis() -> RedisManager:
    """
    Get the Redis manager instance.

    This function is designed to be used as a FastAPI dependency.
    In demo mode, returns a manager even if connection fails.

    Returns:
        RedisManager: The Redis manager instance
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
        try:
            await _redis_manager.connect()
        except Exception as e:
            logger.warning("redis_connection_skipped_demo_mode", error=str(e))
    return _redis_manager


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis_manager
    if _redis_manager is not None:
        await _redis_manager.close()
        _redis_manager = None

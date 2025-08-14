"""Redis client configuration and utilities."""
import redis
from typing import Optional

from app.core.config import settings


class RedisClient:
    """Redis client wrapper."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    def connect(self) -> redis.Redis:
        """Connect to Redis server."""
        if self._client is None:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._client
    
    def disconnect(self):
        """Disconnect from Redis server."""
        if self._client:
            self._client.close()
            self._client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            if self._client is None:
                return False
            self._client.ping()
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            return False
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get the Redis client instance."""
        return self._client


# Global Redis client instance
redis_client = RedisClient()


def get_redis() -> redis.Redis:
    """Get Redis client dependency."""
    return redis_client.connect()
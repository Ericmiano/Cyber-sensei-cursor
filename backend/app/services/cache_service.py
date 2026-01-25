"""Caching service using Redis."""
from typing import Optional, Any
import json
import redis
from app.core.config import settings
from app.core.logging_config import logger


class CacheService:
    """Service for caching data in Redis."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                )
                # Test connection
                self._client.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self._client = None
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,  # Default 1 hour
    ) -> bool:
        """Set value in cache with TTL."""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0


# Singleton instance
cache_service = CacheService()

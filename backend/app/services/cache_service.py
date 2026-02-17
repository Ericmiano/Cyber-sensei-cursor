"""Caching service using Redis with async support."""
from typing import Optional, Any, Callable
import json
import pickle
from functools import wraps
from app.core.config import settings
from app.core.logging_config import logger
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# In-memory fallback cache
_memory_cache: dict[str, tuple[Any, float]] = {}


class CacheService:
    """Service for caching data in Redis with async support and in-memory fallback."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    async def _get_client(self) -> Optional[redis.Redis]:
        """Get or create async Redis client."""
        if not REDIS_AVAILABLE:
            return None
        
        if self._client is None and not self._connected:
            try:
                self._client = await redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=False,
                )
                await self._client.ping()
                self._connected = True
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}. Using in-memory fallback.")
                self._client = None
                self._connected = True
        
        return self._client
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return pickle.loads(data)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        client = await self._get_client()
        
        if client:
            try:
                data = await client.get(key)
                if data:
                    return self._deserialize(data)
                return None
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # In-memory fallback
        import time
        if key in _memory_cache:
            value, expiry = _memory_cache[key]
            if expiry == 0 or time.time() < expiry:
                return value
            else:
                del _memory_cache[key]
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)."""
        client = await self._get_client()
        
        if client:
            try:
                data = self._serialize(value)
                await client.setex(key, ttl, data)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # In-memory fallback
        import time
        expiry = time.time() + ttl if ttl > 0 else 0
        _memory_cache[key] = (value, expiry)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        client = await self._get_client()
        
        if client:
            try:
                await client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        if key in _memory_cache:
            del _memory_cache[key]
        
        return True
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        client = await self._get_client()
        
        if client:
            try:
                keys = []
                async for key in client.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    await client.delete(*keys)
                return len(keys)
            except Exception as e:
                logger.warning(f"Redis delete_pattern error: {e}")
        
        # In-memory fallback
        import fnmatch
        keys_to_delete = [k for k in _memory_cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del _memory_cache[key]
        return len(keys_to_delete)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = await self._get_client()
        
        if client:
            try:
                return await client.exists(key) > 0
            except Exception as e:
                logger.warning(f"Redis exists error: {e}")
        
        import time
        if key in _memory_cache:
            value, expiry = _memory_cache[key]
            if expiry == 0 or time.time() < expiry:
                return True
            else:
                del _memory_cache[key]
        
        return False
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = ":".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache async function results.
    
    Usage:
        @cached(ttl=600, key_prefix="user_mastery")
        async def get_user_mastery(user_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{cache_service.cache_key(*args, **kwargs)}"
            
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Singleton instance
cache_service = CacheService()

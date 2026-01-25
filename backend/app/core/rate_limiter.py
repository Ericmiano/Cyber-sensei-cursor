"""Rate limiting utilities with Redis support."""
from typing import Optional, Callable
from fastapi import Request, HTTPException, status, Depends
from app.core.config import settings
import time
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Fallback in-memory rate limiter
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for rate limiting."""
    global _redis_client
    if not REDIS_AVAILABLE:
        return None
    
    if _redis_client is None and settings.REDIS_URL:
        try:
            _redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await _redis_client.ping()
            logger.info("Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}. Using in-memory fallback.")
            _redis_client = None
    return _redis_client


def get_client_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting."""
    # Use IP address or user ID if authenticated
    client_ip = request.client.host if request.client else "unknown"
    # Could also use: request.state.user_id if authenticated
    return client_ip


async def check_rate_limit(
    request: Request,
    requests_per_minute: int = 60,
    key_func: Optional[callable] = None,
) -> None:
    """
    Check rate limit and raise exception if exceeded.
    
    This is a FastAPI dependency that can be used with Depends().
    """
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    if key_func is None:
        key_func = get_client_identifier
    
    client_id = key_func(request)
    now = time.time()
    
    # Try Redis first
    redis_client = await get_redis_client()
    if redis_client:
        try:
            key = f"rate_limit:{client_id}"
            # Use sliding window with Redis
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, now - 60)  # Remove old entries
            pipe.zcard(key)  # Count current entries
            pipe.zadd(key, {str(now): now})  # Add current request
            pipe.expire(key, 60)  # Set expiry
            results = await pipe.execute()
            request_count = results[1]
            
            if request_count >= requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {requests_per_minute} requests per minute",
                    headers={"Retry-After": "60"},
                )
            return
        except Exception as e:
            if REDIS_AVAILABLE and isinstance(e, redis.RedisError):
                pass  # Already handled
            else:
                pass
            logger.warning(f"Redis error in rate limiting: {e}. Falling back to in-memory.")
    
    # Fallback to in-memory
    if client_id in _rate_limit_store:
        _rate_limit_store[client_id] = [
            timestamp
            for timestamp in _rate_limit_store[client_id]
            if now - timestamp < 60
        ]
        
        request_count = len(_rate_limit_store[client_id])
        if request_count >= requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {requests_per_minute} requests per minute",
                headers={"Retry-After": "60"},
            )
    
    _rate_limit_store[client_id].append(now)


def rate_limit_dependency(requests_per_minute: int = 60, key_func: Optional[Callable[[Request], str]] = None):
    """
    Create a rate limit dependency for FastAPI.
    
    Usage:
        @router.post("/endpoint")
        async def endpoint(
            request: Request,
            _: None = Depends(rate_limit_dependency(requests_per_minute=5))
        ):
            ...
    """
    async def _check(request: Request = None):
        if request:
            await check_rate_limit(request, requests_per_minute, key_func)
    
    return _check


# Backward compatibility decorator (deprecated - use dependency instead)
def rate_limit(requests_per_minute: int = 60):
    """
    Rate limiting decorator (deprecated).
    
    Use rate_limit_dependency() with Depends() instead for better FastAPI integration.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find Request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if request:
                await check_rate_limit(request, requests_per_minute)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

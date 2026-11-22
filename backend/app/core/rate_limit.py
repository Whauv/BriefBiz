from __future__ import annotations

import time
from collections import defaultdict, deque
from uuid import uuid4

import structlog
from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.config import get_settings
from app.services.redis import get_redis

logger = structlog.get_logger(__name__)


def _too_many_requests() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many authentication attempts. Please try again shortly.",
    )


class InMemoryRateLimiter:
    """Per-process sliding-window limiter.

    Used directly in tests and as the fallback for :class:`RedisRateLimiter` when Redis
    is unreachable. It cannot coordinate across worker processes, which is why
    production uses the Redis-backed limiter.
    """

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    async def check(self, key: str) -> None:
        settings = get_settings()
        window = settings.auth_rate_limit_window_seconds
        limit = settings.auth_rate_limit_max_requests
        now = time.monotonic()
        bucket = self._events[key]

        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            raise _too_many_requests()

        bucket.append(now)


class RedisRateLimiter:
    """Sliding-window limiter backed by Redis sorted sets.

    Unlike the in-memory limiter this coordinates across processes, so it rate-limits
    correctly behind multiple uvicorn/gunicorn workers. If Redis is unavailable it logs
    and falls back to an in-process limiter so authentication keeps working.
    """

    def __init__(self) -> None:
        self._fallback = InMemoryRateLimiter()

    async def check(self, key: str) -> None:
        settings = get_settings()
        window = settings.auth_rate_limit_window_seconds
        limit = settings.auth_rate_limit_max_requests
        redis_key = f"ratelimit:{key}"
        now = time.time()

        try:
            client = get_redis()
            await client.zremrangebyscore(redis_key, 0, now - window)
            count = await client.zcard(redis_key)
            if count >= limit:
                raise _too_many_requests()
            await client.zadd(redis_key, {f"{now}:{uuid4().hex}": now})
            await client.expire(redis_key, window)
        except RedisError:
            logger.warning("rate_limit_redis_unavailable", exc_info=True)
            await self._fallback.check(key)


auth_rate_limiter: RedisRateLimiter = RedisRateLimiter()

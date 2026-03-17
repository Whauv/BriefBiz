from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.elasticsearch import get_elasticsearch
from app.services.redis import get_redis

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    redis_client = get_redis()
    elasticsearch_client = get_elasticsearch()

    redis_ok = await redis_client.ping()
    es_ok = await elasticsearch_client.ping()

    return HealthResponse(
        status="ok" if redis_ok and es_ok else "degraded",
        services={
            "api": "ok",
            "redis": "ok" if redis_ok else "unavailable",
            "elasticsearch": "ok" if es_ok else "unavailable",
        },
    )


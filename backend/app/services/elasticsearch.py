from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings

_es_client: AsyncElasticsearch | None = None


def get_elasticsearch() -> AsyncElasticsearch:
    global _es_client
    if _es_client is None:
        settings = get_settings()
        _es_client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
    return _es_client


async def close_elasticsearch() -> None:
    global _es_client
    if _es_client is not None:
        await _es_client.close()
        _es_client = None


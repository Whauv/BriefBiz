from __future__ import annotations

import structlog
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.company import Company
from app.schemas.articles import ArticleCardResponse
from app.schemas.search import SearchCompanyResult, SearchResponse
from app.services.elasticsearch import get_elasticsearch
from app.services.serializers import serialize_article_cards

logger = structlog.get_logger(__name__)

SEARCH_LIMIT = 20


class SearchService:
    """Full-text search with an Elasticsearch primary path and a SQL fallback.

    The query construction, Elasticsearch id-ordering reconciliation, and SQL
    fallback used to live inline in the search route. Pulling them here makes the
    fallback path observable (it is logged rather than silently swallowed) and lets
    the ranking behavior be unit-tested directly.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query: str) -> SearchResponse:
        articles = await self._search_articles(query)
        companies = await self._search_companies(query)
        return SearchResponse(articles=articles, companies=companies)

    async def _search_articles(self, query: str) -> list[ArticleCardResponse]:
        try:
            return await self._search_articles_es(query)
        except Exception:
            # Elasticsearch may be unavailable or return an unexpected shape; fall
            # back to SQL, but surface the failure instead of hiding it.
            logger.warning("search_elasticsearch_fallback", query=query, exc_info=True)
            return await self._search_articles_sql(query)

    async def _search_articles_es(self, query: str) -> list[ArticleCardResponse]:
        es = get_elasticsearch()
        es_response = await es.search(
            index="articles",
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "summary", "companies^2", "region"],
                }
            },
            size=SEARCH_LIMIT,
        )
        article_ids = [int(hit["_id"]) for hit in es_response["hits"]["hits"]]
        if not article_ids:
            return []

        result = await self.session.execute(select(Article).where(Article.id.in_(article_ids)))
        articles_by_id = {article.id: article for article in result.scalars().unique().all()}
        # Preserve the relevance order Elasticsearch returned.
        ordered = [articles_by_id[article_id] for article_id in article_ids if article_id in articles_by_id]
        return await serialize_article_cards(self.session, ordered)

    async def _search_articles_sql(self, query: str) -> list[ArticleCardResponse]:
        result = await self.session.execute(
            select(Article)
            .where(or_(Article.title.ilike(f"%{query}%"), Article.summary_60w.ilike(f"%{query}%")))
            .limit(SEARCH_LIMIT)
        )
        articles = list(result.scalars().unique().all())
        return await serialize_article_cards(self.session, articles)

    async def _search_companies(self, query: str) -> list[SearchCompanyResult]:
        result = await self.session.execute(
            select(Company)
            .where(or_(Company.name.ilike(f"%{query}%"), Company.slug.ilike(f"%{query}%")))
            .limit(SEARCH_LIMIT)
        )
        return [
            SearchCompanyResult(id=item.id, name=item.name, slug=item.slug, sector=item.sector)
            for item in result.scalars().all()
        ]

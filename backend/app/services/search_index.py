from __future__ import annotations

from elasticsearch import AsyncElasticsearch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.company import ArticleCompany, Company
from app.services.elasticsearch import get_elasticsearch

ARTICLE_INDEX = "articles"


class SearchIndexService:
    def __init__(self) -> None:
        self.client: AsyncElasticsearch = get_elasticsearch()

    async def index_article(self, session: AsyncSession, article: Article) -> None:
        await self._ensure_index()
        company_result = await session.execute(
            select(Company.name)
            .join(ArticleCompany, ArticleCompany.company_id == Company.id)
            .where(ArticleCompany.article_id == article.id)
        )
        company_names = list(company_result.scalars().all())

        await self.client.index(
            index=ARTICLE_INDEX,
            id=str(article.id),
            document={
                "id": article.id,
                "title": article.title,
                "summary": article.summary_60w,
                "vertical": article.vertical.value,
                "sentiment": article.sentiment.value,
                "region": article.region,
                "companies": company_names,
            },
        )

    async def _ensure_index(self) -> None:
        exists = await self.client.indices.exists(index=ARTICLE_INDEX)
        if exists:
            return
        await self.client.indices.create(
            index=ARTICLE_INDEX,
            mappings={
                "properties": {
                    "title": {"type": "text"},
                    "summary": {"type": "text"},
                    "vertical": {"type": "keyword"},
                    "sentiment": {"type": "keyword"},
                    "region": {"type": "keyword"},
                    "companies": {"type": "keyword"},
                }
            },
        )

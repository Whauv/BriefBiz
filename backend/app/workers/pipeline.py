from __future__ import annotations

import asyncio
from time import perf_counter

import structlog

from app.db.session import AsyncSessionLocal

from app.schemas.ingestion import SourceArticle
from app.services.article_classifier import ArticleClassifierService
from app.services.ingestion import ArticleIngestionService
from app.services.news_sources import NewsSourceService
from app.utils.hashing import hash_url

logger = structlog.get_logger(__name__)


class NewsIngestionPipeline:
    def __init__(self) -> None:
        self.news_sources = NewsSourceService()
        self.classifier = ArticleClassifierService()

    async def run(self) -> dict[str, int]:
        started = perf_counter()
        source_articles = await self._fetch_all_articles()
        inserted = 0
        skipped = 0

        for source_article in source_articles:
            created = await self._process_article(source_article)
            if created:
                inserted += 1
            else:
                skipped += 1

        summary = {"fetched": len(source_articles), "inserted": inserted, "skipped": skipped}
        logger.info("ingestion_run_completed", duration_ms=round((perf_counter() - started) * 1000, 2), **summary)
        return summary

    async def _fetch_all_articles(self) -> list[SourceArticle]:
        newsapi_articles, rss_articles = await asyncio.gather(
            self.news_sources.fetch_newsapi_articles(),
            self.news_sources.fetch_rss_articles(),
        )
        logger.info(
            "ingestion_sources_fetched",
            newsapi_count=len(newsapi_articles),
            rss_count=len(rss_articles),
        )
        return newsapi_articles + rss_articles

    async def _process_article(self, source_article: SourceArticle) -> bool:
        logger.info("ingestion_article_received", url=str(source_article.url), source_name=source_article.source_name)
        async with AsyncSessionLocal() as session:
            ingestion_service = ArticleIngestionService(session)
            url_hash = hash_url(str(source_article.url))
            if await ingestion_service.article_exists(url_hash):
                logger.info("ingestion_article_skipped_duplicate", url=str(source_article.url))
                return False

            classification = await self.classifier.classify_article(
                source_article.title,
                source_article.raw_content,
            )
            article = await ingestion_service.create_article(
                source_article,
                vertical=classification.vertical,
                region=classification.region,
            )
            extraction = await self.classifier.extract_companies(
                source_article.title,
                source_article.raw_content,
            )
            await ingestion_service.upsert_companies(article, extraction.companies)
            await ingestion_service.create_follow_notifications(article, extraction.companies)
            await ingestion_service.commit()

        article_id = article.id
        from app.workers.tasks import summarize_article

        logger.info(
            "ingestion_article_committed",
            article_id=article_id,
            vertical=classification.vertical.value,
            region=classification.region,
            company_count=len(extraction.companies),
        )
        summarize_article.delay(article_id)
        return True

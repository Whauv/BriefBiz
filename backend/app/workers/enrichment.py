from __future__ import annotations

from time import perf_counter

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.article import Article
from app.services.conflict_detection import ConflictDetectionService
from app.services.enrichment import ArticleEnrichmentService, source_quality_score
from app.services.search_index import SearchIndexService
from app.services.tts import TextToSpeechService

logger = structlog.get_logger(__name__)


class ArticleEnrichmentWorker:
    def __init__(self) -> None:
        self.enrichment_service = ArticleEnrichmentService()
        self.tts_service = TextToSpeechService()
        self.search_index = SearchIndexService()
        self.conflict_detection = ConflictDetectionService()

    async def process_article(self, article_id: int) -> dict[str, int | str]:
        started = perf_counter()
        async with AsyncSessionLocal() as session:
            article = await self._get_article(session, article_id)
            if article is None:
                logger.warning("enrichment_article_not_found", article_id=article_id)
                return {"article_id": article_id, "status": "not_found"}

            content = (article.raw_content or article.title).strip()
            enrichment = await self.enrichment_service.enrich_article(
                title=article.title,
                content=content,
                source_name=article.source_name,
            )

            article.summary_60w = enrichment.summary_60w
            article.deep_dive = enrichment.deep_dive.model_dump()
            article.sentiment = enrichment.sentiment_impact.sentiment
            article.impact_score = enrichment.sentiment_impact.impact_score
            article.why_it_matters = enrichment.why_it_matters
            article.source_quality_score = source_quality_score(article.source_name)
            article.audio_url = await self.tts_service.synthesize_summary(
                article_id=article.id,
                text=enrichment.summary_60w,
            )
            await self.conflict_detection.assign_topic_and_detect_conflict(session, article)

            await session.commit()
            await session.refresh(article)
            try:
                await self.search_index.index_article(session, article)
            except Exception:
                logger.exception("enrichment_indexing_failed", article_id=article.id)
                return {"article_id": article.id, "status": "processed_without_index"}

            logger.info(
                "enrichment_completed",
                article_id=article.id,
                sentiment=article.sentiment.value,
                impact_score=article.impact_score,
                has_audio=bool(article.audio_url),
                duration_ms=round((perf_counter() - started) * 1000, 2),
            )
            return {"article_id": article.id, "status": "processed"}

    async def _get_article(self, session: AsyncSession, article_id: int) -> Article | None:
        result = await session.execute(select(Article).where(Article.id == article_id))
        return result.scalar_one_or_none()

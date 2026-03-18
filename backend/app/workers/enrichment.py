from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.article import Article
from app.services.conflict_detection import ConflictDetectionService
from app.services.enrichment import ArticleEnrichmentService, source_quality_score
from app.services.search_index import SearchIndexService
from app.services.tts import TextToSpeechService


class ArticleEnrichmentWorker:
    def __init__(self) -> None:
        self.enrichment_service = ArticleEnrichmentService()
        self.tts_service = TextToSpeechService()
        self.search_index = SearchIndexService()
        self.conflict_detection = ConflictDetectionService()

    async def process_article(self, article_id: int) -> dict[str, int | str]:
        async with AsyncSessionLocal() as session:
            article = await self._get_article(session, article_id)
            if article is None:
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
                return {"article_id": article.id, "status": "processed_without_index"}

            return {"article_id": article.id, "status": "processed"}

    async def _get_article(self, session: AsyncSession, article_id: int) -> Article | None:
        result = await session.execute(select(Article).where(Article.id == article_id))
        return result.scalar_one_or_none()

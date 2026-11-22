from __future__ import annotations

from math import sqrt

import structlog
from openai import AsyncOpenAI
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.article import Article
from app.services.openai_client import LLM_ERRORS, get_openai_client
from app.utils.slug import slugify

logger = structlog.get_logger(__name__)

CONFLICT_SIMILARITY_THRESHOLD = 0.82
CANDIDATE_LIMIT = 25
LEXICAL_BASIS = ("funding", "layoffs", "regulatory", "startup", "market", "ai", "payments", "ipo")


class ConflictDetectionService:
    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client

    async def assign_topic_and_detect_conflict(self, session: AsyncSession, article: Article) -> None:
        candidates = list(
            (
                await session.execute(
                    select(Article)
                    .where(Article.id != article.id)
                    .order_by(desc(Article.published_at))
                    .limit(CANDIDATE_LIMIT)
                )
            )
            .scalars()
            .all()
        )

        if not candidates:
            article.topic_cluster = slugify(article.title)[:120]
            article.sources_disagree = False
            article.conflict_context = {"related_article_ids": [], "perspectives": []}
            return

        article_embedding = await self._embedding_for(article)
        best_match: Article | None = None
        best_score = 0.0

        for candidate in candidates:
            candidate_embedding = await self._embedding_for(candidate)
            score = self._cosine_similarity(article_embedding, candidate_embedding)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_match is None or best_score < CONFLICT_SIMILARITY_THRESHOLD:
            article.topic_cluster = slugify(article.title)[:120]
            article.sources_disagree = False
            article.conflict_context = {"related_article_ids": [], "perspectives": []}
            return

        cluster_id = best_match.topic_cluster or slugify(best_match.title)[:120]
        article.topic_cluster = cluster_id

        if best_match.sentiment != article.sentiment:
            perspectives = [
                {
                    "article_id": best_match.id,
                    "source_name": best_match.source_name,
                    "sentiment": best_match.sentiment.value,
                    "summary": best_match.summary_60w,
                },
                {
                    "article_id": article.id,
                    "source_name": article.source_name,
                    "sentiment": article.sentiment.value,
                    "summary": article.summary_60w,
                },
            ]
            best_match.sources_disagree = True
            article.sources_disagree = True
            best_match.conflict_context = {
                "related_article_ids": [best_match.id, article.id],
                "perspectives": perspectives,
            }
            article.conflict_context = {
                "related_article_ids": [best_match.id, article.id],
                "perspectives": perspectives,
            }
        else:
            article.sources_disagree = False
            article.conflict_context = {"related_article_ids": [best_match.id], "perspectives": []}

    async def _embedding_for(self, article: Article) -> list[float]:
        settings = get_settings()
        if article.summary_60w:
            text = f"{article.title}\n{article.summary_60w}"
        else:
            text = f"{article.title}\n{article.raw_content or ''}"

        if not settings.effective_embedding_model:
            return self._lexical_embedding(text)

        try:
            client = self._client or get_openai_client()
            response = await client.embeddings.create(model=settings.effective_embedding_model, input=text[:4000])
            return response.data[0].embedding
        except LLM_ERRORS:
            logger.warning("embedding_fallback", article_id=article.id, exc_info=True)
            return self._lexical_embedding(text)

    @staticmethod
    def _lexical_embedding(text: str) -> list[float]:
        """Offline/dev fallback: a presence vector over a fixed keyword basis."""
        haystack = text.lower()
        return [1.0 if token in haystack else 0.0 for token in LEXICAL_BASIS]

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        length = min(len(left), len(right))
        left = left[:length]
        right = right[:length]
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = sqrt(sum(a * a for a in left))
        right_norm = sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

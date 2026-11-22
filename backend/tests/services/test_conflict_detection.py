from __future__ import annotations

from app.models.article import ArticleSentiment
from app.services.conflict_detection import ConflictDetectionService
from tests.factories import create_article

# With no embedding model configured (the test env has no LLM keys), the service uses
# its deterministic lexical-embedding fallback, so these tests are stable offline.


async def test_single_article_gets_its_own_cluster(db_session):
    article = await create_article(db_session, title="Unique funding story")
    service = ConflictDetectionService()

    await service.assign_topic_and_detect_conflict(db_session, article)

    assert article.topic_cluster
    assert article.sources_disagree is False
    assert article.conflict_context == {"related_article_ids": [], "perspectives": []}


async def test_conflicting_sentiment_flags_disagreement(db_session):
    shared = "funding market ai payments"
    await create_article(
        db_session,
        title=shared,
        summary_60w=shared,
        sentiment=ArticleSentiment.BULLISH,
    )
    second = await create_article(
        db_session,
        title=shared,
        summary_60w=shared,
        sentiment=ArticleSentiment.BEARISH,
    )
    service = ConflictDetectionService()

    await service.assign_topic_and_detect_conflict(db_session, second)

    assert second.sources_disagree is True
    assert len(second.conflict_context["perspectives"]) == 2


def test_cosine_similarity_bounds():
    service = ConflictDetectionService()
    assert service._cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert service._cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert service._cosine_similarity([], [1.0]) == 0.0

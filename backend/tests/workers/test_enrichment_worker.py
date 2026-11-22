from __future__ import annotations

from app.workers.enrichment import ArticleEnrichmentWorker
from tests.factories import create_article


class _MissingResult:
    def scalar_one_or_none(self):
        return None


class _FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, query):
        return _MissingResult()


async def test_process_article_handles_missing(monkeypatch):
    from app.workers import enrichment as enrichment_mod

    monkeypatch.setattr(enrichment_mod, "AsyncSessionLocal", lambda: _FakeSession())

    worker = ArticleEnrichmentWorker()
    result = await worker.process_article(123)

    assert result == {"article_id": 123, "status": "not_found"}


async def test_process_article_enriches_with_fallbacks(db_session):
    """End-to-end against the test DB with no LLM/ES/TTS configured.

    Enrichment uses its deterministic fallback, TTS returns None (no key), conflict
    detection uses the lexical fallback, and indexing fails (no Elasticsearch) so the
    worker reports ``processed_without_index`` — the article is still fully enriched.
    """
    article = await create_article(
        db_session,
        summary_60w=None,
        raw_content="A detailed report about market movements and startup funding.",
    )

    worker = ArticleEnrichmentWorker()
    result = await worker.process_article(article.id)

    assert result["article_id"] == article.id
    assert result["status"] in {"processed", "processed_without_index"}

    await db_session.refresh(article)
    assert article.summary_60w  # deterministic fallback populated it
    assert article.topic_cluster  # conflict detection assigned a cluster

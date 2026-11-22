from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.ingestion import SourceArticle


def _make_source(url: str) -> SourceArticle:
    return SourceArticle(
        title="Example story",
        url=url,
        source_name="Bloomberg",
        published_at=datetime.now(UTC),
        raw_content="Body text",
    )


class _FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


async def test_process_article_inserts_new_and_enqueues_summary(monkeypatch):
    from app.workers import pipeline as pipeline_mod
    from app.workers import tasks as tasks_mod

    class FakeArticle:
        id = 42

    class FakeIngestion:
        def __init__(self, session):
            pass

        async def article_exists(self, url_hash):
            return False

        async def create_article(self, source_article, *, vertical, region):
            return FakeArticle()

        async def upsert_companies(self, article, companies):
            return []

        async def create_follow_notifications(self, article, companies):
            return 0

        async def commit(self):
            return None

    monkeypatch.setattr(pipeline_mod, "NewsSourceService", lambda: object())
    monkeypatch.setattr(pipeline_mod, "AsyncSessionLocal", lambda: _FakeSession())
    monkeypatch.setattr(pipeline_mod, "ArticleIngestionService", FakeIngestion)

    enqueued: list[int] = []
    monkeypatch.setattr(tasks_mod.summarize_article, "delay", lambda article_id: enqueued.append(article_id))

    pipeline = pipeline_mod.NewsIngestionPipeline()
    created = await pipeline._process_article(_make_source("https://example.com/new"))

    assert created is True
    assert enqueued == [42]


async def test_process_article_skips_duplicate(monkeypatch):
    from app.workers import pipeline as pipeline_mod
    from app.workers import tasks as tasks_mod

    class FakeIngestion:
        def __init__(self, session):
            pass

        async def article_exists(self, url_hash):
            return True

    monkeypatch.setattr(pipeline_mod, "NewsSourceService", lambda: object())
    monkeypatch.setattr(pipeline_mod, "AsyncSessionLocal", lambda: _FakeSession())
    monkeypatch.setattr(pipeline_mod, "ArticleIngestionService", FakeIngestion)

    enqueued: list[int] = []
    monkeypatch.setattr(tasks_mod.summarize_article, "delay", lambda article_id: enqueued.append(article_id))

    pipeline = pipeline_mod.NewsIngestionPipeline()
    created = await pipeline._process_article(_make_source("https://example.com/dupe"))

    assert created is False
    assert enqueued == []

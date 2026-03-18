import asyncio

from app.workers.celery_app import celery_app


@celery_app.task(name="briefbiz.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="briefbiz.ingestion.run")
def run_news_ingestion() -> dict[str, int]:
    from app.workers.pipeline import NewsIngestionPipeline

    return asyncio.run(NewsIngestionPipeline().run())


@celery_app.task(name="briefbiz.articles.summarize")
def summarize_article(article_id: int) -> dict[str, int | str]:
    from app.workers.enrichment import ArticleEnrichmentWorker

    return asyncio.run(ArticleEnrichmentWorker().process_article(article_id))


@celery_app.task(name="briefbiz.digest.weekly")
def send_weekly_digest() -> dict[str, int]:
    from app.db.session import AsyncSessionLocal
    from app.services.weekly_digest import WeeklyDigestService

    async def _run() -> dict[str, int]:
        async with AsyncSessionLocal() as session:
            sent = await WeeklyDigestService().send_weekly_digests(session)
            return {"sent": sent}

    return asyncio.run(_run())

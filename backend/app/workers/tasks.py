import asyncio
from time import perf_counter

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="briefbiz.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="briefbiz.ingestion.run")
def run_news_ingestion() -> dict[str, int]:
    from app.workers.pipeline import NewsIngestionPipeline

    started = perf_counter()
    logger.info("task_started", task="briefbiz.ingestion.run")
    try:
        result = asyncio.run(NewsIngestionPipeline().run())
        logger.info(
            "task_completed",
            task="briefbiz.ingestion.run",
            duration_ms=round((perf_counter() - started) * 1000, 2),
            **result,
        )
        return result
    except Exception:
        logger.exception("task_failed", task="briefbiz.ingestion.run")
        raise


@celery_app.task(name="briefbiz.articles.summarize")
def summarize_article(article_id: int) -> dict[str, int | str]:
    from app.workers.enrichment import ArticleEnrichmentWorker

    started = perf_counter()
    logger.info("task_started", task="briefbiz.articles.summarize", article_id=article_id)
    try:
        result = asyncio.run(ArticleEnrichmentWorker().process_article(article_id))
        logger.info(
            "task_completed",
            task="briefbiz.articles.summarize",
            article_id=article_id,
            duration_ms=round((perf_counter() - started) * 1000, 2),
            status=result.get("status"),
        )
        return result
    except Exception:
        logger.exception("task_failed", task="briefbiz.articles.summarize", article_id=article_id)
        raise


@celery_app.task(name="briefbiz.digest.weekly")
def send_weekly_digest() -> dict[str, int]:
    from app.db.session import AsyncSessionLocal
    from app.services.weekly_digest import WeeklyDigestService

    async def _run() -> dict[str, int]:
        async with AsyncSessionLocal() as session:
            sent = await WeeklyDigestService().send_weekly_digests(session)
            return {"sent": sent}

    started = perf_counter()
    logger.info("task_started", task="briefbiz.digest.weekly")
    try:
        result = asyncio.run(_run())
        logger.info(
            "task_completed",
            task="briefbiz.digest.weekly",
            duration_ms=round((perf_counter() - started) * 1000, 2),
            **result,
        )
        return result
    except Exception:
        logger.exception("task_failed", task="briefbiz.digest.weekly")
        raise

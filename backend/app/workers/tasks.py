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
    return {"article_id": article_id, "status": "queued"}

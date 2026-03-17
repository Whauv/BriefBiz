from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import close_db_engine
from app.services.elasticsearch import close_elasticsearch
from app.services.openai_client import close_openai_client
from app.services.redis import close_redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    try:
        yield
    finally:
        await close_openai_client()
        await close_redis()
        await close_elasticsearch()
        await close_db_engine()


app = FastAPI(title="BriefBiz API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)
media_dir = Path(__file__).resolve().parents[1] / "media"
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")

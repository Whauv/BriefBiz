from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from app.db.session import close_db_engine
from app.services.elasticsearch import close_elasticsearch
from app.services.openai_client import close_openai_client
from app.services.redis import close_redis

MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    get_settings()
    # Create the media directory on startup rather than at import time, so importing
    # the app (e.g. in tests) has no filesystem side effects.
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        yield
    finally:
        await close_openai_client()
        await close_redis()
        await close_elasticsearch()
        await close_db_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.effective_cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router)
    # check_dir=False: the directory is created in the lifespan startup, not at import.
    app.mount("/media", StaticFiles(directory=MEDIA_DIR, check_dir=False), name="media")
    return app


app = create_app()

from fastapi import APIRouter

from app.api.routes.articles import router as articles_router
from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as companies_router
from app.api.routes.feed import router as feed_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(feed_router)
api_router.include_router(articles_router)
api_router.include_router(companies_router)
api_router.include_router(search_router)
api_router.include_router(notifications_router)

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.article import Article
from app.models.company import ArticleCompany, Company
from app.schemas.companies import CompanyResponse, TrendingCompanyResponse
from app.services.serializers import serialize_company

router = APIRouter(prefix="/companies", tags=["companies"])

TRENDING_WINDOW = timedelta(days=7)
TRENDING_LIMIT = 20


@router.get("/trending", response_model=list[TrendingCompanyResponse])
async def trending_companies(session: AsyncSession = Depends(get_db_session)) -> list[TrendingCompanyResponse]:
    cutoff = datetime.now(UTC) - TRENDING_WINDOW
    result = await session.execute(
        select(Company.slug, Company.name, func.count(ArticleCompany.article_id).label("article_mentions"))
        .join(ArticleCompany, ArticleCompany.company_id == Company.id)
        .join(Article, Article.id == ArticleCompany.article_id)
        .where(Article.published_at >= cutoff)
        .group_by(Company.id)
        .order_by(desc("article_mentions"), Company.name)
        .limit(TRENDING_LIMIT)
    )
    return [TrendingCompanyResponse.model_validate(row._mapping) for row in result]


@router.get("/{slug}", response_model=CompanyResponse)
async def company_profile(slug: str, session: AsyncSession = Depends(get_db_session)) -> CompanyResponse:
    result = await session.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    article_result = await session.execute(
        select(Article)
        .join(ArticleCompany, ArticleCompany.article_id == Article.id)
        .where(ArticleCompany.company_id == company.id)
        .order_by(desc(Article.published_at))
    )
    articles = list(article_result.scalars().unique().all())
    return await serialize_company(session, company, articles)

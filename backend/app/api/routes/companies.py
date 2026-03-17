from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.article import Article
from app.models.company import ArticleCompany, Company
from app.schemas.companies import CompanyResponse, TrendingCompanyResponse
from app.services.serializers import get_article_company_names, serialize_article_card

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/trending", response_model=list[TrendingCompanyResponse])
async def trending_companies(session: AsyncSession = Depends(get_db_session)) -> list[TrendingCompanyResponse]:
    cutoff = datetime.now(UTC) - timedelta(days=7)
    result = await session.execute(
        select(Company.slug, Company.name, func.count(ArticleCompany.article_id).label("article_mentions"))
        .join(ArticleCompany, ArticleCompany.company_id == Company.id)
        .join(Article, Article.id == ArticleCompany.article_id)
        .where(Article.published_at >= cutoff)
        .group_by(Company.id)
        .order_by(desc("article_mentions"), Company.name)
        .limit(20)
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
    company_map = await get_article_company_names(session, [article.id for article in articles])
    return CompanyResponse(
        id=company.id,
        name=company.name,
        slug=company.slug,
        sector=company.sector,
        hq_country=company.hq_country,
        funding_stage=company.funding_stage,
        investors=company.investors,
        article_count=company.article_count,
        last_headline=company.last_headline,
        created_at=company.created_at,
        articles=[serialize_article_card(article, company_map.get(article.id, [])) for article in articles],
    )


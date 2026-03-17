from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.article import Article
from app.models.company import Company
from app.schemas.search import SearchCompanyResult, SearchResponse
from app.services.elasticsearch import get_elasticsearch
from app.services.serializers import get_article_company_names, serialize_article_card

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1),
    session: AsyncSession = Depends(get_db_session),
) -> SearchResponse:
    article_results = []
    try:
        es = get_elasticsearch()
        es_response = await es.search(
            index="articles",
            query={
                "multi_match": {
                    "query": q,
                    "fields": ["title^3", "summary", "companies^2", "region"],
                }
            },
            size=20,
        )
        article_ids = [int(hit["_id"]) for hit in es_response["hits"]["hits"]]
        if article_ids:
            result = await session.execute(select(Article).where(Article.id.in_(article_ids)))
            articles = list(result.scalars().unique().all())
            company_map = await get_article_company_names(session, [article.id for article in articles])
            article_results = [serialize_article_card(article, company_map.get(article.id, [])) for article in articles]
    except Exception:
        result = await session.execute(
            select(Article)
            .where(or_(Article.title.ilike(f"%{q}%"), Article.summary_60w.ilike(f"%{q}%")))
            .limit(20)
        )
        articles = list(result.scalars().unique().all())
        company_map = await get_article_company_names(session, [article.id for article in articles])
        article_results = [serialize_article_card(article, company_map.get(article.id, [])) for article in articles]

    company_result = await session.execute(
        select(Company).where(or_(Company.name.ilike(f"%{q}%"), Company.slug.ilike(f"%{q}%"))).limit(20)
    )
    companies = [
        SearchCompanyResult(id=item.id, name=item.name, slug=item.slug, sector=item.sector)
        for item in company_result.scalars().all()
    ]

    return SearchResponse(articles=article_results, companies=companies)

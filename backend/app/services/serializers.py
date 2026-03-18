from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.company import ArticleCompany, Company
from app.schemas.articles import ArticleCardResponse, ArticleDetailResponse


async def get_article_company_names(session: AsyncSession, article_ids: list[int]) -> dict[int, list[str]]:
    if not article_ids:
        return {}

    result = await session.execute(
        select(ArticleCompany.article_id, Company.name)
        .join(Company, Company.id == ArticleCompany.company_id)
        .where(ArticleCompany.article_id.in_(article_ids))
    )
    company_map: dict[int, list[str]] = {article_id: [] for article_id in article_ids}
    for article_id, company_name in result.all():
        company_map.setdefault(article_id, []).append(company_name)
    return company_map


def serialize_article_card(article: Article, companies: list[str]) -> ArticleCardResponse:
    return ArticleCardResponse(
        id=article.id,
        title=article.title,
        url=article.url,
        source_name=article.source_name,
        source_quality_score=article.source_quality_score,
        published_at=article.published_at,
        summary_60w=article.summary_60w,
        deep_dive=article.deep_dive,
        sentiment=article.sentiment.value,
        impact_score=article.impact_score,
        vertical=article.vertical.value,
        region=article.region,
        image_url=article.image_url,
        audio_url=article.audio_url,
        why_it_matters=article.why_it_matters,
        topic_cluster=article.topic_cluster,
        sources_disagree=article.sources_disagree,
        conflict_context=article.conflict_context,
        companies=companies,
    )


def serialize_article_detail(article: Article, companies: list[str]) -> ArticleDetailResponse:
    return ArticleDetailResponse(
        **serialize_article_card(article, companies).model_dump(),
        raw_content=article.raw_content,
        created_at=article.created_at,
    )

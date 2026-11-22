from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.company import ArticleCompany, Company
from app.models.notification import Notification
from app.schemas.articles import ArticleCardResponse, ArticleDetailResponse
from app.schemas.companies import CompanyResponse
from app.schemas.notifications import NotificationResponse


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


def _card_fields(article: Article, companies: list[str]) -> dict[str, Any]:
    """Shared field mapping for the card and detail responses.

    Returning a dict lets ``serialize_article_detail`` build its (superset) model in a
    single validation pass instead of validating the card and re-validating the detail.
    """
    deep_dive = article.deep_dive or {
        "what_happened": "",
        "key_players": [],
        "market_impact": "",
        "whats_next": "",
    }
    conflict_context = article.conflict_context or {"related_article_ids": [], "perspectives": []}

    return {
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "source_name": article.source_name,
        "source_quality_score": article.source_quality_score,
        "published_at": article.published_at,
        "summary_60w": article.summary_60w,
        "deep_dive": deep_dive,
        "sentiment": article.sentiment.value,
        "impact_score": article.impact_score,
        "vertical": article.vertical.value,
        "region": article.region,
        "image_url": article.image_url,
        "audio_url": article.audio_url,
        "why_it_matters": article.why_it_matters,
        "topic_cluster": article.topic_cluster,
        "sources_disagree": bool(article.sources_disagree),
        "conflict_context": conflict_context,
        "companies": companies,
    }


def serialize_article_card(article: Article, companies: list[str]) -> ArticleCardResponse:
    return ArticleCardResponse(**_card_fields(article, companies))


def serialize_article_detail(article: Article, companies: list[str]) -> ArticleDetailResponse:
    return ArticleDetailResponse(
        **_card_fields(article, companies),
        raw_content=article.raw_content,
        created_at=article.created_at or article.published_at,
    )


async def serialize_article_cards(session: AsyncSession, articles: Iterable[Article]) -> list[ArticleCardResponse]:
    """Load company names and serialize a batch of articles in one step.

    Collapses the ``fetch -> company names -> serialize`` sequence that was repeated
    across the feed, search, company, and article routes.
    """
    article_list = list(articles)
    company_map = await get_article_company_names(session, [article.id for article in article_list])
    return [serialize_article_card(article, company_map.get(article.id, [])) for article in article_list]


async def serialize_company(
    session: AsyncSession,
    company: Company,
    articles: Iterable[Article],
) -> CompanyResponse:
    cards = await serialize_article_cards(session, articles)
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
        articles=cards,
    )


def serialize_notification(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        article_id=notification.article_id,
        type=notification.type,
        read=notification.read,
        created_at=notification.created_at,
    )

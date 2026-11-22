from __future__ import annotations

from app.services.serializers import (
    get_article_company_names,
    serialize_article_cards,
    serialize_article_detail,
    serialize_company,
    serialize_notification,
)
from tests.factories import (
    create_article,
    create_company,
    create_notification,
    create_user,
    link_article_company,
)


async def test_get_article_company_names_groups_by_article(db_session):
    company_a = await create_company(db_session, name="Acme")
    company_b = await create_company(db_session, name="Globex")
    article = await create_article(db_session)
    await link_article_company(db_session, article, company_a)
    await link_article_company(db_session, article, company_b)

    mapping = await get_article_company_names(db_session, [article.id])

    assert sorted(mapping[article.id]) == ["Acme", "Globex"]


async def test_get_article_company_names_empty_input():
    assert await _call_empty() == {}


async def _call_empty():
    # get_article_company_names short-circuits on an empty id list without touching the DB.
    return await get_article_company_names(session=None, article_ids=[])  # type: ignore[arg-type]


async def test_serialize_article_cards_attaches_companies(db_session):
    company = await create_company(db_session, name="Acme")
    article = await create_article(db_session, title="Deal")
    await link_article_company(db_session, article, company)

    cards = await serialize_article_cards(db_session, [article])

    assert len(cards) == 1
    assert cards[0].companies == ["Acme"]


async def test_serialize_article_detail_includes_raw_content(db_session):
    article = await create_article(db_session, raw_content="full body")

    detail = serialize_article_detail(article, [])

    assert detail.raw_content == "full body"
    assert detail.created_at is not None


async def test_serialize_company_includes_article_cards(db_session):
    company = await create_company(db_session, name="Acme")
    article = await create_article(db_session, title="Acme news")
    await link_article_company(db_session, article, company)

    response = await serialize_company(db_session, company, [article])

    assert response.name == "Acme"
    assert response.articles[0].title == "Acme news"


async def test_serialize_notification(db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    notification = await create_notification(db_session, user=user, article=article, read=True)

    result = serialize_notification(notification)

    assert result.id == notification.id
    assert result.read is True

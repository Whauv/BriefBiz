from __future__ import annotations

from sqlalchemy import select

from app.models.company import ArticleCompany, Company
from app.services.ingestion import ArticleIngestionService
from tests.factories import create_article


async def test_article_exists_detects_known_hash(db_session):
    article = await create_article(db_session, url_hash="known-hash")
    service = ArticleIngestionService(db_session)

    assert await service.article_exists("known-hash") is True
    assert await service.article_exists("unknown-hash") is False
    assert article.url_hash == "known-hash"


async def test_upsert_companies_dedupes_and_links(db_session):
    article = await create_article(db_session, title="Acme merges with Acme")
    service = ArticleIngestionService(db_session)

    companies = await service.upsert_companies(article, ["Acme", " acme ", "Globex"])
    await db_session.commit()

    # "Acme" and " acme " collapse to a single company (case-insensitive, trimmed).
    names = sorted(c.name for c in companies)
    assert names == ["Acme", "Globex"]

    all_companies = (await db_session.execute(select(Company))).scalars().all()
    assert len(all_companies) == 2

    links = (
        await db_session.execute(select(ArticleCompany).where(ArticleCompany.article_id == article.id))
    ).scalars().all()
    assert len(links) == 2


async def test_upsert_companies_reuses_existing(db_session):
    article1 = await create_article(db_session, title="First")
    article2 = await create_article(db_session, title="Second")
    service = ArticleIngestionService(db_session)

    await service.upsert_companies(article1, ["Acme"])
    await db_session.commit()
    await service.upsert_companies(article2, ["Acme"])
    await db_session.commit()

    companies = (await db_session.execute(select(Company).where(Company.name == "Acme"))).scalars().all()
    assert len(companies) == 1
    assert companies[0].article_count == 2

from __future__ import annotations

from app.models.article import ArticleVertical
from tests.factories import create_article, create_company


class _FakeES:
    def __init__(self, ids: list[int]) -> None:
        self._ids = ids

    async def search(self, **kwargs):
        return {"hits": {"hits": [{"_id": str(article_id)} for article_id in self._ids]}}


async def test_search_preserves_elasticsearch_order(db_client, db_session, monkeypatch):
    first = await create_article(db_session, title="Alpha result")
    second = await create_article(db_session, title="Beta result")

    # ES returns second, then first — the route must preserve that ranking.
    monkeypatch.setattr(
        "app.services.search_service.get_elasticsearch",
        lambda: _FakeES([second.id, first.id]),
    )

    response = await db_client.get("/search", params={"q": "result"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["articles"]] == [second.id, first.id]


async def test_search_falls_back_to_sql_when_es_unavailable(db_client, db_session, monkeypatch):
    await create_article(db_session, title="Fintech unicorn expands", vertical=ArticleVertical.GENERAL)
    await create_article(db_session, title="Totally unrelated")

    def _boom():
        raise RuntimeError("elasticsearch down")

    monkeypatch.setattr("app.services.search_service.get_elasticsearch", _boom)

    response = await db_client.get("/search", params={"q": "fintech"})

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["articles"]]
    assert titles == ["Fintech unicorn expands"]


async def test_search_returns_matching_companies(db_client, db_session, monkeypatch):
    await create_company(db_session, name="Finco", slug="finco", sector="FinTech")

    monkeypatch.setattr("app.services.search_service.get_elasticsearch", lambda: _FakeES([]))

    response = await db_client.get("/search", params={"q": "finco"})

    assert response.status_code == 200
    companies = response.json()["companies"]
    assert companies[0]["slug"] == "finco"

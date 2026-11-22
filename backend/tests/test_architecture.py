"""Architecture guard tests.

These enforce the layering established by the service-layer refactor: the fully
extracted routers must delegate all data access to services rather than building
queries inline. (Routes that still own small amounts of query logic — articles,
companies, notifications, auth — are intentionally not covered yet.)
"""

from __future__ import annotations

import inspect

from app.api.routes import feed, search


def test_feed_and_search_routes_delegate_queries_to_services():
    for module in (feed, search):
        source = inspect.getsource(module)
        assert "select(" not in source, f"{module.__name__} should not build queries inline"
        assert ".execute(" not in source, f"{module.__name__} should not execute queries inline"


def test_feed_and_search_routes_use_their_services():
    assert "FeedService" in inspect.getsource(feed)
    assert "SearchService" in inspect.getsource(search)

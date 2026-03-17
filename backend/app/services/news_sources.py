from __future__ import annotations

import asyncio
from typing import Any

import feedparser
import httpx
from dateutil import parser as date_parser

from app.core.config import get_settings
from app.schemas.ingestion import SourceArticle
from app.utils.content import strip_html, truncate_text

NEWS_API_BASE_URL = "https://newsapi.org/v2"
RSS_FEEDS: tuple[str, ...] = (
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/venturebeat/SZYF",
    "https://www.forbes.com/innovation/feed2",
    "https://feeds.bloomberg.com/businessweek/news.rss",
    "https://news.crunchbase.com/feed/",
)


class NewsSourceService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_newsapi_articles(self) -> list[SourceArticle]:
        headers = {"X-Api-Key": self.settings.news_api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            responses = await asyncio.gather(
                client.get(
                    f"{NEWS_API_BASE_URL}/top-headlines",
                    headers=headers,
                    params={"category": "business", "pageSize": 100, "language": "en"},
                ),
                client.get(
                    f"{NEWS_API_BASE_URL}/everything",
                    headers=headers,
                    params={
                        "q": "startup funding acquisition IPO",
                        "pageSize": 100,
                        "language": "en",
                        "sortBy": "publishedAt",
                    },
                ),
            )

        articles: list[SourceArticle] = []
        for response in responses:
            response.raise_for_status()
            payload = response.json()
            for article in payload.get("articles", []):
                parsed = self._parse_newsapi_article(article)
                if parsed is not None:
                    articles.append(parsed)
        return articles

    async def fetch_rss_articles(self) -> list[SourceArticle]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            responses = await asyncio.gather(*[client.get(feed_url) for feed_url in RSS_FEEDS])

        articles: list[SourceArticle] = []
        for response in responses:
            response.raise_for_status()
            parsed_feed = feedparser.parse(response.text)
            feed_title = getattr(parsed_feed.feed, "title", None) or "RSS Feed"
            for entry in parsed_feed.entries:
                parsed = self._parse_rss_entry(entry, feed_title=feed_title)
                if parsed is not None:
                    articles.append(parsed)
        return articles

    def _parse_newsapi_article(self, payload: dict[str, Any]) -> SourceArticle | None:
        title = (payload.get("title") or "").strip()
        url = payload.get("url")
        published_at = payload.get("publishedAt")
        if not title or not url or not published_at:
            return None

        content_parts = [
            payload.get("description"),
            payload.get("content"),
        ]
        raw_content = truncate_text(" ".join(part for part in content_parts if part))
        source_name = (payload.get("source") or {}).get("name") or "Unknown"

        return SourceArticle(
            title=title,
            url=url,
            source_name=source_name,
            published_at=date_parser.isoparse(published_at),
            raw_content=raw_content,
            image_url=payload.get("urlToImage"),
        )

    def _parse_rss_entry(self, entry: Any, *, feed_title: str) -> SourceArticle | None:
        title = strip_html(getattr(entry, "title", None) or "")
        url = getattr(entry, "link", None)
        published_at = getattr(entry, "published", None) or getattr(entry, "updated", None)
        if not title or not url or not published_at:
            return None

        content = None
        if getattr(entry, "content", None):
            content = " ".join(
                strip_html(item.get("value")) or "" for item in entry.content if isinstance(item, dict)
            ).strip()
        if not content:
            content = strip_html(getattr(entry, "summary", None))

        media_content = getattr(entry, "media_content", None) or []
        image_url = None
        for item in media_content:
            if isinstance(item, dict) and item.get("url"):
                image_url = item["url"]
                break
        if image_url is None:
            media_thumbnails = getattr(entry, "media_thumbnail", None) or []
            for item in media_thumbnails:
                if isinstance(item, dict) and item.get("url"):
                    image_url = item["url"]
                    break

        return SourceArticle(
            title=title,
            url=url,
            source_name=feed_title,
            published_at=date_parser.parse(published_at),
            raw_content=truncate_text(content),
            image_url=image_url,
        )

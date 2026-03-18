from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.article import Article
from app.models.user import User


class WeeklyDigestService:
    def __init__(self) -> None:
        self.settings = get_settings()
        template_dir = Path(__file__).resolve().parents[1] / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_weekly_digests(self, session: AsyncSession) -> int:
        result = await session.execute(select(User))
        users = list(result.scalars().all())
        sent = 0
        for user in users:
            articles = await self._select_articles_for_user(session, user)
            if not articles:
                continue
            html = self._render_digest(user.name, articles)
            delivered = await self._send_email(user.email, html)
            if delivered:
                sent += 1
        return sent

    async def _select_articles_for_user(self, session: AsyncSession, user: User) -> list[Article]:
        cutoff = datetime.now(UTC) - timedelta(days=7)
        preferences = user.preferences or {}
        query = select(Article).where(Article.published_at >= cutoff)
        regions = preferences.get("regions", [])
        if regions:
            query = query.where(Article.region.in_(regions))
        query = query.order_by(desc(Article.impact_score), desc(Article.published_at)).limit(10)
        return list((await session.execute(query)).scalars().all())

    def _render_digest(self, name: str, articles: list[Article]) -> str:
        template = self.environment.get_template("weekly_digest.html")
        return template.render(name=name, articles=articles, base_url=self.settings.app_base_url)

    async def _send_email(self, email: str, html: str) -> bool:
        if not self.settings.sendgrid_api_key or not self.settings.sendgrid_from_email:
            return False
        payload = {
            "personalizations": [{"to": [{"email": email}]}],
            "from": {"email": self.settings.sendgrid_from_email, "name": "BriefBiz"},
            "subject": "Your BriefBiz Weekly Digest",
            "content": [{"type": "text/html", "value": html}],
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {self.settings.sendgrid_api_key}"},
                    json=payload,
                )
                response.raise_for_status()
            return True
        except Exception:
            return False

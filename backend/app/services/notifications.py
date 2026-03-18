from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    async def create_company_notifications(
        self,
        session: AsyncSession,
        *,
        article_id: int,
        company_names: list[str],
    ) -> int:
        if not company_names:
            return 0

        normalized = {name.casefold() for name in company_names}
        result = await session.execute(select(User))
        users = list(result.scalars().all())
        created = 0
        for user in users:
            followed = {
                item.casefold()
                for item in (user.preferences or {}).get("followed_companies", [])
                if isinstance(item, str)
            }
            if not followed.intersection(normalized):
                continue
            session.add(Notification(user_id=user.id, article_id=article_id, type="followed_company"))
            created += 1
        return created

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notifications import MarkReadRequest, MarkReadResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[NotificationResponse]:
    result = await session.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.read.asc(), Notification.created_at.desc())
    )
    notifications = list(result.scalars().all())
    return [
        NotificationResponse(
            id=item.id,
            user_id=item.user_id,
            article_id=item.article_id,
            type=item.type,
            read=item.read,
            created_at=item.created_at,
        )
        for item in notifications
    ]


@router.post("/mark-read", response_model=MarkReadResponse)
async def mark_read(
    payload: MarkReadRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> MarkReadResponse:
    stmt = update(Notification).where(Notification.user_id == current_user.id)
    if payload.notification_ids:
        stmt = stmt.where(Notification.id.in_(payload.notification_ids))
    stmt = stmt.values(read=True)
    result = await session.execute(stmt)
    await session.commit()
    return MarkReadResponse(updated=result.rowcount or 0)


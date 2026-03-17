from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    article_id: int
    type: str
    read: bool
    created_at: datetime


class MarkReadRequest(BaseModel):
    notification_ids: list[int] = Field(default_factory=list)


class MarkReadResponse(BaseModel):
    updated: int


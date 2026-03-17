from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPreferencesPayload(BaseModel):
    sectors: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    followed_companies: list[str] = Field(default_factory=list)
    followed_investors: list[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    preferences: dict[str, Any]
    created_at: datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UpdatePreferencesRequest(BaseModel):
    sectors: list[str] | None = None
    regions: list[str] | None = None
    followed_companies: list[str] | None = None
    followed_investors: list[str] | None = None


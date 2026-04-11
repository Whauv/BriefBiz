from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

PBKDF2_SCHEME = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
PBKDF2_SALT_BYTES = 16


def _b64encode(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode(value + padding)


def _pbkdf2_digest(password: str, salt: bytes, iterations: int) -> bytes:
    return pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def _verify_legacy_hash(password: str, password_hash: str) -> bool:
    try:
        from passlib.context import CryptContext
    except ImportError:
        return False

    try:
        legacy_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
        return legacy_context.verify(password, password_hash)
    except Exception:
        return False


def hash_password(password: str) -> str:
    salt = token_bytes(PBKDF2_SALT_BYTES)
    digest = _pbkdf2_digest(password, salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_SCHEME}${PBKDF2_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith(f"{PBKDF2_SCHEME}$"):
        try:
            _, iterations_raw, salt_raw, digest_raw = password_hash.split("$", maxsplit=3)
            iterations = int(iterations_raw)
            salt = _b64decode(salt_raw)
            stored_digest = _b64decode(digest_raw)
        except (TypeError, ValueError):
            return False

        candidate_digest = _pbkdf2_digest(password, salt, iterations)
        return compare_digest(candidate_digest, stored_digest)

    if password_hash.startswith("$2") or password_hash.startswith("$bcrypt-sha256$"):
        return _verify_legacy_hash(password, password_hash)

    return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "exp": expire_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

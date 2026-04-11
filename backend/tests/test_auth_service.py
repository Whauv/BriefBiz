from __future__ import annotations

from app.services.auth import hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("supersecure")

    assert password_hash.startswith("pbkdf2_sha256$")
    assert verify_password("supersecure", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_password_hash_is_salted() -> None:
    first_hash = hash_password("supersecure")
    second_hash = hash_password("supersecure")

    assert first_hash != second_hash

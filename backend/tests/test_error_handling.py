from __future__ import annotations


async def test_validation_errors_include_request_id(db_client):
    response = await db_client.post(
        "/auth/register",
        headers={"X-Request-ID": "req-123"},
        json={"email": "not-an-email", "password": "short", "name": ""},
    )

    assert response.status_code == 422
    assert response.json()["request_id"] == "req-123"


async def test_not_found_error_includes_request_id(db_client):
    response = await db_client.get("/articles/999999", headers={"X-Request-ID": "req-404"})

    assert response.status_code == 404
    assert response.json()["request_id"] == "req-404"

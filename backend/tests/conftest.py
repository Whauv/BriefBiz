from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()


class ScalarSequence:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values

    def unique(self):
        return self


class ExecuteResult:
    def __init__(self, *, scalar_one_or_none=None, scalar_one=None, scalars=None, all_rows=None):
        self._scalar_one_or_none = scalar_one_or_none
        self._scalar_one = scalar_one
        self._scalars = scalars or []
        self._all_rows = all_rows or []

    def scalar_one_or_none(self):
        return self._scalar_one_or_none

    def scalar_one(self):
        if self._scalar_one is not None:
            return self._scalar_one
        return self._scalar_one_or_none

    def scalars(self):
        return ScalarSequence(self._scalars)

    def all(self):
        return self._all_rows


@pytest.fixture
def execute_result() -> type[ExecuteResult]:
    return ExecuteResult


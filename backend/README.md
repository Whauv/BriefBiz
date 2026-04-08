# BriefBiz Backend

FastAPI application, async infrastructure clients, and Celery workers for the BriefBiz platform.

## Migrations

Apply the initial schema with:

```bash
alembic upgrade head
```

## Tests

If your local Python environment is inconsistent, use the containerized test runner from the repository root:

```bash
docker compose --profile test run --rm api-test
```

That runs the backend test suite inside the same image used by the API service.

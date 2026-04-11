# BriefBiz Backend

This folder contains the FastAPI application, SQLAlchemy models, Alembic migrations, Celery workers, and backend services for BriefBiz.

For the full project setup, architecture, environment variables, Docker flow, and deployment steps, use the root README:

- [README.md](C:\Users\prana\OneDrive\Documents\Playground\BriefBiz\README.md)

## Backend Quick Start

```bash
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

## Backend Tests

```bash
python -m compileall app tests
python -m pytest tests
```

If the local Python environment is inconsistent, use the containerized runner from the repo root:

```bash
docker compose --profile test run --rm api-test
```

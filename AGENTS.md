# BriefBiz Agents Guide

## Overview

BriefBiz is a full-stack monorepo with:

- `backend/`: FastAPI API, async services, Celery workers, Alembic migrations, and backend tests
- `frontend/`: React + TypeScript + Vite application
- root infra files: Docker Compose, Cloud Build, GitHub Actions, and project documentation

## Setup Commands

### Full stack with Docker

```bash
docker compose up --build
```

### Backend local development

```bash
cd backend
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend local development

```bash
cd frontend
npm install
npm run dev
```

### Workers

```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
celery -A app.workers.celery_app.celery_app beat --loglevel=info
```

## Folder Map

- `backend/app/api/`: FastAPI routers, dependencies, and API composition
- `backend/app/core/`: application config, middleware, exceptions, logging, and rate limits
- `backend/app/db/`: database base classes and session management
- `backend/app/models/`: SQLAlchemy ORM models
- `backend/app/schemas/`: Pydantic request/response schemas
- `backend/app/services/`: domain and integration services
- `backend/app/workers/`: Celery app and task orchestration
- `backend/tests/`: backend route and architecture tests
- `frontend/src/components/`: reusable UI building blocks
- `frontend/src/pages/`: route-level screens
- `frontend/src/hooks/`: React Query and session hooks
- `frontend/src/store/`: client state container
- `frontend/src/utils/`: API helpers, mock data, and shared frontend utilities

## Code Style

- Python: async-first FastAPI patterns, Pydantic v2, typed services, small route handlers
- TypeScript: typed React components and hooks, route-level composition in `pages/`
- Config: environment-driven configuration only, no secrets committed
- Tests: backend tests use `pytest`; frontend placeholder tests live under `frontend/tests/`

## Test Commands

### Backend

```bash
cd backend
ruff check .
python -m pytest
```

### Frontend

```bash
cd frontend
npm run build
```

### Containerized backend tests

```bash
docker compose --profile test run --rm api-test
```

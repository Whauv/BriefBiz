# Contributing to BriefBiz

Thanks for contributing to BriefBiz.

## Development Setup

1. Clone the repository.
2. Create `backend/.env` from `backend/.env.example`.
3. Start local dependencies with Docker:

```bash
docker compose up postgres redis elasticsearch
```

4. Start the backend:

```bash
cd backend
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

5. Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

6. Start background jobs when working on ingestion or enrichment:

```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
celery -A app.workers.celery_app.celery_app beat --loglevel=info
```

## Branching

- Create feature branches from `main`.
- Use focused pull requests with clear titles and descriptions.
- Keep infrastructure, backend, and frontend changes grouped logically when possible.

## Coding Guidelines

- Backend code should use async-first FastAPI patterns.
- Use Pydantic v2 models for request and response contracts.
- Keep configuration in environment variables.
- Frontend components should be fully typed with TypeScript interfaces.
- Prefer small, testable service modules over large route handlers.

## Verification

Run the checks relevant to your changes before opening a pull request.

Backend:

```bash
cd backend
python -m compileall app alembic tests
pytest
```

Frontend:

```bash
cd frontend
npm run build
```

Containers:

```bash
docker compose config
```

## Pull Requests

Please include:

- a concise summary of the change
- screenshots or short recordings for UI work
- notes about schema, worker, or deployment changes
- test coverage or manual verification steps

## Reporting Security Issues

Please do not open public issues for sensitive vulnerabilities. Follow the guidance in `SECURITY.md`.

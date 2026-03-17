# BriefBiz

BriefBiz is an AI-powered business and startup news platform inspired by short-form news experiences, built for global business, venture, startup, and market-moving stories.

## Repository Structure

```text
BriefBiz/
|- backend/    FastAPI, Celery, PostgreSQL, Redis, Elasticsearch
|- frontend/   React, TypeScript, Vite, Tailwind CSS, Framer Motion
`- docker-compose.yml
```

## Current Status

Phase 1 is complete:

- FastAPI backend scaffold with async infrastructure clients
- Celery worker bootstrap with Redis broker/backend
- PostgreSQL and Elasticsearch connection setup
- React + TypeScript + Vite frontend scaffold
- Tailwind CSS, React Query, React Router, Axios, and Framer Motion configured
- Docker Compose for local infrastructure

## Quick Start

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd BriefBiz
```

### 2. Backend environment

Copy the backend environment template and fill in real values:

```bash
cp backend/.env.example backend/.env
```

### 3. Start infrastructure with Docker

```bash
docker compose up --build
```

This currently starts:

- `api`
- `worker`
- `postgres`
- `redis`
- `elasticsearch`

## Local Development

### Backend

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Backend values are defined in `backend/.env.example`:

- `DATABASE_URL`
- `REDIS_URL`
- `ELASTICSEARCH_URL`
- `OPENAI_API_KEY`
- `NEWS_API_KEY`
- `GOOGLE_TTS_KEY`
- `JWT_SECRET`

## GitHub Setup Checklist

- Create a new GitHub repository
- Push this folder as the repository root
- Add GitHub repository secrets later if you enable CI/CD with deployments
- Choose and add a license if you want the repository to be open source

## Next Build Phases

- Phase 2: SQLAlchemy models + Alembic migrations
- Phase 3: News ingestion pipeline
- Phase 4: AI summarization and enrichment workers
- Phase 5: REST API endpoints
- Phase 6: Frontend product UI
- Phase 7: Unique platform features
- Phase 8: Deployment and production infrastructure

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

Current `main` includes Phases 1-4:

- Phase 1: monorepo scaffold, FastAPI backend, React frontend, Docker Compose, Redis, PostgreSQL, and Elasticsearch wiring
- Phase 2: SQLAlchemy models for users, articles, companies, bookmarks, reactions, and notifications plus Alembic migrations
- Phase 3: scheduled ingestion pipeline for NewsAPI and RSS sources with deduplication, GPT-based classification, region extraction, company extraction, and Celery Beat
- Phase 4: article enrichment worker for summaries, deep dives, sentiment, impact score, `why_it_matters`, source quality scoring, Google TTS audio generation, and Elasticsearch indexing

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
- `beat`
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

Apply migrations after the database is running:

```bash
alembic upgrade head
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

## Backend Capabilities

- Async FastAPI application with Redis, Celery, PostgreSQL, and Elasticsearch integration
- Scheduled news ingestion every 15 minutes from NewsAPI and curated RSS feeds
- URL-hash deduplication before insert
- GPT-4o-mini powered vertical classification, region extraction, and company extraction
- Enrichment worker for 60-word summaries, deep-dive JSON, sentiment, impact score, and `why_it_matters`
- Google Cloud Text-to-Speech MP3 generation and local `/media` serving

## GitHub Setup Checklist

- Create a new GitHub repository
- Push this folder as the repository root
- Add GitHub repository secrets later if you enable CI/CD with deployments
- Choose and add a license if you want the repository to be open source

## Next Build Phases

- Phase 5: REST API endpoints
- Phase 6: Frontend product UI
- Phase 7: Unique platform features
- Phase 8: Deployment and production infrastructure

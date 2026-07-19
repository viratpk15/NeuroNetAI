# NeuroNet AI

Multi-agent collaboration intelligence platform. Ingests exported team
communication data (Slack/GitHub/Jira/etc.) and turns it into searchable
knowledge and insights.

## Status: Phase 1 of 4 — foundation

This repo is being built in phases so every commit is real, runnable code
with no placeholders or stubs pretending to be finished features. **What's
here right now:**

- FastAPI backend, clean-architecture layout (`domain` → `application` →
  `infrastructure` → `api`), fully working **Projects** CRUD, async
  SQLAlchemy against Supabase Postgres, unit tests for the service layer.
- Next.js 15 + Tailwind frontend shell with a Dashboard and a Projects page
  that are wired to the real API (create/list/archive/delete all work).
- Docker Compose for local dev, `.env.example` files, no secrets committed.

**Not built yet** (this is the honest roadmap, not a feature list to fake):

- Phase 2: Data import (starting with GitHub Issues/PRs) + first two
  LangGraph agents (Task Extraction, Sentiment) writing real results to the
  database.
- Phase 3: AI Chat (project-aware, using imported data + agent output) and
  Dashboard metrics backed by real analysis instead of "phase 2" placeholders.
- Phase 4: Knowledge graph, analytics, risk detection, reports, remaining
  agents, docs generator.

## Architecture

```
backend/
  app/
    domain/          # entities + repository interfaces, zero framework deps
    application/      # use cases (ProjectService), testable without a DB
    infrastructure/    # SQLAlchemy models, Postgres repository impl
    api/              # FastAPI routes, request/response schemas, DI wiring
  tests/
frontend/
  src/
    app/             # Next.js App Router pages (Dashboard, Projects)
    components/       # Sidebar, shared UI
    lib/api.ts        # typed fetch client for the backend
```

The dependency direction is strict: `api` → `application` → `domain` ←
`infrastructure`. Business logic (`ProjectService`) never imports FastAPI or
SQLAlchemy, which is why `tests/test_project_service.py` can test it with an
in-memory fake repository — no database needed to run the test suite.

## Setup

### 1. Supabase

Create a project at supabase.com, then grab the Postgres connection string
from **Project Settings → Database → Connection string (URI)**.

### 2. Backend

```bash
cd backend
cp .env.example .env        # paste your Supabase DATABASE_URL in here
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs
Tables are auto-created on startup in development mode (via SQLAlchemy
metadata). For production, switch to Alembic migrations before your first
deploy — auto-create is a dev convenience, not a migration strategy.

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

App: http://localhost:3000

### 4. Or, both at once with Docker

```bash
docker compose up
```

## Running tests

```bash
cd backend
pytest
```

`test_project_service.py` exercises create/rename/archive/delete/validation
against an in-memory repository — it's a real check of the business logic,
not a smoke test.

## Next step

Say the word and I'll build phase 2: GitHub Issues/PR import + the first
two LangGraph agents, writing real analysis results into the `documents`
table this repo already has.

# NeuroNet AI

Multi-agent collaboration intelligence platform. Ingests exported team
communication data (Slack/GitHub/Jira/etc.) and turns it into searchable
knowledge and insights.

## Status: v0.6 Complete — AI Reports & Export Center

**What's implemented:**

- ✅ v0.2 Import Engine: Markdown, TXT, GitHub Issues, GitHub PRs
- ✅ v0.2 AI Intelligence Engine: Conversation, Task, Sentiment, Entity agents
- ✅ v0.3 Workspace: Project AI analysis view with task board and sentiment
- ✅ v0.4 Intelligence Dashboard: Cross-project analytics
- ✅ v0.5 Knowledge Graph + AI Chat: Interactive graph and Q&A
- ✅ v0.6 Reports & Export: Multi-format report generation

## Architecture

```
backend/
  app/
    domain/          # entities + repository interfaces, zero framework deps
    application/      # use cases, AI agents, analysis service
    infrastructure/    # SQLAlchemy models, Postgres repository impl, parsers
    api/              # FastAPI routes, request/response schemas, DI wiring
  tests/
frontend/
  src/
    app/             # Next.js App Router pages
    components/       # Reusable UI components (16 total)
    lib/api.ts        # typed fetch client for the backend
```

Clean Architecture: `api` → `application` → `domain` ← `infrastructure`

## Setup

### 1. Supabase

Create a project at supabase.com, then grab the Postgres connection string
from **Project Settings → Database → Connection string (URI)**.

### 2. Backend

```bash
cd backend
cp .env.example .env        # paste your DATABASE_URL
uv venv
source .venv/bin/activate
uv sync --all-extras
uv run uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

App: http://localhost:3000

### 4. Docker

```bash
docker compose up
```

## Running tests

```bash
cd backend
uv run pytest
```

**56 tests passing**

## API Endpoints

### Projects
```
POST   /api/v1/projects     # Create project
GET    /api/v1/projects     # List projects
GET    /api/v1/projects/{id} # Get project
PATCH  /api/v1/projects/{id} # Update project
DELETE /api/v1/projects/{id} # Delete project
```

### Imports
```
POST   /api/v1/imports/markdown
POST   /api/v1/imports/txt
POST   /api/v1/imports/github-issue
POST   /api/v1/imports/github-pr
GET    /api/v1/imports/{job_id}
GET    /api/v1/imports
```

### Analysis
```
POST   /api/v1/analysis/{project_id}    # Run AI analysis
GET    /api/v1/analysis/{project_id}    # Get analysis results
GET    /api/v1/analysis/{project_id}/tasks
GET    /api/v1/analysis/{project_id}/sentiment
GET    /api/v1/analysis/{project_id}/entities
```

## Frontend Routes

| Route | Page | Size |
|-------|------|------|
| /dashboard | Intelligence Dashboard | 2.6 kB |
| /workspace/[projectId] | AI Workspace | 3.4 kB |
| /chat | AI Chat | 1.9 kB |
| /graph | Knowledge Graph | 1.6 kB |
| /reports | Reports & Export | 2.5 kB |
| /projects | Projects | 1.7 kB |

## Export Formats

- **PDF** - Text-based report
- **Markdown** - `.md` with sections
- **JSON** - Full analysis data
# Contributing

Thank you for your interest in contributing to NeuroNet AI!

## Development Setup

### Backend
```bash
cd backend
uv venv
source .venv/bin/activate
uv sync --all-extras
uv run uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Lint
```bash
cd frontend
npm run lint
npm run build
```

## Architecture

This project follows Clean Architecture:

```
backend/
  app/
    domain/          # Entities + Repository interfaces
    application/      # Use cases + AI Agents
    infrastructure/   # SQLAlchemy models + Repository implementations
    api/              # FastAPI routes + Schemas
```

## Code Style

- Python: Format with ruff, follow PEP 8
- TypeScript: Follow ESLint rules, use functional components
- Max 250 lines per file for maintainability

## Pull Request Process

1. Ensure all tests pass
2. Run linters (no warnings)
3. Update documentation if needed
4. Add tests for new features
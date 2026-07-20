# NeuroNet AI - Deployment Guide

## Quick Start

### Local Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/viratpk15/NeuroNetAI.git
   cd NeuroNetAI
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your values
   
   # Frontend  
   cp frontend/.env.local.example frontend/.env.local
   # Edit frontend/.env.local with API URL
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Deployment

```bash
# Terminal 1 - Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | development | Set to "production" for production |
| `CORS_ORIGINS` | Yes | - | Comma-separated allowed origins (e.g., `https://app.example.com`) |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (Supabase recommended) |
| `CHROMA_DB_PATH` | No | ./chroma_data | Path for vector store persistence |
| `MODEL_PROVIDER` | No | gemini | AI provider: gemini, ollama, or groq |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `GEMINI_MODEL` | No | gemini-2.5-flash | Gemini model to use |
| `GROQ_API_KEY` | If using Groq | - | Groq API key |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | http://localhost:8000/api/v1 | Backend API URL |

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set up managed PostgreSQL database (Supabase)
- [ ] Configure HTTPS with reverse proxy (nginx/Caddy)
- [ ] Set up persistent volume for Chroma DB
- [ ] Configure rate limiting
- [ ] Set up monitoring (optional)

## Docker Production Build

```bash
# Build all images
docker-compose build

# Push to registry (if needed)
docker tag neuronet-ai-backend your-registry/neuronet-ai-backend:latest
docker tag neuronet-ai-frontend your-registry/neuronet-ai-frontend:latest
```

## Security Notes

- All Dockerfiles run as non-root user
- No secrets are committed to the repository
- CORS is configured via environment variable
- Health check endpoints are available for monitoring

## Troubleshooting

### Backend won't start
- Check `DATABASE_URL` is correct
- Verify `CORS_ORIGINS` includes your frontend URL
- Ensure `GEMINI_API_KEY` is valid

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running on specified port
- Check CORS configuration in backend

### Import fails silently
- Check backend logs for errors
- Verify document parsing format (TXT/Markdown/GitHub JSON)
- Ensure project ID is valid
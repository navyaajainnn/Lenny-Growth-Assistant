# Lenny Growth Assistant

An AI research desk for grounded product and growth questions from Lenny's Podcast transcripts.

## Current implementation

- FastAPI backend with PostgreSQL sessions and messages
- Local Ollama support using `qwen3:4b` by default
- Optional Anthropic provider selected with `LLM_PROVIDER`
- Official Claude Agent SDK provider selected with `LLM_PROVIDER=claude_agent`
- Transcript ingestion, lexical retrieval, and source metadata
- Ship 30 for 30-style essay skill
- Markdown and sandboxed HTML artifact generation
- React frontend with an in-app Artifact Viewer

## Run locally

Start PostgreSQL and Ollama, then follow [backend/README.md](backend/README.md) for Python setup, schema initialization, transcript ingestion, and API commands. Run the frontend with:

```powershell
cd frontend
npm install
npm run dev
```

Download the public transcript archive before ingestion:

```powershell
python scripts/download_transcripts.py
cd backend
python -m app.ingest ..\data\transcripts
```

Or start PostgreSQL, backend, and frontend together with:

```powershell
docker compose up --build
```

The frontend runs at http://localhost:5173 and API docs at http://localhost:8000/docs.
Compose uses `local-dev-only` for the disposable local database by default and exposes it on host port `5433` to avoid conflicts with an existing PostgreSQL service. Set `POSTGRES_PASSWORD` from a secret manager before using this topology outside local development.

After the stack is running, index the downloaded transcripts into the Compose database:

```powershell
docker compose run --rm backend python -m app.ingest /data/transcripts
```

## Documentation

- [Product requirements](docs/PRD.md)
- [Architecture](docs/architecture.md)
- [Design](docs/design.md)

## Security and data

Secrets belong in local `.env` files or a secret manager; `.env.example` contains placeholders only. Downloaded transcript contents are ignored by Git because the upstream archive requests personal and educational use. The frontend renders generated HTML in a sandboxed iframe.

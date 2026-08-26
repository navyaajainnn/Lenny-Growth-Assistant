# Lenny Growth Assistant Backend

Phase 3 provides the FastAPI foundation, asynchronous Ollama provider, independent chat sessions, PostgreSQL persistence, and a transcript knowledge base. It intentionally does not implement agent routing, cloud providers, frontend features, or artifact generation.

## Prerequisites

- Python 3.12+
- Ollama installed and running locally
- PostgreSQL 15+ running locally or a PostgreSQL-compatible hosted database
- The local model pulled with:

```powershell
ollama pull qwen3:4b
```

`qwen3:4b` is an implementation decision selected for the available development machine. The model and Ollama URL are configurable through environment variables.

## Setup

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.init_db
```

Never commit `.env`; it is ignored by git. Ollama requires no API key; the optional Anthropic key belongs only in local environment configuration or a secret manager.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `Lenny Growth Assistant API` | FastAPI application title |
| `ENVIRONMENT` | `development` | Environment label returned by health checks |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth_assistant` | Async PostgreSQL connection string |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen3:4b` | Local model name |
| `OLLAMA_TIMEOUT_SECONDS` | `12` | Provider request timeout before grounded excerpt fallback |
| `OLLAMA_MAX_OUTPUT_TOKENS` | `384` | Maximum local response length |
| `FRONTEND_URL` | `http://localhost:5173` | Allowed browser origin |
| `LLM_PROVIDER` | `ollama` | `ollama` or `anthropic` |
| `ANTHROPIC_API_KEY` | empty | Optional cloud-provider secret |
| `ANTHROPIC_MODEL` | `claude-3-5-haiku-latest` | Optional cloud model |

## Full stack startup

Docker Compose starts PostgreSQL, the backend, and the frontend. Ollama must already be running on the host:

```powershell
docker compose up --build
```

Open http://localhost:5173. The backend API and docs are available at http://localhost:8000/docs.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at http://127.0.0.1:8000. Verify the health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","environment":"development"}
```

## Chat API

Create a session:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/sessions -ContentType "application/json" -Body '{"user_metadata":{"source":"local"}}'
```

Send a message using the returned session ID:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/sessions/<session-id>/messages -ContentType "application/json" -Body '{"content":"How do I improve activation?"}'
```

The API stores the user and assistant messages in PostgreSQL. The message route depends on the `LLMProvider` interface, so a future provider can be added without changing the route contract.

## Transcript knowledge base

Place `.txt`, `.md`, or JSON transcript files under `data/transcripts`. JSON files may contain either one object or a list of objects with a `text` field and an optional `source` field. Files are split into overlapping word chunks and indexed in the `transcript_chunks` PostgreSQL table.

Run ingestion after adding or refreshing transcripts:

```powershell
python -m app.ingest ..\data\transcripts
```

Ingestion replaces the existing chunk index, making refreshes repeatable. Retrieval uses deterministic lexical term matching in Phase 3, and each assistant response includes the matching source filename and score in its `sources` field. The prompt explicitly instructs the local model to acknowledge when no transcript context supports an answer.

## Tests

```powershell
python -m pytest
```

If Ollama exceeds the timeout or is unavailable, the API returns a definite grounded response made from the retrieved transcript excerpts and still includes source metadata. The tests use an in-memory SQLite database and mocked HTTP/provider responses; they do not require PostgreSQL or Ollama. A live integration check can be performed with:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

The official Claude Agent SDK is optional and is selected with `LLM_PROVIDER=claude_agent`. It requires an Anthropic credential and may incur usage charges. The default `LLM_PROVIDER=ollama` path remains local and free of Anthropic charges.

## Extending the provider layer

API routes depend on the `LLMProvider` protocol rather than provider-specific details. Set `LLM_PROVIDER=claude_agent` with `ANTHROPIC_API_KEY` to use the official Claude Agent SDK. The adapter is deliberately limited to one turn with no tools enabled; transcript context is retrieved by the application and passed into the prompt. Ollama remains the default. Cloud fallback is intentionally not automatic to avoid unexpected data sharing.

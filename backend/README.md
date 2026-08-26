# Lenny Growth Assistant Backend

This backend provides FastAPI session APIs, PostgreSQL persistence, grounded transcript retrieval, configurable local and cloud providers, and Markdown/HTML artifact generation for the Lenny Growth Assistant.

## Prerequisites

- Python 3.12+
- Ollama installed and running locally
- PostgreSQL 15+ running locally or a PostgreSQL-compatible hosted database
- The local model pulled with:

```powershell
ollama pull qwen2.5:1.5b
```

`qwen2.5:1.5b` is an implementation decision selected for the available development machine. It avoids the slow reasoning phase observed with `qwen3:4b`; the model and Ollama URL are configurable through environment variables.

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
| `TRANSCRIPT_DIRECTORY` | repository `data/transcripts` directory | Transcript archive indexed when the database index is empty |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Local model name |
| `OLLAMA_TIMEOUT_SECONDS` | `60` | Provider request timeout before grounded excerpt fallback |
| `OLLAMA_MAX_OUTPUT_TOKENS` | `512` | Maximum local answer length |
| `OLLAMA_ARTIFACT_TIMEOUT_SECONDS` | `180` | Longer timeout for the Ship 30 for 30 artifact skill |
| `OLLAMA_ARTIFACT_MAX_OUTPUT_TOKENS` | `1800` | Output budget for the approximately 1,250-word artifact |
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

The application automatically performs this ingestion at startup when `transcript_chunks` is empty; this covers a new local database and Docker Compose volume. It does not replace a non-empty index on restart. Ingestion replaces the existing chunk index when explicitly run, making refreshes repeatable. Retrieval uses deterministic lexical term matching in Phase 3, and each assistant response includes the matching source filename and score in its `sources` field. The prompt explicitly instructs the local model to acknowledge when no transcript context supports an answer.

## Tests

```powershell
python -m pytest
```

If Ollama exceeds the timeout or is unavailable, the API returns a definite grounded response made from the retrieved transcript excerpts and still includes source metadata. The tests use an in-memory SQLite database and mocked HTTP/provider responses; they do not require PostgreSQL or Ollama. A live integration check can be performed with:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## Manual UI test plan

1. Start the Compose stack and open http://localhost:5173.
2. Ask `How can a product team improve activation?`; verify an answer and one or more source chips appear.
3. Send a follow-up such as `Give me three actions for this week`; verify the assistant uses the same session context.
4. Click **Markdown** then **Generate**; verify a rendered document appears in the Artifact Viewer. On CPU-only machines this may take one to two minutes.
5. Click **HTML** then **Generate**; verify the result renders in the sandboxed iframe and does not navigate the page.
6. Ask an unrelated question, such as `What is the best carbonara recipe?`; verify the assistant acknowledges that the archive does not support an answer.

## Troubleshooting

- If answers show grounded excerpts instead of a written response, the local model exceeded its timeout. Check that Ollama is running and that `qwen2.5:1.5b` is installed with `ollama pull qwen2.5:1.5b`.
- If a local Ollama server has been running for a long time and generation stalls, restart it, then retry the request.
- If the browser shows a database error, use only one backend on port 8000. Compose is reached at `http://localhost:8000`; the frontend is configured for that address.

The official Claude Agent SDK is optional and is selected with `LLM_PROVIDER=claude_agent`. It requires an Anthropic credential and may incur usage charges. The default `LLM_PROVIDER=ollama` path remains local and free of Anthropic charges.

## Extending the provider layer

API routes depend on the `LLMProvider` protocol rather than provider-specific details. Set `LLM_PROVIDER=claude_agent` with `ANTHROPIC_API_KEY` to use the official Claude Agent SDK. The adapter is deliberately limited to one turn with no tools enabled; transcript context is retrieved by the application and passed into the prompt. Ollama remains the default. Cloud fallback is intentionally not automatic to avoid unexpected data sharing.

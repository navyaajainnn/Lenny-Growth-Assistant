# Architecture

## Boundaries

The frontend calls a FastAPI backend. Routes depend on application services, which depend on repositories, retrieval, and the `LLMProvider` protocol. Ollama and Anthropic are interchangeable provider implementations selected through `LLM_PROVIDER`.

## Database schema

- `chat_sessions`: UUID, JSON user metadata, created/updated timestamps
- `messages`: UUID, session UUID, role, content, source metadata JSON, timestamp
- `transcript_chunks`: UUID, source path, chunk content, position
- `artifacts`: UUID, session UUID, format, content, timestamp

`python -m app.init_db` creates tables and adds the Phase 3/4 columns needed by existing databases.

## API endpoints

- `GET /health`
- `POST /sessions`
- `POST /sessions/{session_id}/messages`
- `POST /sessions/{session_id}/artifacts`

Requests use Pydantic validation. Provider, database, timeout, and missing-session failures map to structured JSON errors.

## Ingestion and retrieval

`python -m app.ingest <directory>` loads transcript Markdown/text/JSON files, splits them into overlapping chunks, and replaces the PostgreSQL chunk index. Phase 3 uses deterministic lexical retrieval. Each result retains its relative source path and score, which is returned with assistant messages.

## Agent and model routing

The application-level routing boundary is `create_provider()`, and all API routes consume `LLMProvider`. Ollama is the default local implementation. Anthropic is an optional cloud implementation requiring `ANTHROPIC_API_KEY`. Cloud fallback is explicit rather than automatic to prevent accidental data sharing.

## Security

Generated HTML is untrusted. The frontend renders it inside an iframe with an empty `sandbox` attribute, which blocks scripts, forms, navigation, and same-origin access. The prompt also forbids scripts, event handlers, and external resources. Markdown is rendered by ReactMarkdown rather than injected with `innerHTML`.

## Deployment topology

Docker Compose runs PostgreSQL, the backend, and the frontend. Local Ollama remains outside Compose and is reached through Docker Desktop's `host.docker.internal`. Production should replace default database credentials with a secret manager and put the services behind TLS.

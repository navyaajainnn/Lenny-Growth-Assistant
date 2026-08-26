# Product Requirements

## User and problem

The primary user is a product manager or growth practitioner who wants practical advice from Lenny's Podcast without manually searching hundreds of episodes. The assistant removes search time and turns scattered conversations into a grounded, actionable answer.

## Success metric

At least 80% of evaluated answers should cite a relevant transcript source, and a user should receive a first response in under two minutes on the local demo machine.

## Assumptions

- The transcript archive is available locally under its stated personal/educational use terms.
- Local Ollama is the default demo runtime.
- Users value traceable advice more than unsupported breadth.
- A later deployment will provide managed PostgreSQL and secret storage.

## Scope

Included: session-based grounded chat, transcript ingestion, source metadata, local/cloud provider configuration, Ship 30 for 30-style essay generation, Markdown/HTML artifacts, and an in-app sandboxed viewer.

Excluded from the current implementation: authentication, multi-tenant authorization, semantic embeddings, automatic cloud fallback, billing, and production hosting-specific integrations.

## User flow

1. User opens the research desk and receives a new session.
2. User asks a product or growth question.
3. The system retrieves transcript chunks and sends grounded context to the selected provider.
4. The answer displays with source paths.
5. User chooses Markdown or HTML and generates an artifact from the conversation.

## Acceptance criteria

- A session maintains independent conversation history.
- Unsupported questions receive an explicit no-support instruction.
- Assistant responses expose retrieved source metadata.
- Provider selection changes through environment configuration.
- HTML artifacts render in an isolated viewer.
- Database and provider failures produce structured errors; model timeouts preserve grounding through source-excerpt fallbacks.

## Risks and trade-offs

Local model quality and latency are lower than many cloud models. Lexical retrieval is transparent and dependency-light but misses synonyms. Source text and generated output require careful rights and privacy handling. Sandboxing reduces artifact capability in exchange for a safer viewer.

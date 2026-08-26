# Development History

This folder records the material implementation decisions, failed checks, and corrections made while building the project.

## Recorded milestones

- Read the assignment requirements before implementation.
- Built the FastAPI, Ollama, configuration, and health foundation.
- Added PostgreSQL sessions and provider-independent chat services.
- Imported the public transcript archive and fixed source attribution so episode paths remain distinct.
- Fixed test execution context issues caused by running from the repository root instead of `backend`.
- Fixed a database-unavailable path that initially returned 500 instead of structured 503.
- Fixed accidental frontend dependency staging by ignoring `node_modules` and `dist`.
- Added the official Claude Agent SDK as an optional, no-tool provider path while keeping Ollama as the default.
- Added reproducible data download, Compose readiness checks, migrations, logging, and final validation coverage.

No credentials, API keys, private transcript content, or local environment values are stored here.
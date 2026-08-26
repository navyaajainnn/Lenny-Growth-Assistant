# Oogway Labs — Lenny Growth Assistant

## Take-Home Assignment Requirements

> This document is a structured representation of the Oogway Labs Forward Deployed Engineer take-home assignment. The original `.docx` assignment remains the authoritative source.

---

## 1. Objective

Build and deploy **“The Lenny Growth Assistant”**, a full-stack, AI-powered conversational web application.

The application must:

* Ingest transcripts from Lenny’s Podcast.
* Answer complex product and growth questions.
* Generate highly formatted content grounded in the transcript knowledge base.
* Generate Markdown or HTML/CSS artifacts.
* Render generated artifacts natively inside the product.
* Provide a user-friendly experience where users do not need to understand prompts, models, or infrastructure.

The solution should be treated as a small forward-deployment engagement rather than only a coding exercise.

The implementation should demonstrate:

* Product judgment.
* Engineering judgment.
* AI system design.
* Clear assumptions.
* Sensible scope decisions.
* Communication of trade-offs.
* Operational handoff.

---

# 2. Forward Deployment Brief

The PRD must include a short discovery brief covering:

### User and Problem

Define:

* Who the primary user is.
* What job the user is trying to complete.
* What pain the assistant removes.

### Success Metric

Define at least one measurable product or operational success metric.

### Assumptions

Document important assumptions made because the client brief is incomplete.

### Scope Choices

Clearly state:

* What is included.
* What is intentionally excluded.
* Why those scope decisions were made.

### Risks and Trade-offs

Identify key risks, including relevant risks such as:

* Hallucination.
* Latency.
* Cost.
* Local-model quality.
* Data leakage.
* Unsafe artifact rendering.

---

# 3. Core Requirements

## 3.1 API, Sessions, and Persistence

### Backend

The backend API must use:

**FastAPI**

### Agent Integration

The agent layer must use either:

* Anthropic Claude Agent SDK
* Pi Coding Agent

### Sessions

Users must be able to:

* Start a new chat.
* Maintain independent session context.

Each session must maintain its own conversation context.

### Persistence

Use PostgreSQL to store:

* Conversations.
* Session IDs.
* Timestamps.
* User metadata.

Supabase or Railway may be used.

### API Quality

The API should provide:

* Clear request/response contracts.
* Validation.
* Structured errors.
* Health endpoints.

---

# 3.2 Flexible LLM Configuration

The application must allow the evaluator to switch the underlying model without changing application code.

### Cloud LLM

Integrate at least one cloud provider, such as:

* Anthropic Claude
* OpenAI

### Local LLM

Local LLM usage is mandatory for the demo.

The submitted demo must use:

**Ollama**

Use a model that works comfortably on the development machine.

### Model Toggle

The selected provider must be:

* Visible in the UI or configuration.
* Clearly documented.

Fallback behavior must also be documented.

---

# 3.3 Knowledge Base

### Data Source

Use transcripts from:

**Lenny’s Podcast / Newsletter transcript repository**

### Ingestion

Document how transcripts are:

* Loaded.
* Chunked or selected.
* Indexed.
* Refreshed.
* Traced back to their source.

### Grounding

Answers must cite or clearly identify the relevant transcript/source used.

---

# 4. Product Tasks

## 4.1 Grounded Conversational Assistant

Implement either:

* RAG
* Long-context system

The assistant must answer product management and growth questions strictly from Lenny’s transcripts.

The experience must:

* Handle follow-up questions.
* Preserve session context.
* Acknowledge when the available material does not support an answer.

The assistant should not invent unsupported information.

---

# 4.2 Ship 30 for 30 Content Skill

Create a dedicated skill or tool that turns grounded answers into a **Ship 30 for 30-style essay**.

The linked source should be read to identify relevant writing principles.

Those principles must be encoded in the skill rather than relying only on an unstructured one-off prompt.

### Essay Requirements

The generated essay should have:

* Approximately 1,250 words.
* A strong hook.
* Clear narrative progression.
* Skimmable formatting.
* Headings.
* Bullets.
* Selective bold emphasis.
* A specific, useful takeaway.
* Claims grounded in the transcript knowledge base.

---

# 4.3 Artifact Generation and In-App Viewer

When requested, the assistant must generate:

* Markdown documents
* OR complete HTML/CSS snippets

Generated artifacts must be based on the current conversation.

### Artifact Viewer

The frontend must include an **Artifact Viewer**, similar to Claude Artifacts.

The artifact should:

* Render beside the chat.
* Render natively inside the product.
* Not simply display raw code.
* Not redirect the user to another application.

### Security

Generated HTML must be treated as untrusted.

Implement and explain a reasonable:

* Isolation strategy
* OR sanitization strategy

The evaluator should be able to understand:

* What the viewer permits.
* What it blocks.
* Why those restrictions exist.

---

# 5. Deployment and Operational Readiness

The solution should be handed over in a form that another engineering team can operate.

## One-Command Startup

Provide a practical setup path.

Docker Compose or an equivalent reproducible workflow is preferred.

## Configuration

Provide:

`.env.example`

It must contain:

* Safe defaults.
* Required variables.
* Optional variables.

Never commit secrets.

## Observability

Add structured logs and enough visibility to diagnose:

* Model failures.
* Retrieval failures.
* Database failures.
* Artifact-rendering failures.

## Resilience

Handle failures gracefully, including:

* Missing API keys.
* Unavailable Ollama.
* Model timeouts.
* Empty retrieval results.
* Database connection failures.

## Handoff

Document how another engineer can:

* Run the system.
* Test the system.
* Troubleshoot the system.
* Extend the system.

---

# 6. Required Deliverables

## 6.1 Public GitHub Repository

Provide a public GitHub repository containing:

* Complete source code.
* Sensible project structure.
* No committed secrets.

## 6.2 README.md

Include:

* Architecture overview.
* Prerequisites.
* Installation instructions.
* Environment variables.
* Local model setup.
* Cloud model setup.
* Run commands.
* Tests.
* Troubleshooting.

## 6.3 PRD

Include:

* User.
* Problem.
* Success metric.
* Assumptions.
* Scope.
* User flows.
* Acceptance criteria.
* Risks.
* Implementation plan.

## 6.4 design.md

Include:

* UI/UX principles.
* Information architecture.
* Key interaction states.
* Responsive behavior.
* Accessibility considerations.
* Design decisions.

## 6.5 architecture.md

Include:

* Database schema.
* API endpoints.
* Component boundaries.
* Ingestion/retrieval flow.
* Agent routing.
* Model toggle.
* Security.
* Deployment topology.

## 6.6 Agent Transcripts

Include coding-agent transcripts/logs in a dedicated folder.

Include:

* Failed attempts.
* Corrections.
* Relevant development history.

Before committing:

* Remove secrets.
* Remove sensitive data.

## 6.7 Tests

Include meaningful automated tests covering critical:

* API behavior.
* Retrieval behavior.
* Routing behavior.
* Persistence behavior.

Also include a short manual test plan for the UI.

## 6.8 Demo Video

Create a:

**2–3 minute video**

Requirements:

* Camera enabled.
* Explain the problem.
* Show the product.
* Demonstrate local Ollama.
* Briefly explain one important technical trade-off.
* Upload the video to YouTube.

---

# 7. Submission

### Submission Form

https://forms.gle/LgotDHNVxW1mbzNE7

### Assignment Due Date

The assignment document states:

**25/08/26 EOD**

Before submitting, verify that a fresh evaluator can:

1. Clone the repository.
2. Follow the documented setup instructions.
3. Run the solution successfully.

The evaluator should not need undocumented setup steps.

---

# 8. Evaluation Criteria

The solution will be evaluated on:

## Customer and Product Judgment

* Discovery framing.
* Assumptions.
* Prioritization.
* Success metrics.
* Trade-off decisions.

## Technical Execution

End-to-end functionality across:

* UI.
* FastAPI.
* PostgreSQL.
* Agent layer.
* Retrieval.
* Model configuration.

## Agentic Architecture and Grounding

Evaluate:

* Skill boundaries.
* Reliable routing.
* Source-grounded answers.
* Sensible failure behavior.

## Deployment and Operability

Evaluate:

* Reproducibility.
* Observability.
* Resilience.
* Security.
* Documentation.
* Evaluator handoff.

## Code Quality

Evaluate:

* Separation of concerns.
* Readability.
* Maintainability.
* Validation.
* Error handling.
* Meaningful tests.

## UI/UX Quality

Evaluate:

* Polished chat experience.
* Understandable states.
* Useful artifact viewer.
* Responsive layout.
* Accessibility.

## Communication

Evaluate:

* PRD.
* Architecture documentation.
* Design rationale.
* README.
* Demo.
* Explanation of decisions.

---

# 9. Helpful Resources

The assignment identifies the following resources/topics:

* FastAPI
* Ollama
* Anthropic Claude Agent SDK
* Pi Coding Agent
* Supabase
* Railway
* Ship 30 for 30 guide
* Impeccable

---

# 10. AI-Assisted Development

The assignment explicitly encourages the thoughtful use of coding agents, including:

* Claude
* Codex
* Cursor
* Devin

The evaluation is focused on the candidate’s ability to:

* Direct AI-assisted development.
* Verify generated work.
* Improve generated work.
* Exercise engineering judgment.

The use of AI coding tools itself is not the evaluation target; the quality of the resulting engineering decisions and implementation is.

---

# 11. Mandatory Requirement Checklist

Before submission, verify:

* [ ] FastAPI backend
* [ ] Agent layer using Claude Agent SDK or Pi Coding Agent
* [ ] New chat/session functionality
* [ ] Independent session context
* [ ] PostgreSQL persistence
* [ ] Conversation persistence
* [ ] Session IDs
* [ ] Timestamps
* [ ] User metadata
* [ ] Request/response validation
* [ ] Structured API errors
* [ ] Health endpoint
* [ ] At least one cloud LLM provider
* [ ] Ollama local LLM
* [ ] Model/provider configuration
* [ ] Visible model/provider selection or configuration
* [ ] Documented fallback behavior
* [ ] Lenny transcript knowledge base
* [ ] Transcript ingestion
* [ ] Chunking/selection strategy
* [ ] Indexing
* [ ] Refresh strategy
* [ ] Source traceability
* [ ] Grounded answers
* [ ] Source citations/identification
* [ ] Follow-up questions
* [ ] Session context preservation
* [ ] Unsupported-question handling
* [ ] Dedicated Ship 30 for 30 skill/tool
* [ ] Approximately 1,250-word output
* [ ] Strong hook
* [ ] Narrative progression
* [ ] Skimmable formatting
* [ ] Useful takeaway
* [ ] Transcript-grounded claims
* [ ] Markdown artifact generation
* [ ] HTML/CSS artifact generation
* [ ] In-app Artifact Viewer
* [ ] Artifact rendering beside chat
* [ ] HTML sanitization/isolation
* [ ] Security explanation
* [ ] One-command/reproducible startup
* [ ] `.env.example`
* [ ] No committed secrets
* [ ] Structured logs
* [ ] Model failure handling
* [ ] Retrieval failure handling
* [ ] Database failure handling
* [ ] Artifact-rendering failure handling
* [ ] Missing API-key handling
* [ ] Ollama-unavailable handling
* [ ] Model timeout handling
* [ ] Empty retrieval handling
* [ ] README
* [ ] PRD
* [ ] design.md
* [ ] architecture.md
* [ ] Agent transcripts/logs
* [ ] Automated tests
* [ ] Manual UI test plan
* [ ] 2–3 minute demo video
* [ ] Camera enabled in demo
* [ ] Local Ollama demonstrated
* [ ] Technical trade-off explained
* [ ] Public GitHub repository
* [ ] Fresh-clone verification

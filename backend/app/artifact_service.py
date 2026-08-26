import uuid
from html import escape

from app.config import Settings
from app.knowledge import TranscriptRetriever
from app.providers.base import LLMProvider
from app.providers.base import LLMProviderError
from app.repositories import SessionRepository
from app.skills import build_artifact_prompt


class ArtifactService:
    def __init__(
        self,
        repository: SessionRepository,
        provider: LLMProvider,
        retriever: TranscriptRetriever,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._retriever = retriever
        self._settings = settings

    async def create(self, session_id: uuid.UUID, output_format: str):
        session = await self._repository.get(session_id)
        if session is None:
            from app.services import SessionNotFoundError

            raise SessionNotFoundError(str(session_id))
        messages = await self._repository.list_messages(session_id)
        query = messages[-1].content if messages else "product growth"
        retrieved = await self._retriever.retrieve(query)
        context = "\n\n".join(f"Source: {item.source}\n{item.content}" for item in retrieved)
        conversation = "\n".join(f"{message.role}: {message.content}" for message in messages)
        try:
            content = await self._provider.generate(
                build_artifact_prompt(conversation, context, output_format),
                max_output_tokens=self._settings.ollama_artifact_max_output_tokens,
                timeout_seconds=self._settings.ollama_artifact_timeout_seconds,
            )
        except LLMProviderError:
            content = self._fallback_artifact(retrieved, output_format)
        return await self._repository.add_artifact(session_id, output_format, content)

    @staticmethod
    def _fallback_artifact(retrieved, output_format: str) -> str:
        excerpts = "\n\n".join(
            f"## {item.source}\n\n{item.content[:1200].strip()}" for item in retrieved
        ) or "No relevant transcript excerpts were found."
        if output_format == "markdown":
            return "# Grounded research notes\n\nThe local model did not finish in time.\n\n" + excerpts
        return (
            "<article><h1>Grounded research notes</h1>"
            "<p>The local model did not finish in time.</p><pre>"
            + escape(excerpts)
            + "</pre></article>"
        )

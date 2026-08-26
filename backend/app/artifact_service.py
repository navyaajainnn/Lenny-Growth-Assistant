import uuid

from app.knowledge import TranscriptRetriever
from app.providers.base import LLMProvider
from app.repositories import SessionRepository
from app.skills import build_artifact_prompt


class ArtifactService:
    def __init__(
        self,
        repository: SessionRepository,
        provider: LLMProvider,
        retriever: TranscriptRetriever,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._retriever = retriever

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
        content = await self._provider.generate(
            build_artifact_prompt(conversation, context, output_format)
        )
        return await self._repository.add_artifact(session_id, output_format, content)

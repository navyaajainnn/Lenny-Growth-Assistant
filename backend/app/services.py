import uuid

from app.knowledge import TranscriptRetriever
from app.providers.base import LLMProvider
from app.providers.base import LLMProviderError
from app.repositories import SessionRepository


class SessionNotFoundError(Exception):
    pass


class ChatService:
    def __init__(
        self,
        repository: SessionRepository,
        provider: LLMProvider,
        retriever: TranscriptRetriever,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._retriever = retriever

    async def respond(self, session_id: uuid.UUID, content: str):
        session = await self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundError(str(session_id))

        user_message = await self._repository.add_message(session_id, "user", content)
        history = await self._repository.list_messages(session_id)
        retrieved = await self._retriever.retrieve(content)
        context = "\n\n".join(
            f"Source: {chunk.source}\n{chunk.content[:1800]}" for chunk in retrieved
        )
        grounding = (
            "Use only the transcript context below. If it does not support an answer, "
            "say that the available transcripts do not support an answer.\n\n"
            f"Transcript context:\n{context or '[No relevant transcript context found]'}"
        )
        conversation = "\n".join(f"{message.role}: {message.content}" for message in history)
        prompt = f"{grounding}\n\nConversation:\n{conversation}"
        sources = [
            {"source": chunk.source, "score": chunk.score} for chunk in retrieved
        ]
        try:
            response = await self._provider.generate(prompt)
        except LLMProviderError:
            response = self._fallback_response(retrieved)
        assistant_message = await self._repository.add_message(
            session_id, "assistant", response, sources=sources
        )
        return user_message, assistant_message

    @staticmethod
    def _fallback_response(retrieved) -> str:
        if not retrieved:
            return "The available transcripts do not support an answer."
        excerpts = "\n\n".join(
            f"From `{chunk.source}`:\n{chunk.content[:700].strip()}"
            for chunk in retrieved
        )
        return (
            "The local model did not respond in time, so here are the most relevant "
            "grounded transcript excerpts instead:\n\n" + excerpts
        )

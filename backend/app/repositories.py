import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database import DatabaseUnavailableError
from app.models import Artifact, ChatSession, Message

DATABASE_OPERATION_FAILED = "Database operation failed"


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, user_metadata: dict[str, Any]) -> ChatSession:
        try:
            session = ChatSession(user_metadata=user_metadata)
            self._db.add(session)
            await self._db.commit()
            await self._db.refresh(session)
            return session
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError(DATABASE_OPERATION_FAILED) from error

    async def get(self, session_id: uuid.UUID) -> ChatSession | None:
        try:
            return await self._db.get(ChatSession, session_id)
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError(DATABASE_OPERATION_FAILED) from error

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        sources: list[dict[str, Any]] | None = None,
    ) -> Message:
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                sources=sources or [],
            )
            self._db.add(message)
            await self._db.commit()
            await self._db.refresh(message)
            return message
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError(DATABASE_OPERATION_FAILED) from error

    async def list_messages(self, session_id: uuid.UUID) -> list[Message]:
        try:
            result = await self._db.execute(
                select(Message).where(Message.session_id == session_id).order_by(Message.created_at, Message.id)
            )
            return list(result.scalars())
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError(DATABASE_OPERATION_FAILED) from error

    async def add_artifact(self, session_id: uuid.UUID, output_format: str, content: str) -> Artifact:
        try:
            artifact = Artifact(session_id=session_id, format=output_format, content=content)
            self._db.add(artifact)
            await self._db.commit()
            await self._db.refresh(artifact)
            return artifact
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError(DATABASE_OPERATION_FAILED) from error

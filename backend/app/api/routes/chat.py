import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.artifact_service import ArtifactService
from app.database import get_session_factory
from app.knowledge import TranscriptRetriever
from app.providers.base import LLMProvider
from app.providers.factory import create_provider
from app.repositories import SessionRepository
from app.schemas import ArtifactResponse, CreateArtifactRequest, CreateMessageRequest, CreateSessionRequest, MessageResponse, SessionResponse
from app.services import ChatService

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_provider(settings: Settings = Depends(get_settings)) -> LLMProvider:
    return create_provider(settings)


async def get_database(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[AsyncSession]:
    async with get_session_factory(settings.database_url)() as session:
        yield session


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_database),
) -> SessionResponse:
    session = await SessionRepository(db).create(request.user_metadata)
    return SessionResponse.model_validate(session, from_attributes=True)


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def create_message(
    session_id: uuid.UUID,
    request: CreateMessageRequest,
    db: AsyncSession = Depends(get_database),
    provider: LLMProvider = Depends(get_provider),
) -> MessageResponse:
    _, assistant_message = await ChatService(
        SessionRepository(db), provider, TranscriptRetriever(db)
    ).respond(session_id, request.content)
    return MessageResponse.model_validate(assistant_message, from_attributes=True)


@router.post("/{session_id}/artifacts", response_model=ArtifactResponse, status_code=201)
async def create_artifact(
    session_id: uuid.UUID,
    request: CreateArtifactRequest,
    db: AsyncSession = Depends(get_database),
    provider: LLMProvider = Depends(get_provider),
) -> ArtifactResponse:
    artifact = await ArtifactService(
        SessionRepository(db), provider, TranscriptRetriever(db)
    ).create(session_id, request.format)
    return ArtifactResponse.model_validate(artifact, from_attributes=True)

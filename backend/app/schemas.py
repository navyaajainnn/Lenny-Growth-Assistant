import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    user_metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    id: uuid.UUID
    user_metadata: dict[str, Any]
    created_at: datetime


class CreateMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: Literal["user", "assistant"]
    content: str
    sources: list[dict[str, Any]]
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    message: str


class CreateArtifactRequest(BaseModel):
    format: Literal["markdown", "html"] = "markdown"


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    format: Literal["markdown", "html"]
    content: str
    created_at: datetime

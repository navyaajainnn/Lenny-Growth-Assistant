import uuid

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.chat import get_database, get_provider
from app.main import app
from app.models import Base, TranscriptChunk


class FakeProvider:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "A grounded response"


@pytest.mark.anyio
async def test_session_message_preserves_context_and_persists() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    provider = FakeProvider()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with factory() as session:
        session.add(
            TranscriptChunk(
                source="activation-episode.txt",
                content="Activation improves when users reach a meaningful first value quickly.",
                position=0,
            )
        )
        await session.commit()

    async def override_database():
        async with factory() as session:
            yield session

    def override_provider() -> FakeProvider:
        return provider

    app.dependency_overrides[get_database] = override_database
    app.dependency_overrides[get_provider] = override_provider
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            session_response = await client.post(
                "/sessions", json={"user_metadata": {"source": "test"}}
            )
            assert session_response.status_code == 201
            session_id = session_response.json()["id"]

            message_response = await client.post(
                f"/sessions/{session_id}/messages",
                json={"content": "How do I improve activation?"},
            )

        assert message_response.status_code == 200
        assert message_response.json()["content"] == "A grounded response"
        assert message_response.json()["sources"][0]["source"] == "activation-episode.txt"
        assert "Transcript context" in provider.prompts[0]
        assert provider.prompts[0].endswith("Conversation:\nuser: How do I improve activation?")
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.anyio
async def test_message_for_unknown_session_returns_structured_error() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_database():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_database] = override_database
    app.dependency_overrides[get_provider] = lambda: FakeProvider()
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"/sessions/{uuid.uuid4()}/messages", json={"content": "hello"}
            )

        assert response.status_code == 404
        assert response.json()["error"] == "session_not_found"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()

import uuid

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.chat import get_database, get_provider
from app.main import app
from app.models import Base


class ArtifactProvider:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def generate(self, prompt: str, **_: object) -> str:
        self.prompts.append(prompt)
        if len(self.prompts) == 2:
            assert "ship_30_for_30" in prompt or "Ship 30 for 30" in prompt
        return "# A grounded essay\n\nA practical takeaway."


@pytest.mark.anyio
async def test_artifact_endpoint_generates_persisted_markdown() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_database():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_database] = override_database
    app.dependency_overrides[get_provider] = ArtifactProvider
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            session = await client.post("/sessions", json={})
            session_id = session.json()["id"]
            await client.post(f"/sessions/{session_id}/messages", json={"content": "Explain activation"})
            response = await client.post(
                f"/sessions/{session_id}/artifacts", json={"format": "markdown"}
            )

        assert response.status_code == 201
        assert response.json()["format"] == "markdown"
        assert response.json()["content"].startswith("#")
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.anyio
async def test_artifact_endpoint_rejects_unknown_session() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_database():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_database] = override_database
    app.dependency_overrides[get_provider] = ArtifactProvider
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/sessions/{uuid.uuid4()}/artifacts", json={"format": "html"}
            )
        assert response.status_code == 404
        assert response.json()["error"] == "session_not_found"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()

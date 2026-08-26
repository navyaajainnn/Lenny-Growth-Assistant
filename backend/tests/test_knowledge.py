from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.knowledge import (
    TranscriptRetriever,
    chunk_text,
    ingest_transcripts,
    load_transcript_files,
    transcript_chunk_count,
)
from app.models import Base, TranscriptChunk


def test_chunk_text_creates_overlapping_chunks() -> None:
    chunks = chunk_text("one two three four five", chunk_size=3, overlap=1)

    assert chunks == ["one two three", "three four five", "five"]


def test_load_transcript_files_supports_text_and_json(tmp_path: Path) -> None:
    (tmp_path / "episode.txt").write_text("Activation starts with first value.", encoding="utf-8")
    (tmp_path / "newsletter.json").write_text(
        '[{"source":"newsletter-1","text":"Retention follows value."}]',
        encoding="utf-8",
    )

    records = load_transcript_files(tmp_path)

    assert records == [
        ("episode.txt", "Activation starts with first value."),
        ("newsletter-1", "Retention follows value."),
    ]


@pytest.mark.anyio
async def test_ingestion_and_retrieval_return_relevant_source(tmp_path: Path) -> None:
    (tmp_path / "activation.md").write_text(
        "Activation improves when users reach meaningful value quickly.", encoding="utf-8"
    )
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with factory() as session:
        assert await ingest_transcripts(session, tmp_path) == 1
        assert await transcript_chunk_count(session) == 1
        matches = await TranscriptRetriever(session).retrieve("improves activation")

    assert matches[0].source == "activation.md"
    assert matches[0].score == 2
    await engine.dispose()

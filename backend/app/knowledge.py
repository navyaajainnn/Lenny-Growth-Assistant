import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TranscriptChunk

WORD_PATTERN = re.compile(r"[a-z0-9']+")


@dataclass(frozen=True)
class RetrievedChunk:
    id: uuid.UUID
    source: str
    content: str
    score: int


def tokenize(text: str) -> set[str]:
    return set(WORD_PATTERN.findall(text.lower()))


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, chunk_size - overlap)
    return [" ".join(words[start : start + chunk_size]) for start in range(0, len(words), step)]


def _load_json_records(path: Path) -> list[tuple[str, str]]:
    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else [raw]
    return [
        (str(item.get("source", path.name)), item["text"])
        for item in items
        if isinstance(item, dict) and isinstance(item.get("text"), str)
    ]


def _load_file_records(path: Path, directory: Path) -> list[tuple[str, str]]:
    if path.suffix.lower() == ".json":
        return _load_json_records(path)
    return [
        (path.relative_to(directory).as_posix(), path.read_text(encoding="utf-8"))
    ]


def load_transcript_files(directory: Path) -> list[tuple[str, str]]:
    supported_suffixes = {".txt", ".md", ".json"}
    paths = (
        path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix.lower() in supported_suffixes
    )
    return [record for path in paths for record in _load_file_records(path, directory)]


async def ingest_transcripts(db: AsyncSession, directory: Path) -> int:
    await db.execute(delete(TranscriptChunk))
    count = 0
    for source, text in load_transcript_files(directory):
        for position, content in enumerate(chunk_text(text)):
            db.add(TranscriptChunk(source=source, content=content, position=position))
            count += 1
    await db.commit()
    return count


class TranscriptRetriever:
    def __init__(self, db: AsyncSession, limit: int = 4) -> None:
        self._db = db
        self._limit = limit

    async def retrieve(self, query: str) -> list[RetrievedChunk]:
        result = await self._db.execute(select(TranscriptChunk))
        query_terms = tokenize(query)
        scored: list[RetrievedChunk] = []
        for chunk in result.scalars():
            score = len(query_terms & tokenize(chunk.content))
            if score:
                scored.append(RetrievedChunk(chunk.id, chunk.source, chunk.content, score))
        return sorted(scored, key=lambda item: (-item.score, item.source, str(item.id)))[: self._limit]

import argparse
import asyncio
from pathlib import Path

from app.config import get_settings
from app.database import get_session_factory
from app.knowledge import ingest_transcripts


async def main(directory: Path) -> None:
    async with get_session_factory(get_settings().database_url)() as db:
        count = await ingest_transcripts(db, directory)
    print(f"Indexed {count} transcript chunks from {directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index Lenny transcript files")
    parser.add_argument("directory", type=Path)
    arguments = parser.parse_args()
    asyncio.run(main(arguments.directory))

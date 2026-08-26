import asyncio
import logging

from app.init_db import initialize_database
from app.config import get_settings
from app.database import get_session_factory
from app.knowledge import ingest_transcripts, transcript_chunk_count

logger = logging.getLogger("lenny_growth_assistant")


async def start() -> None:
    for attempt in range(1, 11):
        try:
            await initialize_database()
            await index_transcripts_if_needed()
            return
        except Exception:
            if attempt == 10:
                raise
            logger.warning("database_startup_retry", extra={"attempt": attempt})
            await asyncio.sleep(min(attempt * 2, 10))


async def index_transcripts_if_needed() -> None:
    """Seed an empty transcript index so a new deployment is usable immediately."""
    settings = get_settings()
    directory = settings.transcript_directory
    if not directory.is_dir():
        logger.warning("transcript_directory_missing", extra={"directory": str(directory)})
        return

    async with get_session_factory(settings.database_url)() as db:
        existing_count = await transcript_chunk_count(db)
        if existing_count:
            logger.info("transcript_index_present", extra={"chunk_count": existing_count})
            return
        count = await ingest_transcripts(db, directory)
    logger.info(
        "transcript_index_created",
        extra={"directory": str(directory), "chunk_count": count},
    )


if __name__ == "__main__":
    asyncio.run(start())

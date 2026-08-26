import asyncio
import logging

from app.init_db import initialize_database

logger = logging.getLogger("lenny_growth_assistant")


async def start() -> None:
    for attempt in range(1, 11):
        try:
            await initialize_database()
            return
        except Exception:
            if attempt == 10:
                raise
            logger.warning("database_startup_retry", extra={"attempt": attempt})
            await asyncio.sleep(min(attempt * 2, 10))


if __name__ == "__main__":
    asyncio.run(start())

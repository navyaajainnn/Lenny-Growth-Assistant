import asyncio
import logging

from app.config import get_settings
from app.database import get_engine
from app.models import Base
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def initialize_database() -> None:
    engine = get_engine(get_settings().database_url)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            if connection.dialect.name == "postgresql":
                await connection.execute(
                    text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS sources JSON NOT NULL DEFAULT '[]'")
                )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(initialize_database())

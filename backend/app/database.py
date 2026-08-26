from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class DatabaseUnavailableError(Exception):
    """The configured database could not be reached or used."""


@lru_cache
def get_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(database_url), expire_on_commit=False)


async def get_db(database_url: str) -> AsyncIterator[AsyncSession]:
    async with get_session_factory(database_url)() as session:
        yield session

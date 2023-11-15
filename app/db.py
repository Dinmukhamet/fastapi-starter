import contextlib
from gettext import gettext as _
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .deps import get_settings

settings = get_settings()


class DatabaseSessionNotInitializedException(Exception):
    def __init__(self, message=_("DatabaseSessionManager is not initialized")):
        super().__init__(message)


class DatabaseSessionManager:
    def __init__(self):
        self._engine = create_async_engine(
            str(settings.database_url), echo=settings.database_echo
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            raise DatabaseSessionNotInitializedException()
        await self._engine.dispose()
        del self._engine
        del self._sessionmaker

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseSessionNotInitializedException()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise DatabaseSessionNotInitializedException()

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db():
    async with DatabaseSessionManager().session() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import DatabaseSessionManager
from .deps import get_settings

from app.users.views import router


def app():
    settings = get_settings()
    sessionmanager = DatabaseSessionManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    server = FastAPI(title="FastAPI server", lifespan=lifespan, debug=settings.debug)
    server.include_router(router)
    return server

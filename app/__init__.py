from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.users.views import router

from .db import DatabaseSessionManager
from .deps import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if app.state.sessionmanager._engine is not None:
        await app.state.sessionmanager.close()


settings = get_settings()
app = FastAPI(title="FastAPI app", lifespan=lifespan, debug=settings.debug)
app.state.sessionmanager = DatabaseSessionManager()
app.include_router(router)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from backend.config import DEBUG_MODE
from backend.router.api.auth import router as auth_router
from backend.router.api.meta import router as meta_router
from backend.router.api.user import router as user_router

from .router.lifespan import shut_down, start_up


class Settings(BaseSettings):
    openapi_url: str = "" if not DEBUG_MODE else "/openapi.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_up()
    yield
    shut_down()


settings = Settings()
app = FastAPI(
    title="Qamposer Backend",
    summary="MVP Backend for Qamposer",
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
    middleware=(),
)

origins = [
    "http://localhost:3000",
    "http://localhost:4321",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(meta_router)
app.include_router(user_router)
app.include_router(auth_router)

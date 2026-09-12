from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Split Karo - Smart group expense management API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# Allow the Vite dev server and the configured FRONTEND_URL.
# allow_credentials=True is required because auth uses HttpOnly session cookies.
# ---------------------------------------------------------------------------
_allowed_origins: list[str] = []
if settings.environment != "production":
    _allowed_origins.extend(
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
for origin in settings.frontend_url.split(","):
    origin = origin.strip().rstrip("/")
    if origin and origin not in _allowed_origins:
        _allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get(
    "/health",
    tags=["System"],
)
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }

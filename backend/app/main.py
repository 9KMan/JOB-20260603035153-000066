"""Application entry point.

Wires together FastAPI app, middleware, routers, and lifecycle events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.router import api_router
from app.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, RequestLoggingMiddleware
from app.core.middleware import RequestIDMiddleware
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    configure_logging(settings.log_level)
    # Warm up: open initial connection
    async with engine.begin() as conn:
        await conn.run_sync(lambda _c: None)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    version=__version__,
    description="Production REST API",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

# Middleware order matters: outermost first
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    """Service root with metadata."""
    return JSONResponse(
        {
            "service": settings.project_name,
            "version": __version__,
            "docs": f"{settings.api_v1_prefix}/docs",
        }
    )

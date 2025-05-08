import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.api_router_definition import router
from app.config import settings
from app.util.database_util import async_engine
from app.util.logger_util import define_logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("🚀 Starting the FastAPI application...")
    define_logger()

    yield

    logger.info("💤 Shutting down the FastAPI application...")
    try:
        await asyncio.wait_for(async_engine.dispose(), timeout=10)
    except asyncio.TimeoutError:
        logger.warning("Shutdown timed out!")
    logger.info("Shutdown complete!")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Parking Platform API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins_list,
        allow_credentials=True,
        allow_methods=settings.allow_methods_list,
        allow_headers=settings.allow_headers_list,
    )
    app.include_router(router)

    return app

app = create_app()

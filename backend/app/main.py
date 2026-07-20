import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.interview import router as interview_router
from app.api.v1.resume import router as resume_router
from app.db.chroma import close_chroma_connection, connect_to_chroma
from app.db.mongo import close_mongo_connection, connect_to_mongo
from app.exceptions.handlers import register_exception_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up application-wide database connections."""

    mongo_connected = False
    chroma_connected = False

    try:
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        mongo_connected = True

        logger.info("Connecting to ChromaDB...")
        connect_to_chroma()
        chroma_connected = True

        logger.info("Application startup complete.")
        yield

    finally:
        if chroma_connected:
            logger.info("Closing ChromaDB connection...")
            close_chroma_connection()

        if mongo_connected:
            logger.info("Closing MongoDB connection...")
            await close_mongo_connection()

        logger.info("Application shutdown complete.")


app = FastAPI(
    title="AI Interview Coach API",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)


@app.get("/")
async def root():
    return {
        "message": "AI Interview Coach API",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }
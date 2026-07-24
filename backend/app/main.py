import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.interview import router as interview_router
from app.api.v1.resume import router as resume_router
from app.api.v1.resume_analysis import router as resume_analysis_router
from app.api.v1.voice import router as voice_router
from app.api.v1.reports import router as reports_router
from app.api.v1.coding_interview import router as coding_interview_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.coaching import router as coaching_router

from app.db.mongo import close_mongo_connection, connect_to_mongo
from app.exceptions.handlers import register_exception_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise essential application services."""

    mongo_connected = False

    try:
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        mongo_connected = True

        logger.info("Application startup complete.")
        yield

    finally:
        if mongo_connected:
            logger.info("Closing MongoDB connection...")
            await close_mongo_connection()

        logger.info("Application shutdown complete.")


app = FastAPI(
    title="AI Interview Coach API",
    version="1.0.0",
    lifespan=lifespan,
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(embeddings_router)
app.include_router(resume_analysis_router)
app.include_router(voice_router)
app.include_router(reports_router)
app.include_router(coding_interview_router)
app.include_router(sessions_router)
app.include_router(coaching_router)


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
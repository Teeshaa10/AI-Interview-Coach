from fastapi import APIRouter

from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.interview import router as interview_router
from app.api.v1.resume import router as resume_router
from app.api.v1.voice import router as voice_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(resume_router)
api_v1_router.include_router(embeddings_router)
api_v1_router.include_router(interview_router)
api_v1_router.include_router(voice_router)

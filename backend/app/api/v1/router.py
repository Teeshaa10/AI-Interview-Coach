from fastapi import APIRouter

from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.resume import router as resume_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(resume_router)
api_v1_router.include_router(embeddings_router)

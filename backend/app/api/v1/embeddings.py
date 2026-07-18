from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.v1.resume import _extract_user_id
from app.dependencies import get_current_user
from app.embedding_dependencies import get_semantic_search_service
from app.schemas.embedding import EmbeddingSearchRequest, EmbeddingSearchResponse
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.post("/search", response_model=EmbeddingSearchResponse)
async def search_resume_chunks(
    payload: EmbeddingSearchRequest,
    current_user: Annotated[Any, Depends(get_current_user)],
    service: Annotated[SemanticSearchService, Depends(get_semantic_search_service)],
) -> EmbeddingSearchResponse:
    results = await service.search(
        query=payload.query,
        user_id=_extract_user_id(current_user),
        top_k=payload.top_k,
        resume_id=payload.resume_id,
        min_similarity=payload.min_similarity,
    )
    return EmbeddingSearchResponse(query=payload.query, count=len(results), results=results)

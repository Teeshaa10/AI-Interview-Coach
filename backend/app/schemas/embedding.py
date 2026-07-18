from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmbeddingSearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    resume_id: str | None = None
    min_similarity: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def reject_blank_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Query must not be blank")
        return value.strip()


class EmbeddingSearchResult(BaseModel):
    chunk_id: str
    chunk_text: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    resume_id: str
    filename: str
    chunk_index: int
    start_char: int
    end_char: int


class EmbeddingSearchResponse(BaseModel):
    query: str
    count: int
    results: list[EmbeddingSearchResult]

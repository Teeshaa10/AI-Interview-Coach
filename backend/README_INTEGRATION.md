# AI Interview Coach Backend

## Implemented modules

### Module 1 — Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Module 2 — Resume Upload & Parsing

- `POST /api/v1/resume/upload`
- `GET /api/v1/resume/me`
- `DELETE /api/v1/resume/{resume_id}`

PDF and DOCX uploads are validated, stored under `uploads/`, parsed, and persisted in MongoDB.

### Module 3 — Embeddings & Semantic Search

- Resume text is automatically split into configurable overlapping chunks after upload.
- Chunks are embedded in one batch with `sentence-transformers/all-MiniLM-L6-v2`.
- Vectors and metadata are persisted in ChromaDB using deterministic IDs.
- Failed vector indexing rolls back the MongoDB resume document and uploaded file.
- Deleting a resume also deletes its ChromaDB vectors.
- `POST /api/v1/embeddings/search` performs authenticated, user-scoped semantic search.
- Search can optionally be restricted to one owned resume with `resume_id`.

Example request:

```json
{
  "query": "backend engineering experience with FastAPI and MongoDB",
  "top_k": 5,
  "min_similarity": 0.2
}
```

Optional single-resume search:

```json
{
  "query": "machine learning projects",
  "top_k": 10,
  "resume_id": "MongoDB ObjectId string",
  "min_similarity": 0.0
}
```

## Configuration

Copy `.env.example` to `.env` and set MongoDB and JWT values. Module 3 uses:

```text
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_NAME=resume_chunks
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_CHUNK_SIZE=500
EMBEDDING_CHUNK_OVERLAP=100
```

The embedding model downloads on first use and remains cached in the process.

## Install and run

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

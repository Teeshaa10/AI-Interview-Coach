# Resume Module Integration

## Included endpoints

- `POST /api/v1/resume/upload`
- `GET /api/v1/resume/me`
- `DELETE /api/v1/resume/{resume_id}`

## Existing project contracts

This module expects:

```python
from app.db.mongodb import get_database
```

`get_database` should return or asynchronously resolve to an
`AsyncIOMotorDatabase`.

It also expects:

```python
from app.dependencies import get_current_user
```

`get_current_user` must return a dictionary, Pydantic model, or object
containing `id` or `_id`.

## Install dependencies

```bash
pip install -r requirements-resume.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

## Important integration note

If your existing `app/main.py` already defines the FastAPI app, do not replace
unrelated application setup. Copy these parts into it:

```python
from app.api.v1.router import api_v1_router
from app.exceptions.resume import ResumeError
```

Register the exception handler and include:

```python
app.include_router(api_v1_router)
```

If your existing API v1 router already exists, include only:

```python
from app.api.v1.resume import router as resume_router
api_v1_router.include_router(resume_router)
```

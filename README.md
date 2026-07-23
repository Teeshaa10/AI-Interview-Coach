# AI Interview Coach

An AI-powered interview practice platform: upload a resume, get personalized
interview questions, answer them, and receive AI-graded feedback.

- **Backend:** FastAPI, Python 3.11+, MongoDB (Motor), ChromaDB, Google Gemini, JWT auth
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod

See `CHECKPOINT.md` for the exact current implementation status, what's
still pending, and known backend limitations discovered while building
the frontend.

## Required versions

- Node.js 20 LTS or newer (Vite 7 requires Node ^20.19 or ^22.12+)
- Python 3.11+
- A MongoDB Atlas connection string and Google Gemini API key (see
  `backend/.env.example`)

## 1. Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # Windows; use `cp` on macOS/Linux
# fill in MongoDB / Gemini credentials in backend/.env
python -m uvicorn app.main:app --reload
```

- Backend: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## 2. Run the frontend

```bash
cd frontend
copy .env.example .env      # Windows; use `cp` on macOS/Linux
npm install
npm run dev
```

- Frontend: `http://localhost:5173`

## API base URL

The frontend reads its backend URL from `VITE_API_BASE_URL` in
`frontend/.env` (see `frontend/.env.example`). **Do not add `/api/v1`** -
inspecting `backend/app/main.py` shows every router (`auth`, `resume`,
`interview`, `resume-analysis`, `voice`, `reports`, `coding-interviews`) is
mounted directly on the app with no version prefix. A separate
`/api/v1`-prefixed router exists in `app/api/v1/router.py` but is not
wired into `main.py`, so it is not part of the live API.

## CORS

`backend/app/main.py` already allows `http://localhost:5173` and
`http://127.0.0.1:5173` with credentials - no backend change was needed
for the frontend to talk to it locally. If you deploy the frontend to a
different origin, add that origin to the `allow_origins` list in
`app/main.py`; do not switch it to `allow_origins=["*"]` in production.

## Authentication flow

1. `POST /auth/register` creates the account (no token returned).
2. `POST /auth/login` returns `{ access_token, token_type, user }`. The
   frontend stores the token in `localStorage` and attaches it as
   `Authorization: Bearer <token>` to every subsequent request.
3. `GET /auth/me` is used on app load to verify the stored token is still
   valid and to refresh the cached user.
4. Any `401` response anywhere in the app clears stored auth state and
   redirects to `/login`.

## Modules completed (frontend)

- **Module 1 - Foundation & Authentication:** complete.
- **Module 2 - Dashboard & Resume Management:** mostly complete, adapted
  to a real backend constraint - see `CHECKPOINT.md` ("no resume list
  endpoint" and "embeddings router not mounted").
- **Module 3 - AI HR Interview:** core flow (setup → session → complete)
  implemented against the verified `/interview/*` endpoints.

## Common CORS troubleshooting

- **"Network Error" / CORS error in the browser console:** confirm the
  backend is running on `http://127.0.0.1:8000` and that
  `frontend/.env`'s `VITE_API_BASE_URL` matches it exactly (including
  `http://` vs `https://` and the port).
- **CORS error only in production:** add your deployed frontend origin to
  `allow_origins` in `backend/app/main.py`.
- **401 on every request right after login:** check the browser's
  Application/Storage tab for `aic_access_token` in `localStorage` - if
  it's missing, login didn't complete successfully.

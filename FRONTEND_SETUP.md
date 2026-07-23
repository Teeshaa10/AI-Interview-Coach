# Frontend setup

## 1. Start the backend

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

## 2. Start the frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Frontend: `http://localhost:5173`

The frontend contains authentication, dashboard, resume upload and ATS analysis, personalised AI interviews, coding interviews with Monaco Editor, and performance reports.

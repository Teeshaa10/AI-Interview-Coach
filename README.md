# 🚀 AI Interview Coach

An AI-powered interview preparation platform that helps candidates prepare for technical interviews using Resume Analysis, AI-generated Interview Questions, Coding Interviews, Voice Interviews, and Detailed Performance Reports.

---

# ✨ Features

## 🔐 Authentication
- User Registration
- JWT Login Authentication
- Protected APIs
- Current User Endpoint

---

## 📄 Resume Management
- Resume Upload
- Resume Parsing
- Resume Embedding Generation
- ChromaDB Storage
- Semantic Resume Search

---

## 🤖 AI Interview Generator
- AI-generated HR Interview Questions
- Resume-based Personalized Questions
- Multiple Difficulty Levels
- Experience-based Question Generation

---

## 🧠 AI Interview Evaluation
- AI Evaluation using Google Gemini
- Detailed Feedback
- Strengths & Weaknesses
- Improvement Suggestions
- Overall Score

---

## 🎤 Voice Interview
- Audio Upload
- Speech-to-Text
- AI Evaluation
- Voice Interview Sessions

---

## 💻 Coding Interview
- AI-generated Coding Questions
- Multiple Difficulty Levels
- Topic-based Questions
- C++ / Java / Python Support
- Local Judge0 Code Execution
- AI Code Review
- Complexity Analysis

---

## 📊 Interview Reports
- Interview History
- Coding Performance
- HR Interview Performance
- Overall Analytics
- Feedback Reports

---

# 🏗️ System Architecture

```
                User
                  │
                  ▼
           FastAPI Backend
                  │
        ┌─────────┼──────────┐
        │         │          │
        ▼         ▼          ▼
   MongoDB     ChromaDB   Judge0
      │           │          │
      └──────┬────┘          │
             ▼               │
         Google Gemini ◄─────┘
```

---

# 🛠 Tech Stack

### Backend
- FastAPI
- Python 3.11
- Pydantic v2
- Dependency Injection

### Database
- MongoDB Atlas
- ChromaDB

### AI
- Google Gemini
- Sentence Transformers
- all-MiniLM-L6-v2

### Authentication
- JWT Authentication

### Code Execution
- Judge0 (Self Hosted)

### Others
- Docker
- WSL2
- Uvicorn

---

# 📂 Project Structure

```
backend
│
├── app
│   ├── api
│   ├── core
│   ├── db
│   ├── exceptions
│   ├── models
│   ├── repositories
│   ├── schemas
│   ├── services
│   ├── prompts
│   └── main.py
│
├── uploads
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Teeshaa10/AI-Interview-Coach.git
```

```bash
cd AI-Interview-Coach/backend
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file using `.env.example`.

Example:

```env
MONGODB_URL=

JWT_SECRET_KEY=

GEMINI_API_KEY=

CODE_EXECUTION_PROVIDER=judge0

JUDGE0_BASE_URL=http://localhost:2358
```

---

## Run Backend

```bash
python -m uvicorn app.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# 🐳 Judge0 Setup

Start Docker Desktop.

Navigate to Judge0 folder.

```bash
docker compose up -d
```

Verify

```bash
docker compose ps
```

Judge0 API

```
http://localhost:2358
```

---

# 📑 Main API Endpoints

## Authentication

```
POST /auth/register
POST /auth/login
GET  /auth/me
```

---

## Resume

```
POST /resume/upload
GET  /resume/search
```

---

## Interview

```
POST /interview/start
POST /interview/{resume_id}/answer
```

---

## Voice

```
POST /voice/start
POST /voice/answer
```

---

## Coding

```
POST /coding/start
POST /coding/submit
POST /coding/evaluate
```

---

## Reports

```
GET /reports
GET /reports/{id}
```

---

# 📈 Future Improvements

- Frontend Dashboard
- Video Interviews
- Real-time AI Interviewer
- Company-specific Interview Modes
- Resume ATS Score
- Mock Interview Analytics
- Leaderboard
- Deployment on Cloud

---

# 🔒 Security

- JWT Authentication
- Protected Routes
- Secure Password Hashing
- Environment Variables
- Self-hosted Judge0

---

# 👨‍💻 Author

**Divyansh Gupta**

B.Tech CSAI • IIIT Delhi

---

# ⭐ If you like this project, consider giving it a star!

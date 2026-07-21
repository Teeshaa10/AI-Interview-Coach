# AI Interview Coach

AI Interview Coach is a FastAPI-based backend that helps users upload resumes, generate interview questions, evaluate answers, conduct voice interviews, run coding interviews, and generate reports.

## Tech Stack

- FastAPI
- MongoDB Atlas
- ChromaDB
- Sentence Transformers
- Google Gemini
- JWT Authentication
- Judge0
- Python 3.11+
- Pydantic v2

## Features

- User registration and login
- JWT authentication
- Resume upload and parsing
- Resume embeddings and semantic search
- AI interview question generation
- Interview answer evaluation
- Voice interview support
- Coding interview generation
- Code execution using Judge0
- Interview report generation

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── exceptions/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── uploads/
├── requirements.txt
├── pyproject.toml
└── .env.example

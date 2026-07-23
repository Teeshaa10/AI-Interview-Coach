# Modules 7 and 8 Setup

## Module 7: Advanced Interview Reports

Finish an interview before generating a report.

Endpoints:
- `POST /reports/interview/{interview_id}/generate`
- `GET /reports/interview/{interview_id}`
- `GET /reports/history`
- `GET /reports/{report_id}`
- `DELETE /reports/{report_id}`
- `GET /reports/analytics/summary`
- `GET /reports/analytics/trends?grouping=weekly`

The report uses saved interview scores deterministically. It does not invent scores.

## Module 8: Coding Interview

Code is never executed locally. Configure one remote provider.

### Piston

```env
CODE_EXECUTION_PROVIDER=piston
PISTON_BASE_URL=https://emkc.org
```

### Judge0

```env
CODE_EXECUTION_PROVIDER=judge0
JUDGE0_BASE_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your-key
JUDGE0_API_HOST=judge0-ce.p.rapidapi.com
```

Endpoints:
- `POST /coding-interviews/start`
- `GET /coding-interviews/history`
- `GET /coding-interviews/languages`
- `GET /coding-interviews/{session_id}`
- `POST /coding-interviews/{session_id}/submit`
- `POST /coding-interviews/{session_id}/complete`
- `GET /coding-interviews/{session_id}/submissions`

Install and run:

```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

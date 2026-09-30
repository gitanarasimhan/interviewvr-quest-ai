# InterviewVR AI backend

This folder contains the MVP backend API for the InterviewVR AI product.

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

## Quick start

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/health
- http://localhost:8000/docs

# InterviewVR AI

InterviewVR AI is a small MVP for an AI-powered virtual interview coach. The solution is organized in two layers:

- Unity client for the interview flow and editor simulation
- Python API for transcription and interview evaluation

The design deliberately avoids Quest-only dependencies so the same business logic can run in the Unity Editor using simulated keyboard/mouse input.

## Product scope

Supported roles:
- Software Engineer
- Product Manager

Supported interview types:
- Behavioral
- Technical

Core flow:
1. Select job role and interview type
2. Show interview question
3. User answers verbally
4. Convert speech to text
5. Send transcript to AI backend
6. Return structured feedback
7. Show score, strengths, improvements, missing information, and a follow-up question
8. Repeat through ~5 questions
9. Display a final interview report

## Repository structure

- `backend/` — Python API and evaluation logic
- `unity/InterviewVR/` — Unity project skeleton and simulation scripts
- `docs/` — architecture and phase planning
- `.gitignore` — project-level ignore rules

## Local development

### Python API

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Unity client

Open the Unity project under `unity/InterviewVR` in the Unity Editor. The scripts include:

- `InterviewController.cs` — manages the interview flow
- `KeyboardInputController.cs` — simulates voice input in the editor
- `InterviewData.cs` — schema for the interview question and feedback data

## API endpoints

- `GET /health`
- `GET /api/interview/questions?role=software_engineer&interview_type=behavioral`
- `POST /api/interview/evaluate`

## Notes

- Quest and headset support are intentionally deferred to later phases.
- The first MVP prioritizes reliability and Windows development workflow.
- AI feedback is implemented behind a service boundary so it can be swapped for OpenAI or another provider later.

## Roadmap

See `docs/ARCHITECTURE.md` for the phased build plan.

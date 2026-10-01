# InterviewVR AI

InterviewVR AI is an AI-powered virtual interview coach that conducts a dynamic, GPT-driven conversation rather than a fixed question bank. The solution is organized in two layers:

- Unity client for the conversational interview flow and editor simulation
- Python API for transcription, dynamic question generation, and answer evaluation

The design deliberately avoids Quest-only dependencies so the same business logic can run in the Unity Editor using simulated keyboard/mouse input.

## Product scope

Supported roles:
- Software Engineer
- Product Manager

Supported interview types:
- Behavioral
- Technical
- Case Study

Core flow:
1. Select job role and interview type, start a session (`/api/interview/start`)
2. AI generates the opening question
3. User answers verbally
4. Convert speech to text
5. Send the answer to the backend (`/api/interview/chat`)
6. AI returns structured feedback (score, strengths, improvements, missing information) **and** a dynamically generated follow-up question based on the answer
7. Repeat steps 3–6 for the length of the interview
8. Finalize the session (`/api/interview/end`) and display the aggregated final report

## Repository structure

- `backend/` — Python API: dynamic conversation service, HMAC security, Lambda handler
- `unity/InterviewVR/` — Unity project with a chat-based conversation UI and simulation scripts
- `docs/` — architecture, security, and deployment guides
- `.gitignore` — project-level ignore rules

## Local development

### Python API

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then add your OPENAI_API_KEY and QUEST_APP_SECRET
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Unity client

Open the Unity project under `unity/InterviewVR` in the Unity Editor. The scripts include:

- `InterviewController.cs` — drives the start/chat/end conversation flow and (optionally) HMAC-signed requests
- `KeyboardInputController.cs` — simulates voice input in the editor
- `InterviewData.cs` — schema for the conversation request/response data
- `UI/ChatUIController.cs` — chat bubble conversation view
- `UI/FeedbackDisplayController.cs` — real-time score/feedback display
- `UI/InterviewProgressController.cs` — interview completion progress bar
- `Network/SecureAPIClient.cs` — HMAC-signed request helper

## API endpoints

- `GET /health`
- `POST /api/interview/start`
- `POST /api/interview/chat`
- `POST /api/interview/end`
- `POST /api/interview/evaluate` (legacy, standalone evaluation)
- `POST /api/interview/report` (legacy, standalone report)
- `POST /api/interview/transcribe`

See `backend/README.md` for full request/response examples and `docs/API_KEYS_AND_SECURITY.md` for HMAC configuration.

## Notes

- Quest and headset support are intentionally deferred to later phases.
- The backend is ready to deploy to AWS Lambda via `backend/lambda_handler.py` (see `docs/QUEST_STORE_DEPLOYMENT.md`).
- AI feedback is implemented behind a service boundary so it can be swapped for OpenAI or another provider later.

## Roadmap

See `docs/ARCHITECTURE.md` for the phased build plan.

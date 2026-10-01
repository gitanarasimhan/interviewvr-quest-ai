# Backend — InterviewVR AI API

## API Overview

The backend drives a dynamic, AI-powered interview conversation rather than
a static Q&A bank. The core endpoints are:

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health/startup check (safe for Lambda warmers & load balancers) |
| `/api/interview/start` | POST | Start a new interview session for a role/interview type, returns `session_id` + opening question |
| `/api/interview/chat` | POST | Submit a candidate's answer, get AI feedback + the next dynamically generated question |
| `/api/interview/end` | POST | Finalize a session and get the aggregated final report |
| `/api/interview/evaluate` | POST | Legacy: evaluate a single standalone answer outside of a session |
| `/api/interview/report` | POST | Legacy: generate a report from a list of scores outside of a session |
| `/api/interview/transcribe` | POST | Transcribe audio (or pass through text) via Whisper |

### Example flow

```bash
# 1. Start an interview
curl -X POST http://localhost:8000/api/interview/start \
  -H "Content-Type: application/json" \
  -d '{"role": "software_engineer", "interview_type": "behavioral"}'
# => {"session_id": "...", "question": "Tell me about...", "progress": 0.0, ...}

# 2. Answer, get feedback + next question
curl -X POST http://localhost:8000/api/interview/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "answer": "I led a production incident..."}'
# => {"score": 85, "strengths": [...], "next_question": "...", "is_complete": false, ...}

# 3. Repeat step 2 until "is_complete": true, then finalize
curl -X POST http://localhost:8000/api/interview/end \
  -H "Content-Type: application/json" \
  -d '{"session_id": "..."}'
# => {"average_score": 84.5, "summary": "...", "recommendations": [...]}
```

Conversation state (questions, answers, feedback, scores) is tracked
in-memory per session by `app/conversation_service.py`. Swap the
`ConversationService._sessions` dict for a persistent store (DynamoDB,
Redis, etc.) for multi-instance production deployments.

## Quest Store Strategy

For deploying InterviewVR AI to the public Meta Quest Store and beyond, see:

**`docs/QUEST_STORE_DEPLOYMENT.md`** — Complete guide covering:
- Why you can't bundle API keys in the APK
- Backend-as-a-Service (BaaS) architecture
- Three implementation tiers (MVP → Secured → Monetized)
- Deployment platforms (Heroku, AWS Lambda, DigitalOcean)
- Cost estimation
- Security checklist

## Quick Reference: Backend Deployment

### Heroku (Easiest for MVP)
```bash
heroku create interviewvr-api
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set APP_ENV=production
git push heroku main
```

### AWS Lambda

The backend includes `lambda_handler.py`, a ready-made entry point using
[Mangum](https://github.com/jordaneremieff/mangum) to adapt the FastAPI app
for AWS Lambda + API Gateway. Set the Lambda handler to
`lambda_handler.handler`.

```bash
sam build
sam deploy --guided
```

See `docs/QUEST_STORE_DEPLOYMENT.md` for a full SAM template example.

### DigitalOcean App Platform
1. Push code to GitHub
2. Connect repo in dashboard
3. Set environment variables
4. Deploy

## API Security (HMAC Request Signing)

For production Quest Store release, set `REQUIRE_SIGNATURE=true` and share
`QUEST_APP_SECRET` between the backend and the Unity app. Every signed
request includes an `X-Signature` (HMAC-SHA256 over
`"{timestamp}.{body}"`) and an `X-Timestamp` header; requests older than
`SIGNATURE_MAX_AGE_SECONDS` (default 300s / 5 minutes) are rejected to
prevent replay attacks.

```csharp
// Unity/Quest side
var client = new SecureAPIClient("https://api.yourserver.com", appSecret);
client.SendSignedRequest("/api/interview/chat", "POST", json,
    onSuccess: (response) => Debug.Log(response),
    onError: (error) => Debug.LogError(error)
);
```

```python
# Backend side (already wired into app/main.py via `dependencies=[...]`)
from app.auth import verify_quest_signature
from fastapi import Depends

@app.post("/api/interview/chat", dependencies=[Depends(verify_quest_signature)])
def chat(payload: ChatRequest) -> ChatResponse:
    # Only reached if signature + timestamp are valid (when REQUIRE_SIGNATURE=true)
    ...
```

## Local Testing

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Test health endpoint:
```bash
curl http://localhost:8000/health
```

Run the test suite:
```bash
pytest tests/
```

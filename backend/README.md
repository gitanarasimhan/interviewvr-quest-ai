# Deployment Guides

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
```bash
sam build
sam deploy --guided
```

### DigitalOcean App Platform
1. Push code to GitHub
2. Connect repo in dashboard
3. Set environment variables
4. Deploy

## API Security

For production Quest Store release, use HMAC signature verification:

```csharp
// Unity/Quest side
var client = new SecureAPIClient("https://api.yourserver.com", appSecret);
client.SendSignedRequest("/api/interview/evaluate", "POST", json, 
    onSuccess: (response) => Debug.Log(response),
    onError: (error) => Debug.LogError(error)
);
```

```python
# Backend side
from app.auth import verify_quest_signature
from fastapi import Depends

@app.post("/api/interview/evaluate")
def evaluate_transcript(
    payload: EvaluateRequest,
    verified: bool = Depends(verify_quest_signature)
) -> EvaluateResponse:
    # Only reached if signature is valid
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

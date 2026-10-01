# InterviewVR AI — Quest Store Deployment & API Key Strategy

## Challenge: Public App + Private API Keys

When you publish to the Meta Quest Store, your app is public. Anyone can download it. You cannot bundle private API keys (OpenAI, Whisper, etc.) in the app binary because:

1. **Security risk** — users can reverse-engineer the APK and extract the key
2. **Cost** — if the key is public, attackers can use it and you pay the bill
3. **Meta Quest Store policy** — keys in binaries are a red flag for review

---

## Solution: Backend-as-a-Service Architecture

The recommended production pattern is **Backend-as-a-Service (BaaS)**:

```
┌──────────────────────┐
│  Meta Quest Store    │
│  Public InterviewVR  │
│      App (APK)       │
└──────────┬───────────┘
           │ HTTPS
           ↓
┌──────────────────────────────────────┐
│  Your Backend (Private Cloud)        │
│  • Python API (secured)              │
│  • OpenAI API key (in env vars)      │
│  • Billing/usage tracking            │
│  • Rate limiting & auth              │
└──────────────────────────────────────┘
           │
           ↓
┌──────────────────────┐
│  OpenAI API          │
│  (Whisper + GPT)     │
└──────────────────────┘
```

**The Quest app:**
- Contains NO API keys
- Sends encrypted HTTPS requests to your backend
- Receives evaluated feedback
- Handles all UI/UX locally

**Your backend:**
- Holds the OpenAI key (in AWS Secrets Manager, environment variable, etc.)
- Authenticates Quest app users
- Manages API quotas and billing
- Logs usage for analytics

---

## Implementation: Three Tiers

### Tier 1: MVP (Today)
**Setup:** Public backend, no user auth needed yet

```python
# backend/app/main.py
@app.post("/api/interview/evaluate")
def evaluate_transcript(payload: EvaluateRequest) -> EvaluateResponse:
    # OpenAI key is in environment variable
    feedback = InterviewEvaluationService.evaluate(payload)
    return feedback
```

**Deploy to:**
- Heroku (free/paid tier)
- AWS Lambda + API Gateway
- DigitalOcean App Platform
- Railway.app

**Pros:**
- Simple setup
- Works immediately
- No auth complexity

**Cons:**
- Anyone can spam your backend and cost you money
- No usage tracking per user

---

### Tier 2: Secured Backend (Recommended for Public Release)
**Setup:** User authentication + API key validation

Add authentication so only your Quest app can call your backend:

```python
# backend/app/auth.py
from fastapi import Depends, HTTPException
import hmac
import hashlib

def verify_quest_request(request_signature: str, request_body: str) -> dict:
    """
    Verify the request came from your Quest app.
    Uses HMAC signing to prevent spoofing.
    """
    app_secret = os.getenv("QUEST_APP_SECRET")
    expected_signature = hmac.new(
        app_secret.encode(),
        request_body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(request_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return {"valid": True}

# backend/app/main.py
@app.post("/api/interview/evaluate")
def evaluate_transcript(
    payload: EvaluateRequest,
    signature: str = Header(None)
) -> EvaluateResponse:
    verify_quest_request(signature, json.dumps(payload.dict()))
    feedback = InterviewEvaluationService.evaluate(payload)
    return feedback
```

**Unity/Quest side:**

```csharp
// unity/InterviewVR/Assets/Scripts/InterviewVR/Network/SecureAPI.cs
using System.Security.Cryptography;
using System.Text;

public class SecureAPIClient
{
    private string appSecret = "your-app-secret-here";  // Store securely
    
    private string GenerateHMAC(string body)
    {
        using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(appSecret)))
        {
            var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(body));
            return System.Convert.ToHexString(hash);
        }
    }
    
    public IEnumerator EvaluateAnswer(EvaluateRequest request)
    {
        string json = JsonUtility.ToJson(request);
        string signature = GenerateHMAC(json);
        
        using (UnityWebRequest webRequest = new UnityWebRequest(apiUrl, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");
            webRequest.SetRequestHeader("X-Signature", signature);
            
            yield return webRequest.SendWebRequest();
            // Handle response...
        }
    }
}
```

**Deploy to:**
- AWS Lambda + API Gateway (with Cognito for optional user auth)
- Heroku (private dyno)
- DigitalOcean App Platform
- Google Cloud Run

**Pros:**
- Only your Quest app can call the backend
- Prevents unauthorized usage
- Cost-protected

**Cons:**
- Need to embed app secret (manage carefully)
- No per-user tracking yet

---

### Tier 3: Monetized Backend (For Scale)
**Setup:** User accounts + credits/subscription system

```python
# backend/app/models.py
from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    api_key = Column(String, unique=True)
    credits = Column(Float, default=10.0)  # Free trial: 10 interview evaluations
    email = Column(String)

# backend/app/auth.py
def verify_api_key(api_key: str) -> User:
    """
    User provides their API key in the Quest app.
    We verify it against our database.
    """
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if user.credits <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    return user

# backend/app/main.py
@app.post("/api/interview/evaluate")
def evaluate_transcript(
    payload: EvaluateRequest,
    api_key: str = Header(None)
) -> EvaluateResponse:
    user = verify_api_key(api_key)
    feedback = InterviewEvaluationService.evaluate(payload)
    
    # Deduct 1 credit from user
    user.credits -= 0.1  # or whatever cost per evaluation
    db.commit()
    
    return feedback
```

**Flow:**
1. User downloads app from Quest Store
2. On first launch, generate a unique API key for their device
3. User logs in or skips login (free trial)
4. App stores API key locally (encrypted)
5. Every API call includes the key
6. Backend tracks credits and billing

**Deploy to:**
- AWS (Lambda + RDS for database)
- Heroku (with PostgreSQL add-on)
- DigitalOcean (App Platform + Managed Database)
- Firebase + Cloud Functions

**Pros:**
- Track individual users
- Implement free tier + paid upgrade
- Control costs
- Collect analytics

**Cons:**
- Requires database
- More operational complexity
- Need billing integration (Stripe, Paddle)

---

## Recommended Path for You

### Phase 1: MVP (Now)
- Deploy backend to **Heroku free tier** or **Railway.app**
- OpenAI key in environment variable
- No auth (simple)
- Add rate limiting to prevent abuse

### Phase 2: Public Release (Before Quest Store)
- Add HMAC signature validation
- Deploy to **AWS Lambda + API Gateway** (scales automatically)
- Monitor costs (set CloudWatch alarms)
- Add usage logging

### Phase 3: Monetization (After Launch)
- Add user accounts and API keys
- Implement free tier (10 interviews)
- Integrate Stripe/Paddle for payments
- Track revenue

---

## Quick Deployment Checklist

### For Heroku (Easiest to start)

```bash
# 1. Install Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create interviewvr-api

# 4. Add environment variables
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set APP_ENV=production

# 5. Deploy
git push heroku main

# 6. Check logs
heroku logs --tail
```

### For AWS Lambda (More control, auto-scaling)

```bash
# 1. Install SAM CLI
# 2. Build
sam build

# 3. Deploy (first time interactive)
sam deploy --guided

# 4. AWS Secrets Manager stores OPENAI_API_KEY
# 5. Lambda function fetches it at runtime
```

### For DigitalOcean App Platform

1. Push code to GitHub
2. Connect repo in DigitalOcean dashboard
3. Set environment variables in the UI
4. Deploy (auto CI/CD)

---

## Cost Estimation

| Service | MVP Cost | Tier 2 Cost | Tier 3 Cost |
|---------|----------|------------|-------------|
| Backend hosting | $7/mo (Heroku) | $0-10/mo (Lambda) | $50+/mo (AWS) |
| Database | Free | Free | $15/mo (RDS) |
| OpenAI API | $0.01-1/call | $0.01-1/call | $0.01-1/call |
| **Total** | **~$7-20/mo** | **~$20-50/mo** | **~$100+/mo** |

*Note: Actual OpenAI cost depends on evaluation complexity and user volume.*

---

## Security Best Practices for Quest Store

✅ **DO:**
- Store OpenAI key only on backend
- Use HTTPS for all API calls
- Implement rate limiting
- Log API usage for audit trails
- Rotate API keys quarterly
- Validate all requests (signature or API key)
- Use separate keys for dev/staging/production

❌ **DON'T:**
- Embed API keys in APK
- Send secrets over HTTP
- Log API keys in error messages
- Use the same key for multiple apps
- Skip authentication for public APIs

---

## Next Steps

1. **Choose your deployment platform** (Heroku/AWS/DigitalOcean)
2. **I'll add** HMAC auth to the backend + Quest app
3. **I'll create** deployment scripts and documentation
4. **I'll set up** environment-based config for dev/staging/prod

Which platform appeals to you?

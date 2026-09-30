# InterviewVR AI — API Keys & Secure Configuration

## Required API Keys

You will need the following API keys to run the full MVP:

### 1. OpenAI API Key
**Purpose:** Answer evaluation (GPT-4o-mini) + speech-to-text (Whisper)
**Get it:** https://platform.openai.com/account/api-keys
**Cost:** Pay-as-you-go (typical MVP testing: $5-20/month)

### 2. (Optional) Azure Speech Services API Key
**Purpose:** Alternative to Whisper for speech-to-text
**Get it:** https://portal.azure.com → Cognitive Services → Speech
**Cost:** Free tier available (5 hours/month)

---

## Secure Storage Methods

### Option 1: Environment Variables (Recommended for local dev)

**Backend (.env file):**
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
WHISPER_MODEL=whisper-1
APP_ENV=development
```

**Never commit .env to GitHub.** It's already in `.gitignore`.

### Option 2: AWS Secrets Manager (Recommended for production)

Store secrets in AWS and retrieve them at runtime:
```python
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='interviewvr-api-keys')
api_key = json.loads(secret['SecretString'])['openai_api_key']
```

### Option 3: GitHub Secrets (For CI/CD only)

If you use GitHub Actions for testing:
1. Go to repo Settings → Secrets and variables → Actions
2. Add `OPENAI_API_KEY`
3. Reference in workflows as `${{ secrets.OPENAI_API_KEY }}`

**Do NOT print or log secrets in CI/CD logs.**

### Option 4: HashiCorp Vault (For teams)

For shared team development:
```python
import hvac

client = hvac.Client(url='https://vault.company.com')
secret = client.secrets.kv.read_secret_version(path='interviewvr')
api_key = secret['data']['data']['openai_api_key']
```

### Option 5: 1Password / LastPass / Bitwarden (Team secret sharing)

1. Store API keys in your team password manager
2. Share via secure link (time-limited access)
3. Developers copy to local `.env` manually

---

## Setup Instructions

### Local Development

1. **Copy the example file:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Add your OpenAI API key:**
   ```bash
   # Edit backend/.env
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-4o-mini
   WHISPER_MODEL=whisper-1
   APP_ENV=development
   ```

3. **Verify .env is in .gitignore:**
   ```bash
   cat .gitignore | grep .env
   # Should show: .env
   ```

4. **Load in Python:**
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   api_key = os.getenv('OPENAI_API_KEY')
   ```

### Production Deployment

**For Heroku:**
```bash
heroku config:set OPENAI_API_KEY=sk-...
```

**For Docker:**
```bash
docker run -e OPENAI_API_KEY=sk-... interviewvr-api
```

**For AWS Lambda:**
```bash
aws secretsmanager create-secret --name interviewvr-keys \
  --secret-string '{"openai_api_key": "sk-..."}'
```

---

## Best Practices

✅ **Do:**
- Use `.env` files for local development
- Rotate API keys quarterly
- Use environment-specific keys (dev, staging, prod)
- Log key usage in production for audit trails
- Use short-lived API keys when possible

❌ **Don't:**
- Commit `.env` to Git
- Log API keys in error messages
- Share keys via email or Slack
- Use the same key for dev and production
- Hardcode keys in source code

---

## Revoking a Compromised Key

1. **OpenAI:** https://platform.openai.com/account/api-keys → Delete the key
2. **Immediately update** your production .env or secrets manager
3. **Rotate** to a new key
4. **Check usage logs** for suspicious activity

---

## Next Steps

1. Get your OpenAI API key
2. Create `backend/.env` from the example
3. Run the backend with the key loaded
4. Test the evaluation and transcription endpoints

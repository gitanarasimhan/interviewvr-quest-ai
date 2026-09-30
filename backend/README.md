# Complete API Keys & Security Guide

For the full setup details including:
- Where to get API keys
- How to securely store them
- Best practices
- Production deployment

See: `docs/API_KEYS_AND_SECURITY.md`

## Quick Start

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Copy it (you'll only see it once)

### 2. Create backend/.env

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
WHISPER_MODEL=whisper-1
APP_ENV=development
```

### 3. Install dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test it

```bash
curl http://localhost:8000/health
```

## What's New

✅ **OpenAI Integration:**
- GPT-4o-mini for intelligent answer evaluation
- Whisper API for speech-to-text (not yet wired to Unity)

✅ **Unity UI Layer:**
- `InterviewUIManager.cs` — main flow controller
- `FeedbackPanel.cs` — shows score and feedback after each answer
- `ReportPanel.cs` — displays final report

✅ **Secure Configuration:**
- `app/config.py` loads from `.env` file
- Environment-based settings
- Never commits secrets to GitHub

## Next Steps

1. **Get OpenAI key** and set up `.env`
2. **Build Unity UI scene** with the new UI components
3. **Add microphone recording** to Unity (currently uses keyboard simulation)
4. **Test evaluation** by running the backend and hitting the API with sample answers

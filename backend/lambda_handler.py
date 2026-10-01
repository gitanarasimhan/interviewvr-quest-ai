"""AWS Lambda entry point for the InterviewVR AI backend.

Deploy this module with the AWS Lambda Python runtime (e.g. via the SAM
CLI or Serverless Framework) and set the Lambda handler to
`lambda_handler.handler`.

Local testing (recommended before deploying):
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Deploying with AWS SAM:
    sam build
    sam deploy --guided

Required environment variables (set via the Lambda console, SAM template,
or `serverless.yml`):
    OPENAI_API_KEY
    OPENAI_MODEL
    QUEST_APP_SECRET
    REQUIRE_SIGNATURE=true
    APP_ENV=production

See `docs/QUEST_STORE_DEPLOYMENT.md` for the full deployment guide.
"""

from __future__ import annotations

from mangum import Mangum

from app.main import app

handler = Mangum(app)

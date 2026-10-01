from __future__ import annotations

import hmac
import hashlib
import json
from typing import Optional

from fastapi import HTTPException, Header

from app.config import get_settings

settings = get_settings()


class RequestSigner:
    """Sign and verify requests between Quest app and backend.
    
    The Quest app embeds a shared secret and signs each request.
    The backend verifies the signature to prevent spoofing.
    """

    @staticmethod
    def sign_request(body: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for request body.
        
        Call this on the Quest/Unity side before sending.
        """
        signature = hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    def verify_request(body: str, signature: str, secret: str) -> bool:
        """Verify request signature.
        
        Call this on the backend side to validate the request.
        """
        expected_signature = RequestSigner.sign_request(body, secret)
        return hmac.compare_digest(signature, expected_signature)


def verify_quest_signature(request_body: str, x_signature: Optional[str] = Header(None)) -> bool:
    """FastAPI dependency to verify Quest app request.
    
    Usage:
        @app.post("/api/interview/evaluate")
        def evaluate_transcript(
            payload: EvaluateRequest,
            verified: bool = Depends(verify_quest_signature)
        ) -> EvaluateResponse:
            # Only reached if signature is valid
            ...
    """
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing X-Signature header")
    
    if not RequestSigner.verify_request(request_body, x_signature, settings.quest_app_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return True

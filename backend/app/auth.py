from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Optional

from fastapi import Header, HTTPException, Request

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("interviewvr.auth")


class RequestSigner:
    """Sign and verify requests between Quest app and backend.

    The Quest app embeds a shared secret and signs each request using
    HMAC-SHA256 over ``"{timestamp}.{body}"``. Including the timestamp in
    the signed payload prevents replay attacks: the backend rejects any
    signature whose timestamp is outside an allowed window.

    The Quest/Unity side must perform the mirrored computation (see
    ``SecureAPIClient`` in ``unity/InterviewVR/Assets/Scripts/InterviewVR/Network``).
    """

    @staticmethod
    def sign_request(body: str, secret: str, timestamp: Optional[str] = None) -> str:
        """Generate HMAC-SHA256 signature for a request body.

        Call this on the Quest/Unity side before sending. ``timestamp``
        should be the Unix epoch seconds (as a string) sent in the
        ``X-Timestamp`` header alongside the resulting signature.
        """
        timestamp = timestamp or str(int(time.time()))
        message = f"{timestamp}.{body}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return signature

    @staticmethod
    def verify_request(body: str, signature: str, secret: str, timestamp: str) -> bool:
        """Verify a request signature (does not validate timestamp freshness)."""
        expected_signature = RequestSigner.sign_request(body, secret, timestamp)
        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def is_timestamp_fresh(timestamp: str, max_age_seconds: int) -> bool:
        """Return True if ``timestamp`` is within ``max_age_seconds`` of now.

        This also rejects timestamps that are too far in the future, which
        guards against clock-skew abuse.
        """
        try:
            request_time = float(timestamp)
        except (TypeError, ValueError):
            return False

        now = time.time()
        age = now - request_time
        return -max_age_seconds <= age <= max_age_seconds


async def verify_quest_signature(
    request: Request,
    x_signature: Optional[str] = Header(None),
    x_timestamp: Optional[str] = Header(None),
) -> bool:
    """FastAPI dependency verifying Quest app request signatures.

    Expects the following headers on every protected request:
        X-Signature: HMAC-SHA256 hex digest of "{timestamp}.{raw_body}"
        X-Timestamp: Unix epoch seconds the signature was generated at

    Requests older than ``settings.signature_max_age_seconds`` (default
    5 minutes) are rejected to prevent replay attacks. Failed attempts are
    logged for auditing.

    Signature verification is only enforced when ``QUEST_APP_SECRET``-based
    signing is enabled via ``REQUIRE_SIGNATURE=true``, so local development
    can continue to work without signing every request.

    Usage:
        @app.post("/api/interview/chat")
        def chat(
            payload: ChatRequest,
            verified: bool = Depends(verify_quest_signature),
        ) -> ChatResponse:
            # Only reached if signature is valid
            ...
    """
    if not settings.require_signature:
        return True

    if not x_signature or not x_timestamp:
        logger.warning("Rejected request missing signature headers from %s", request.client)
        raise HTTPException(status_code=401, detail="Missing X-Signature or X-Timestamp header")

    if not RequestSigner.is_timestamp_fresh(x_timestamp, settings.signature_max_age_seconds):
        logger.warning("Rejected request with stale/invalid timestamp from %s", request.client)
        raise HTTPException(status_code=401, detail="Request timestamp is expired or invalid")

    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    if not RequestSigner.verify_request(body, x_signature, settings.quest_app_secret, x_timestamp):
        logger.warning("Rejected request with invalid signature from %s", request.client)
        raise HTTPException(status_code=401, detail="Invalid signature")

    return True

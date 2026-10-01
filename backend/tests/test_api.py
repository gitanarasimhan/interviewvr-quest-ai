import hashlib
import hmac
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import conversation_service as conversation_service_module
from app.conversation_service import ConversationService
from app.main import app
from app.config import get_settings

client = TestClient(app)
settings = get_settings()


@pytest.fixture(autouse=True)
def reset_sessions():
    """Ensure conversation sessions don't leak between tests."""
    ConversationService._sessions.clear()
    yield
    ConversationService._sessions.clear()


def _make_mock_chat_completion(content: str) -> MagicMock:
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=content))]
    return mock_response


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_questions_endpoint_removed():
    """The static question bank endpoint has been replaced by the chat flow."""
    response = client.get("/api/interview/questions?role=software_engineer&interview_type=behavioral")
    assert response.status_code == 404


def test_start_interview_returns_question():
    with patch.object(
        conversation_service_module.client.chat.completions,
        "create",
        return_value=_make_mock_chat_completion("Tell me about a challenging bug you fixed."),
    ):
        response = client.post(
            "/api/interview/start",
            json={"role": "software_engineer", "interview_type": "behavioral"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"]
    assert payload["question"] == "Tell me about a challenging bug you fixed."
    assert payload["progress"] == 0.0


def test_chat_flow_returns_feedback_and_next_question():
    with patch.object(
        conversation_service_module.client.chat.completions,
        "create",
        return_value=_make_mock_chat_completion("What was your first question?"),
    ):
        start_response = client.post(
            "/api/interview/start",
            json={"role": "software_engineer", "interview_type": "behavioral"},
        )
    session_id = start_response.json()["session_id"]

    feedback_json = (
        '{"score": 85, "strengths": ["Clear communication"], '
        '"improvements": ["Add metrics"], "missing_information": ["Impact"], '
        '"follow_up_question": "What was the measurable impact?"}'
    )
    with patch.object(
        conversation_service_module.client.chat.completions,
        "create",
        return_value=_make_mock_chat_completion(feedback_json),
    ):
        response = client.post(
            "/api/interview/chat",
            json={
                "session_id": session_id,
                "answer": "I debugged a production incident by reviewing logs and rolling out a fix.",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["score"] == 85
    assert payload["next_question"] == "What was the measurable impact?"
    assert payload["is_complete"] is False
    assert payload["progress"] > 0


def test_chat_unknown_session_returns_404():
    response = client.post(
        "/api/interview/chat",
        json={"session_id": "does-not-exist", "answer": "Some answer"},
    )
    assert response.status_code == 404


def test_end_interview_returns_report():
    with patch.object(
        conversation_service_module.client.chat.completions,
        "create",
        return_value=_make_mock_chat_completion("Opening question?"),
    ):
        start_response = client.post(
            "/api/interview/start",
            json={"role": "software_engineer", "interview_type": "technical"},
        )
    session_id = start_response.json()["session_id"]

    feedback_json = (
        '{"score": 90, "strengths": ["Strong"], "improvements": [], '
        '"missing_information": [], "follow_up_question": "Next question?"}'
    )
    with patch.object(
        conversation_service_module.client.chat.completions,
        "create",
        return_value=_make_mock_chat_completion(feedback_json),
    ):
        client.post(
            "/api/interview/chat",
            json={"session_id": session_id, "answer": "A detailed technical answer."},
        )

    response = client.post("/api/interview/end", json={"session_id": session_id})
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["total_questions"] == 1
    assert payload["average_score"] == 90.0


def test_end_interview_unknown_session_returns_404():
    response = client.post("/api/interview/end", json={"session_id": "does-not-exist"})
    assert response.status_code == 404


def test_evaluate_answer_legacy_endpoint():
    response = client.post(
        "/api/interview/evaluate",
        json={
            "role": "software_engineer",
            "interview_type": "behavioral",
            "question_id": "se-beh-1",
            "transcript": "I led a production incident response and worked with engineering to isolate the issue.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert 0 <= payload["score"] <= 100
    assert isinstance(payload["strengths"], list)


def test_generate_report_legacy_endpoint():
    response = client.post(
        "/api/interview/report",
        json={
            "role": "software_engineer",
            "interview_type": "technical",
            "scores": [80, 90, 75],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_questions"] == 3
    assert payload["average_score"] == 81.7


def test_transcribe_rejects_path_traversal():
    response = client.post(
        "/api/interview/transcribe",
        json={"file_path": "../../etc/passwd"},
    )
    assert response.status_code == 200
    assert response.json()["transcript"] == "[Invalid file path]"


def test_hmac_signature_required_when_enabled():
    settings.require_signature = True
    try:
        response = client.post(
            "/api/interview/start",
            json={"role": "software_engineer", "interview_type": "behavioral"},
        )
        assert response.status_code == 401
    finally:
        settings.require_signature = False


def test_hmac_signature_accepted_with_valid_headers():
    settings.require_signature = True
    try:
        body = '{"role": "software_engineer", "interview_type": "behavioral"}'
        timestamp = str(int(time.time()))
        message = f"{timestamp}.{body}"
        signature = hmac.new(
            settings.quest_app_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        with patch.object(
            conversation_service_module.client.chat.completions,
            "create",
            return_value=_make_mock_chat_completion("Opening question?"),
        ):
            response = client.post(
                "/api/interview/start",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": signature,
                    "X-Timestamp": timestamp,
                },
            )
        assert response.status_code == 200
    finally:
        settings.require_signature = False


def test_hmac_signature_rejects_stale_timestamp():
    settings.require_signature = True
    try:
        body = '{"role": "software_engineer", "interview_type": "behavioral"}'
        timestamp = str(int(time.time()) - 1000)
        message = f"{timestamp}.{body}"
        signature = hmac.new(
            settings.quest_app_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        response = client.post(
            "/api/interview/start",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Signature": signature,
                "X-Timestamp": timestamp,
            },
        )
        assert response.status_code == 401
    finally:
        settings.require_signature = False

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_questions():
    response = client.get("/api/interview/questions?role=software_engineer&interview_type=behavioral")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["role"] == "software_engineer"
    assert data[0]["interview_type"] == "behavioral"


def test_evaluate_answer():
    response = client.post(
        "/api/interview/evaluate",
        json={
            "role": "software_engineer",
            "interview_type": "behavioral",
            "question_id": "se-beh-1",
            "transcript": "I led a production incident response and worked with engineering to isolate the issue. We used logs to identify the root cause and gradually rolled out a fix while monitoring the service. The result was improved reliability and fewer user-facing errors.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert 0 <= payload["score"] <= 100
    assert isinstance(payload["strengths"], list)
    assert isinstance(payload["improvements"], list)
    assert isinstance(payload["missing_information"], list)
    assert isinstance(payload["follow_up_question"], str)


def test_generate_report():
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

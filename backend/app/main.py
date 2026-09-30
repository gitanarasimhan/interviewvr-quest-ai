from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import QUESTION_BANK
from app.schemas import EvaluateRequest, EvaluateResponse, InterviewReportResponse, QuestionResponse
from app.services import InterviewEvaluationService, ReportService, TranscriptService

settings = get_settings()

app = FastAPI(
    title="InterviewVR AI API",
    version="0.1.0",
    description="MVP backend for InterviewVR AI interview coaching.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "interviewvr-ai-api", "env": settings.app_env}


@app.get("/api/interview/questions", response_model=list[QuestionResponse])
def get_questions(role: str, interview_type: str) -> list[QuestionResponse]:
    selected_role = role.lower()
    selected_type = interview_type.lower()

    if selected_role not in QUESTION_BANK:
        raise HTTPException(status_code=400, detail=f"Unsupported role: {role}")
    if selected_type not in QUESTION_BANK[selected_role]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported interview type '{interview_type}' for role '{role}'",
        )

    return [
        QuestionResponse(
            id=q.id,
            role=q.role,
            interview_type=q.interview_type,
            prompt=q.prompt,
        )
        for q in QUESTION_BANK[selected_role][selected_type]
    ]


@app.post("/api/interview/evaluate", response_model=EvaluateResponse)
def evaluate_transcript(payload: EvaluateRequest) -> EvaluateResponse:
    feedback = InterviewEvaluationService.evaluate(payload)
    return EvaluateResponse(
        score=feedback.score,
        strengths=feedback.strengths,
        improvements=feedback.improvements,
        missing_information=feedback.missing_information,
        follow_up_question=feedback.follow_up_question,
    )


@app.post("/api/interview/report", response_model=InterviewReportResponse)
def generate_report(payload: dict[str, Any]) -> InterviewReportResponse:
    role = payload.get("role", "software_engineer")
    interview_type = payload.get("interview_type", "behavioral")
    scores = payload.get("scores") or [80]

    if not isinstance(scores, list):
        raise HTTPException(status_code=400, detail="'scores' must be a list of numbers.")
    if not scores:
        raise HTTPException(status_code=400, detail="'scores' cannot be empty.")

    report = ReportService.generate_report(
        role=str(role),
        interview_type=str(interview_type),
        scores=[int(score) for score in scores],
        feedbacks=[],
    )

    return InterviewReportResponse(
        role=report["role"],
        interview_type=report["interview_type"],
        total_questions=report["total_questions"],
        average_score=float(report["average_score"]),
        summary=report["summary"],
        recommendations=report["recommendations"],
    )


@app.post("/api/interview/transcribe")
def transcribe_audio(payload: dict[str, Any]) -> dict[str, str]:
    """Transcribe audio using OpenAI Whisper.
    
    Accepts either:
    - text: Direct text input (for testing)
    - file_path: Path to audio file on disk
    """
    text = payload.get("text")
    file_path = payload.get("file_path")

    if text:
        return {"transcript": str(text)}
    if file_path:
        transcript = TranscriptService.transcribe_file(file_path)
        return {"transcript": transcript}

    return {"transcript": ""}

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_quest_signature
from app.config import get_settings
from app.conversation_service import ConversationService
from app.schemas import (
    ChatRequest,
    ChatResponse,
    EndInterviewRequest,
    EndInterviewResponse,
    EvaluateRequest,
    EvaluateResponse,
    InterviewReportResponse,
    StartInterviewRequest,
    StartInterviewResponse,
)
from app.services import InterviewEvaluationService, ReportService, TranscriptService

settings = get_settings()
logger = logging.getLogger("interviewvr.main")

app = FastAPI(
    title="InterviewVR AI API",
    version="0.2.0",
    description="Dynamic AI-driven interview backend for InterviewVR AI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health/startup check endpoint. Safe to use for Lambda warmers and load balancers."""
    return {"status": "ok", "service": "interviewvr-ai-api", "env": settings.app_env}


def _progress(session) -> float:
    completed_turns = sum(1 for turn in session.turns if turn.answer is not None)
    return min(completed_turns / settings.session_max_questions, 1.0)


@app.post(
    "/api/interview/start",
    response_model=StartInterviewResponse,
    dependencies=[Depends(verify_quest_signature)],
)
def start_interview(payload: StartInterviewRequest) -> StartInterviewResponse:
    """Initialize a new dynamic AI interview session and return the opening question."""
    session = ConversationService.start_session(role=payload.role, interview_type=payload.interview_type)
    question = session.current_turn.question if session.current_turn else ""

    return StartInterviewResponse(
        session_id=session.id,
        role=session.role,
        interview_type=session.interview_type,
        question=question,
        progress=_progress(session),
    )


@app.post(
    "/api/interview/chat",
    response_model=ChatResponse,
    dependencies=[Depends(verify_quest_signature)],
)
def chat(payload: ChatRequest) -> ChatResponse:
    """Submit a candidate answer and receive AI feedback plus the next question."""
    try:
        feedback, session = ConversationService.evaluate_answer(payload.session_id, payload.answer)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown session_id: {payload.session_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    next_question = None
    if not session.completed and session.current_turn and session.current_turn.answer is None:
        next_question = session.current_turn.question

    return ChatResponse(
        session_id=session.id,
        score=feedback.score,
        strengths=feedback.strengths,
        improvements=feedback.improvements,
        missing_information=feedback.missing_information,
        next_question=next_question,
        is_complete=session.completed,
        progress=_progress(session),
    )


@app.post(
    "/api/interview/end",
    response_model=EndInterviewResponse,
    dependencies=[Depends(verify_quest_signature)],
)
def end_interview(payload: EndInterviewRequest) -> EndInterviewResponse:
    """Finalize an interview session and return the aggregated report."""
    try:
        report = ConversationService.end_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown session_id: {payload.session_id}")

    return EndInterviewResponse(
        session_id=payload.session_id,
        role=report["role"],
        interview_type=report["interview_type"],
        total_questions=report["total_questions"],
        average_score=float(report["average_score"]),
        summary=report["summary"],
        recommendations=report["recommendations"],
    )


@app.post("/api/interview/transcribe", dependencies=[Depends(verify_quest_signature)])
def transcribe_audio(payload: dict) -> dict[str, str]:
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


@app.post(
    "/api/interview/evaluate",
    response_model=EvaluateResponse,
    dependencies=[Depends(verify_quest_signature)],
)
def evaluate_transcript(payload: EvaluateRequest) -> EvaluateResponse:
    """Evaluate a single standalone answer outside of a conversation session.

    Kept for backward compatibility and for integrations that only need a
    one-off evaluation without the full start/chat/end session lifecycle.
    """
    feedback = InterviewEvaluationService.evaluate(payload)
    return EvaluateResponse(
        score=feedback.score,
        strengths=feedback.strengths,
        improvements=feedback.improvements,
        missing_information=feedback.missing_information,
        follow_up_question=feedback.follow_up_question,
    )


@app.post(
    "/api/interview/report",
    response_model=InterviewReportResponse,
    dependencies=[Depends(verify_quest_signature)],
)
def generate_report(payload: dict) -> InterviewReportResponse:
    """Generate a report from a list of scores outside of a conversation session."""
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


try:
    # Optional dependency: only required when deploying to AWS Lambda.
    # See `lambda_handler.py` for the entry point used by the Lambda runtime.
    from mangum import Mangum

    lambda_handler = Mangum(app)
except ImportError:  # pragma: no cover - mangum is only needed on Lambda
    lambda_handler = None

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["software_engineer", "product_manager"]
InterviewType = Literal["behavioral", "technical", "case_study"]


class QuestionResponse(BaseModel):
    id: str
    role: Role
    interview_type: InterviewType
    prompt: str


class EvaluateRequest(BaseModel):
    role: Role
    interview_type: InterviewType
    question_id: str = Field(..., min_length=1)
    transcript: str = Field(..., min_length=1)


class EvaluateResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    strengths: list[str]
    improvements: list[str]
    missing_information: list[str]
    follow_up_question: str


class InterviewReportResponse(BaseModel):
    role: Role
    interview_type: InterviewType
    total_questions: int
    average_score: float
    summary: str
    recommendations: list[str]


class StartInterviewRequest(BaseModel):
    """Request to begin a new dynamic AI interview conversation."""

    role: Role
    interview_type: InterviewType = "behavioral"


class StartInterviewResponse(BaseModel):
    """Response containing the new session id and opening question."""

    session_id: str
    role: Role
    interview_type: InterviewType
    question: str
    progress: float = Field(..., ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    """Candidate's answer to the current question in an active session."""

    session_id: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """AI feedback on the candidate's answer plus the next question, if any."""

    session_id: str
    score: int = Field(..., ge=0, le=100)
    strengths: list[str]
    improvements: list[str]
    missing_information: list[str]
    next_question: Optional[str] = None
    is_complete: bool = False
    progress: float = Field(..., ge=0.0, le=1.0)


class EndInterviewRequest(BaseModel):
    """Request to finalize an interview session and get the final report."""

    session_id: str = Field(..., min_length=1)


class EndInterviewResponse(InterviewReportResponse):
    session_id: str

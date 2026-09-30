from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["software_engineer", "product_manager"]
InterviewType = Literal["behavioral", "technical"]


class QuestionResponse(BaseModel):
    id: str
    role: Role
    interview_type: InterviewType
    prompt: str


class EvaluateRequest(BaseModel):
    role: Role
    interview_type: InterviewType
    question_id: str
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

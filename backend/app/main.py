from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import QUESTION_BANK
from app.schemas import EvaluateRequest, EvaluateResponse, InterviewReportResponse, QuestionResponse

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
    return {"status": "ok", "service": "interviewvr-ai-api"}


@app.get("/api/interview/questions", response_model=list[QuestionResponse])
def get_questions(role: str, interview_type: str) -> list[QuestionResponse]:
    selected_role = role.lower()
    selected_type = interview_type.lower()

    if selected_role not in QUESTION_BANK or selected_type not in QUESTION_BANK[selected_role]:
        raise ValueError("Unsupported role or interview type")

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
    transcript = payload.transcript.strip()
    word_count = len(transcript.split())

    if word_count < 10:
        score = 45
        strengths = ["The answer was clear and relevant to the question."]
        improvements = ["Add more concrete examples and outcome details."]
        missing_information = ["Specific measurable impact or trade-offs."]
        follow_up_question = "Can you walk through one concrete example of your decision-making process?"
    elif word_count < 30:
        score = 70
        strengths = ["The answer included a clear structure and relevant examples."]
        improvements = ["Include more detail on trade-offs and business impact."]
        missing_information = ["Metrics, ownership, and final results."]
        follow_up_question = "What measurable outcome did your approach produce?"
    else:
        score = 88
        strengths = [
            "Strong structure and relevant examples.",
            "The answer showed reasoning and ownership.",
        ]
        improvements = [
            "Add a bit more emphasis on trade-offs and stakeholder alignment.",
            "Tie examples to measurable outcomes more explicitly.",
        ]
        missing_information = [
            "The exact metric or outcome of the decision.",
            "How the decision compared against alternatives.",
        ]
        follow_up_question = "How would you handle the same situation if the timeline were cut in half?"

    return EvaluateResponse(
        score=score,
        strengths=strengths,
        improvements=improvements,
        missing_information=missing_information,
        follow_up_question=follow_up_question,
    )


@app.post("/api/interview/report", response_model=InterviewReportResponse)
def generate_report(payload: dict) -> InterviewReportResponse:
    role = payload.get("role", "software_engineer")
    interview_type = payload.get("interview_type", "behavioral")
    scores = payload.get("scores", [80])
    average_score = sum(scores) / len(scores) if scores else 80

    return InterviewReportResponse(
        role=role,
        interview_type=interview_type,
        total_questions=len(scores),
        average_score=round(average_score, 1),
        summary="The candidate demonstrated solid communication skills with a generally strong answer structure and clear examples.",
        recommendations=[
            "Continue refining measurable outcomes in examples.",
            "Add deeper discussion of trade-offs and priorities.",
            "Use stronger STAR-format answers for behavioral questions.",
        ],
    )

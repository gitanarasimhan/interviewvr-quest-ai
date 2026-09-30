from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["software_engineer", "product_manager"]
InterviewType = Literal["behavioral", "technical"]


@dataclass
class Question:
    id: str
    role: Role
    interview_type: InterviewType
    prompt: str


@dataclass
class Feedback:
    score: int
    strengths: list[str]
    improvements: list[str]
    missing_information: list[str]
    follow_up_question: str


@dataclass
class InterviewReport:
    role: Role
    interview_type: InterviewType
    total_questions: int
    average_score: float
    summary: str
    recommendations: list[str]


QUESTION_BANK: dict[Role, dict[InterviewType, list[Question]]] = {
    "software_engineer": {
        "behavioral": [
            Question(
                id="se-beh-1",
                role="software_engineer",
                interview_type="behavioral",
                prompt="Tell me about a time you handled a difficult bug in production.",
            ),
            Question(
                id="se-beh-2",
                role="software_engineer",
                interview_type="behavioral",
                prompt="Describe a project where you had to work across teams to deliver a feature.",
            ),
            Question(
                id="se-beh-3",
                role="software_engineer",
                interview_type="behavioral",
                prompt="How do you prioritize competing engineering tasks when deadlines are tight?",
            ),
        ],
        "technical": [
            Question(
                id="se-tech-1",
                role="software_engineer",
                interview_type="technical",
                prompt="Explain how you would design a scalable API for a growing application.",
            ),
            Question(
                id="se-tech-2",
                role="software_engineer",
                interview_type="technical",
                prompt="How would you debug a performance issue in a backend service?",
            ),
            Question(
                id="se-tech-3",
                role="software_engineer",
                interview_type="technical",
                prompt="What trade-offs would you consider when choosing a database for a new product?",
            ),
        ],
    },
    "product_manager": {
        "behavioral": [
            Question(
                id="pm-beh-1",
                role="product_manager",
                interview_type="behavioral",
                prompt="Tell me about a time you had to make a product decision with incomplete data.",
            ),
            Question(
                id="pm-beh-2",
                role="product_manager",
                interview_type="behavioral",
                prompt="Describe a conflict between engineering and design. How did you resolve it?",
            ),
            Question(
                id="pm-beh-3",
                role="product_manager",
                interview_type="behavioral",
                prompt="How do you gather customer feedback and turn it into a roadmap decision?",
            ),
        ],
        "technical": [
            Question(
                id="pm-tech-1",
                role="product_manager",
                interview_type="technical",
                prompt="How would you evaluate whether a new feature should be built in-house or by a partner?",
            ),
            Question(
                id="pm-tech-2",
                role="product_manager",
                interview_type="technical",
                prompt="Explain how you would assess the impact of a new analytics dashboard on product decisions.",
            ),
            Question(
                id="pm-tech-3",
                role="product_manager",
                interview_type="technical",
                prompt="How would you decide whether a product metric is a leading indicator or a lagging indicator?",
            ),
        ],
    },
}

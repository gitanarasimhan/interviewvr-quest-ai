from __future__ import annotations

from typing import Any

from app.models import Feedback, InterviewType, Role


class InterviewEvaluationService:
    """Evaluates interview answers using a simple heuristic model.

    For the MVP this is intentionally lightweight and deterministic so the product can be
    developed and tested on a Windows PC without external dependencies.
    """

    @staticmethod
    def evaluate(payload: Any) -> Feedback:
        transcript = (getattr(payload, "transcript", "") or "").strip()
        word_count = len(transcript.split())

        if word_count < 20:
            score = 45
            strengths = ["The answer was clear and directly addressed the question."]
            improvements = [
                "Add concrete examples with specific details and outcomes.",
                "Describe the impact or result of your actions.",
            ]
            missing_information = [
                "Specific metrics or measurable outcomes.",
                "Context about the challenge or decision.",
            ]
            follow_up = "Can you walk through a specific example step-by-step?"

        elif word_count < 50:
            score = 70
            strengths = [
                "Good use of structure and relevant examples.",
                "Answer showed awareness of the problem.",
            ]
            improvements = [
                "Add more detail on trade-offs or alternatives you considered.",
                "Emphasize the measurable impact of your decision.",
            ]
            missing_information = [
                "Specific metrics, KPIs, or business impact.",
                "How you prioritized between competing concerns.",
            ]
            follow_up = "What was the measurable outcome or impact of your decision?"

        else:
            score = 88
            strengths = [
                "Strong structure with clear examples and outcomes.",
                "Demonstrated thoughtful decision-making and ownership.",
                "Good use of specific metrics and results.",
            ]
            improvements = [
                "Consider discussing a challenging trade-off in more detail.",
                "Add more about stakeholder alignment or communication.",
            ]
            missing_information = [
                "What you would do differently if you faced it again.",
                "How this experience shaped your approach to similar problems.",
            ]
            follow_up = "If you faced this situation again, what would you do differently?"

        return Feedback(
            score=score,
            strengths=strengths,
            improvements=improvements,
            missing_information=missing_information,
            follow_up_question=follow_up,
        )


class TranscriptService:
    """Speech-to-text stub for the MVP."""

    @staticmethod
    def transcribe(audio_data: bytes) -> str:
        return "This is a simulated transcript."


class ReportService:
    """Generate a final interview report from scores."""

    @staticmethod
    def generate_report(
        role: Role,
        interview_type: InterviewType,
        scores: list[int],
        feedbacks: list[Feedback],
    ) -> dict[str, Any]:
        average_score = sum(scores) / len(scores) if scores else 0

        improvement_themes: dict[str, int] = {}
        for feedback in feedbacks:
            for improvement in feedback.improvements:
                improvement_themes[improvement] = improvement_themes.get(improvement, 0) + 1

        recommendations = sorted(
            improvement_themes.items(), key=lambda item: item[1], reverse=True
        )
        recommendations = [item[0] for item in recommendations[:3]]

        if not recommendations:
            recommendations = [
                "Practice using the STAR method for behavioral questions.",
                "Add more quantitative metrics to demonstrate impact.",
                "Prepare deeper technical explanations for complex topics.",
            ]

        summary = f"You completed a {interview_type} interview for {role.replace('_', ' ')}. "
        if average_score >= 85:
            summary += "You demonstrated strong expertise and clear communication."
        elif average_score >= 70:
            summary += "You showed solid understanding with room to strengthen a few specific areas."
        else:
            summary += "Focus on adding more concrete examples and measurable outcomes."

        return {
            "role": role,
            "interview_type": interview_type,
            "total_questions": len(scores),
            "average_score": round(average_score, 1),
            "scores": scores,
            "summary": summary,
            "recommendations": recommendations,
        }

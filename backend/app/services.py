from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from openai import OpenAI, APIError

from app.config import get_settings
from app.models import Feedback, InterviewType, Role

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

_SAFE_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class InterviewEvaluationService:
    """Evaluates interview answers using OpenAI GPT.
    
    For the MVP, this uses GPT-4o-mini for cost-effectiveness.
    For production, you could switch to GPT-4 or GPT-4 Turbo.
    """

    @staticmethod
    def evaluate(payload: Any) -> Feedback:
        transcript = (getattr(payload, "transcript", "") or "").strip()
        role = getattr(payload, "role", "software_engineer")
        interview_type = getattr(payload, "interview_type", "behavioral")
        question_id = getattr(payload, "question_id", "")

        if not transcript:
            return InterviewEvaluationService._fallback_feedback()

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert interview coach evaluating candidate responses. Return a JSON object with: score (0-100), strengths (list), improvements (list), missing_information (list), follow_up_question (string).",
                    },
                    {
                        "role": "user",
                        "content": f"Role: {role}\nInterview Type: {interview_type}\nCandidate Answer: {transcript}",
                    },
                ],
                temperature=0.7,
            )

            result = response.choices[0].message.content
            feedback_dict = json.loads(result)

            return Feedback(
                score=int(feedback_dict.get("score", 70)),
                strengths=feedback_dict.get("strengths", []),
                improvements=feedback_dict.get("improvements", []),
                missing_information=feedback_dict.get("missing_information", []),
                follow_up_question=feedback_dict.get("follow_up_question", "Tell me more about that."),
            )
        except (APIError, json.JSONDecodeError, KeyError) as e:
            print(f"Error evaluating with OpenAI: {e}")
            return InterviewEvaluationService._fallback_feedback()

    @staticmethod
    def _fallback_feedback() -> Feedback:
        """Fallback evaluation when OpenAI is unavailable."""
        return Feedback(
            score=70,
            strengths=["The answer was clear and addressed the question."],
            improvements=["Add more concrete examples and measurable outcomes."],
            missing_information=["Specific metrics or business impact."],
            follow_up_question="Can you walk through a specific example in more detail?",
        )


class TranscriptService:
    """Convert audio to text using OpenAI Whisper API.
    
    Usage:
        transcript = TranscriptService.transcribe_file('recording.mp3')
    """

    @staticmethod
    def _resolve_safe_path(file_path: str) -> Path | None:
        """Validate `file_path` is a plain filename (no directory
        components or traversal sequences) and resolve it under the
        configured audio upload directory.

        Rejects anything containing path separators, "..", or characters
        outside of a strict allowlist, so a value like "../../etc/passwd"
        or an absolute path can never escape `settings.audio_upload_dir`.
        """
        filename = os.path.basename(file_path)
        if not filename or filename != file_path or filename in (".", ".."):
            return None
        if not _SAFE_FILENAME_PATTERN.match(filename):
            return None

        return Path(settings.audio_upload_dir) / filename

    @staticmethod
    def transcribe_file(file_path: str) -> str:
        """Transcribe an audio file using Whisper.

        `file_path` must be a plain filename located directly inside
        `settings.audio_upload_dir`; any path traversal or directory
        component is rejected before the file is opened.
        """
        safe_path = TranscriptService._resolve_safe_path(file_path)
        if safe_path is None:
            print(f"Rejected audio file path outside upload directory: {file_path}")
            return "[Invalid file path]"

        try:
            with open(safe_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=settings.whisper_model,
                    file=audio_file,
                )
            return transcript.text
        except FileNotFoundError:
            print(f"Audio file not found: {file_path}")
            return "[Audio file not found]"
        except APIError as e:
            print(f"Whisper API error: {e}")
            return "[Transcription failed]"

    @staticmethod
    def transcribe_bytes(audio_bytes: bytes, file_format: str = "mp3") -> str:
        """Transcribe audio from bytes."""
        try:
            import io
            audio_stream = io.BytesIO(audio_bytes)
            audio_stream.name = f"audio.{file_format}"
            
            transcript = client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=audio_stream,
            )
            return transcript.text
        except APIError as e:
            print(f"Whisper API error: {e}")
            return "[Transcription failed]"


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

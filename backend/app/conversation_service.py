from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import APIError, OpenAI

from app.config import get_settings
from app.models import ConversationSession, ConversationTurn, Feedback
from app.services import ReportService

settings = get_settings()
logger = logging.getLogger("interviewvr.conversation")

client = OpenAI(api_key=settings.openai_api_key)


INTERVIEWER_SYSTEM_PROMPT = """You are an experienced, friendly technical interviewer named Alex \
conducting a {interview_type} interview for a {role} role.

Ask one clear, focused question at a time. Use the candidate's previous \
answers to decide what to ask next: dig deeper into vague or incomplete \
answers with a specific follow-up, or move on to a new topic once an area \
has been explored well.

Keep questions concise (1-3 sentences) and avoid repeating earlier topics.

Example:
  Interviewer: Tell me about a time you resolved a conflict with a teammate.
  Candidate: We disagreed on a technical approach, so I suggested we prototype both.
  Interviewer: What was the outcome, and what did you learn from comparing the two prototypes?
"""

EVALUATOR_SYSTEM_PROMPT = """You are an expert interview coach evaluating a candidate's answer \
in a {interview_type} interview for a {role} role.

Return ONLY a JSON object with keys: score (0-100 integer), strengths (list \
of strings), improvements (list of strings), missing_information (list of \
strings), and follow_up_question (a single, specific follow-up question \
string that digs deeper into the candidate's answer or moves the interview \
forward).
"""


class ConversationService:
    """Manages dynamic, AI-driven interview conversations.

    Sessions are kept in an in-memory store for the lifetime of the
    process. This is sufficient for a single Lambda/uvicorn worker during
    development; swap `_sessions` for a persistent store (DynamoDB, Redis,
    etc.) for multi-instance production deployments.
    """

    _sessions: dict[str, ConversationSession] = {}

    @classmethod
    def start_session(cls, role: str, interview_type: str) -> ConversationSession:
        session = ConversationSession(role=role, interview_type=interview_type)
        question = cls._generate_question(session)
        session.turns.append(ConversationTurn(question=question))
        cls._sessions[session.id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> ConversationSession:
        session = cls._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Unknown session_id: {session_id}")
        return session

    @classmethod
    def evaluate_answer(cls, session_id: str, answer: str) -> tuple[Feedback, ConversationSession]:
        session = cls.get_session(session_id)
        turn = session.current_turn

        if turn is None or turn.answer is not None:
            raise ValueError("No pending question awaiting an answer for this session.")

        turn.answer = answer.strip()
        feedback = cls._generate_feedback(session, turn)
        turn.feedback = feedback
        session.scores.append(feedback.score)

        if len(session.turns) >= settings.session_max_questions:
            session.completed = True
        else:
            next_question = feedback.follow_up_question or cls._generate_question(session)
            session.turns.append(ConversationTurn(question=next_question))

        return feedback, session

    @classmethod
    def end_session(cls, session_id: str) -> dict[str, Any]:
        session = cls.get_session(session_id)
        session.completed = True

        feedbacks = [turn.feedback for turn in session.turns if turn.feedback is not None]
        report = ReportService.generate_report(
            role=session.role,
            interview_type=session.interview_type,
            scores=session.scores,
            feedbacks=feedbacks,
        )
        return report

    @classmethod
    def _generate_question(cls, session: ConversationSession) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": INTERVIEWER_SYSTEM_PROMPT.format(
                        interview_type=session.interview_type, role=session.role
                    ),
                },
                *session.history_as_messages(settings.session_history_window),
            ]
            if not session.turns:
                messages.append(
                    {
                        "role": "user",
                        "content": "Begin the interview with your first question.",
                    }
                )

            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.7,
                timeout=20,
            )
            question = (response.choices[0].message.content or "").strip()
            return question or cls._fallback_question(session)
        except (APIError, TimeoutError) as exc:
            logger.warning("Falling back to default question after OpenAI error: %s", exc)
            return cls._fallback_question(session)

    @classmethod
    def _generate_feedback(cls, session: ConversationSession, turn: ConversationTurn) -> Feedback:
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": EVALUATOR_SYSTEM_PROMPT.format(
                            interview_type=session.interview_type, role=session.role
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {turn.question}\nCandidate Answer: {turn.answer}",
                    },
                ],
                temperature=0.5,
                timeout=20,
                response_format={"type": "json_object"},
            )
            result = response.choices[0].message.content
            feedback_dict = json.loads(result)

            return Feedback(
                score=int(feedback_dict.get("score", 70)),
                strengths=feedback_dict.get("strengths", []),
                improvements=feedback_dict.get("improvements", []),
                missing_information=feedback_dict.get("missing_information", []),
                follow_up_question=feedback_dict.get(
                    "follow_up_question", "Can you tell me more about that?"
                ),
            )
        except (APIError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Falling back to default feedback after error: %s", exc)
            return cls._fallback_feedback()

    @staticmethod
    def _fallback_question(session: ConversationSession) -> str:
        """Deterministic fallback question used when OpenAI is unavailable."""
        fallback_questions = {
            "behavioral": "Tell me about a challenging project you worked on and how you approached it.",
            "technical": "Walk me through how you would design a system to handle a sudden spike in traffic.",
            "case_study": "How would you approach solving an ambiguous, open-ended problem with limited data?",
        }
        return fallback_questions.get(
            session.interview_type, "Tell me about a time you overcame a significant challenge."
        )

    @staticmethod
    def _fallback_feedback() -> Feedback:
        return Feedback(
            score=70,
            strengths=["The answer was clear and addressed the question."],
            improvements=["Add more concrete examples and measurable outcomes."],
            missing_information=["Specific metrics or business impact."],
            follow_up_question="Can you walk through a specific example in more detail?",
        )

    @classmethod
    def _purge_expired_sessions(cls) -> None:
        """Remove sessions older than `session_ttl_seconds` to bound memory use."""
        now = time.time()
        expired = [
            session_id
            for session_id, session in cls._sessions.items()
            if now - session.created_at > settings.session_ttl_seconds
        ]
        for session_id in expired:
            cls._sessions.pop(session_id, None)

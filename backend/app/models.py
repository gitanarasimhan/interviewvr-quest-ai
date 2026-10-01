from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Literal

Role = Literal["software_engineer", "product_manager"]
InterviewType = Literal["behavioral", "technical", "case_study"]


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


@dataclass
class ConversationTurn:
    """A single question/answer/feedback exchange in a conversation."""

    question: str
    answer: str | None = None
    feedback: Feedback | None = None


@dataclass
class ConversationSession:
    """Tracks the full state of a dynamic AI interview conversation.

    A session is created when an interview starts and is kept in memory
    (or any pluggable session store) for the lifetime of the interview.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    role: str = "software_engineer"
    interview_type: str = "behavioral"
    turns: list[ConversationTurn] = field(default_factory=list)
    scores: list[int] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed: bool = False

    @property
    def current_turn(self) -> ConversationTurn | None:
        if not self.turns:
            return None
        return self.turns[-1]

    def history_as_messages(self, max_turns: int = 6) -> list[dict[str, str]]:
        """Return the last `max_turns` exchanges formatted as chat messages.

        Keeping only a recent window of history bounds the size of the
        prompt sent to the model as the conversation grows longer.
        """
        messages: list[dict[str, str]] = []
        for turn in self.turns[-max_turns:]:
            messages.append({"role": "assistant", "content": turn.question})
            if turn.answer:
                messages.append({"role": "user", "content": turn.answer})
        return messages


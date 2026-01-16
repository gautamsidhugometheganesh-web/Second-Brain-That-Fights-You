from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.interrogation import (
    InterrogationPrompt,
    InterrogationSubmission,
    InterrogationSubmissionCreate,
)


class InterrogationStore:
    def __init__(self) -> None:
        self._sessions: list[InterrogationPrompt] = []
        self._submissions: list[InterrogationSubmission] = []

    def add_session(self, prompt: InterrogationPrompt) -> InterrogationPrompt:
        self._sessions.append(prompt)
        return prompt

    def list_sessions(self) -> list[InterrogationPrompt]:
        return list(self._sessions)

    def get_session(self, interrogation_id: UUID) -> InterrogationPrompt | None:
        return next(
            (session for session in self._sessions if session.id == interrogation_id),
            None,
        )

    def add_submission(
        self,
        interrogation_id: UUID,
        payload: InterrogationSubmissionCreate,
    ) -> InterrogationSubmission:
        record = InterrogationSubmission(
            id=uuid4(),
            interrogation_id=interrogation_id,
            answers=payload.answers,
            forced_choice=payload.forced_choice,
            finish_or_delete=payload.finish_or_delete,
            notes=payload.notes,
            created_at=datetime.now(timezone.utc),
        )
        self._submissions.append(record)
        return record

    def list_submissions(self, interrogation_id: UUID) -> list[InterrogationSubmission]:
        return [
            submission
            for submission in self._submissions
            if submission.interrogation_id == interrogation_id
        ]

    def clear(self) -> None:
        self._sessions.clear()
        self._submissions.clear()

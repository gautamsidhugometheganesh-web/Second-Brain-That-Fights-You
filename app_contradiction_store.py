from __future__ import annotations

from collections.abc import Iterable

from app.contradictions import ContradictionRecord


class ContradictionStore:
    def __init__(self) -> None:
        self._records: list[ContradictionRecord] = []

    def add_many(self, records: Iterable[ContradictionRecord]) -> list[ContradictionRecord]:
        records_list = list(records)
        self._records.extend(records_list)
        return records_list

    def list(self) -> list[ContradictionRecord]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()

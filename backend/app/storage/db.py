"""Placeholder persistence layer.

Swap this for Redis/Postgres as needed. The current implementation is a no-op
used to sketch future caching or audit trails.
"""

from __future__ import annotations

from typing import Any, Dict


class InMemoryStore:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def clear(self) -> None:
        self._data.clear()

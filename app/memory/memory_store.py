"""In-memory and persistent memory for agent context."""

from __future__ import annotations

from typing import Any

from app.models.schemas import TaskRecord


class MemoryStore:
    """Simple memory store for task context; extensible for vector DB."""

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}

    def set(self, task_id: str, key: str, value: Any) -> None:
        if task_id not in self._cache:
            self._cache[task_id] = {}
        self._cache[task_id][key] = value

    def get(self, task_id: str, key: str, default: Any = None) -> Any:
        return self._cache.get(task_id, {}).get(key, default)

    def get_all(self, task_id: str) -> dict[str, Any]:
        return dict(self._cache.get(task_id, {}))

    def clear(self, task_id: str) -> None:
        self._cache.pop(task_id, None)

    def from_task_record(self, record: TaskRecord) -> None:
        self._cache[record.task_id] = record.model_dump()


_memory_store = MemoryStore()


def get_memory_store() -> MemoryStore:
    return _memory_store

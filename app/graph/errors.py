"""Workflow execution errors with traceable fallback metadata."""

from __future__ import annotations


class WorkflowError(Exception):
    """Base workflow error."""

    def __init__(self, message: str, *, fallback_mode: str | None = None):
        super().__init__(message)
        self.fallback_mode = fallback_mode


class WorkflowExecutionError(WorkflowError):
    """LangGraph or pipeline step failed."""


class WorkflowProgrammingError(WorkflowError):
    """Non-recoverable programming error; should not be silently swallowed in tests."""

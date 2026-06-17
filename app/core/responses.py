"""Structured API envelope helpers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiErrorBody(BaseModel):
    code: str
    message: str
    recoverable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ApiErrorBody | None = None
    trace_id: str | None = None


def success_response(data: Any, *, trace_id: str | None = None) -> dict:
    return ApiResponse(success=True, data=data, trace_id=trace_id).model_dump(exclude_none=True)


def error_response(
    code: str,
    message: str,
    *,
    recoverable: bool = False,
    details: dict | None = None,
    trace_id: str | None = None,
) -> dict:
    return ApiResponse(
        success=False,
        error=ApiErrorBody(
            code=code,
            message=message,
            recoverable=recoverable,
            details=details or {},
        ),
        trace_id=trace_id,
    ).model_dump(exclude_none=True)

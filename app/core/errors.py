"""Unified application exceptions for API, MCP, and agents."""

from __future__ import annotations


class AppError(Exception):
    """Base error with stable code for clients and traces."""

    code: str = "internal_error"
    recoverable: bool = False
    http_status: int = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        recoverable: bool | None = None,
        http_status: int | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if recoverable is not None:
            self.recoverable = recoverable
        if http_status is not None:
            self.http_status = http_status
        self.details = details or {}

    def to_dict(self) -> dict:
        payload = {
            "code": self.code,
            "message": self.message,
            "recoverable": self.recoverable,
        }
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(AppError):
    code = "validation_error"
    recoverable = True
    http_status = 422


class NotFoundError(AppError):
    code = "not_found"
    recoverable = True
    http_status = 404


class SecurityError(AppError):
    code = "security_error"
    recoverable = False
    http_status = 403


class ProviderError(AppError):
    code = "provider_error"
    recoverable = True
    http_status = 502


class WorkflowError(AppError):
    code = "workflow_error"
    recoverable = True
    http_status = 500

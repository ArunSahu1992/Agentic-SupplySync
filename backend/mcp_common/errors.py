"""Common MCP error envelope, per docs/mcp/mcp-reference.md §5."""

from __future__ import annotations

from typing import Literal, TypedDict

ErrorCode = Literal["NOT_FOUND", "INVALID_INPUT", "UPSTREAM_UNAVAILABLE", "LOW_CONFIDENCE", "INTERNAL"]

_RETRYABLE_DEFAULTS: dict[ErrorCode, bool] = {
    "NOT_FOUND": False,
    "INVALID_INPUT": False,
    "UPSTREAM_UNAVAILABLE": True,
    "LOW_CONFIDENCE": False,
    "INTERNAL": False,
}


class ErrorEnvelope(TypedDict):
    code: ErrorCode
    message: str
    retryable: bool


class ToolError(Exception):
    """Raised by a tool implementation; carries the common error envelope."""

    def __init__(self, code: ErrorCode, message: str, retryable: bool | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = _RETRYABLE_DEFAULTS[code] if retryable is None else retryable

    def to_envelope(self) -> ErrorEnvelope:
        return {"code": self.code, "message": self.message, "retryable": self.retryable}

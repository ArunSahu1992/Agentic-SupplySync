"""Minimal MCP tool registry: register-by-stable-name, success-xor-error return."""

from __future__ import annotations

from typing import Any, Callable

from backend.mcp_common.errors import ToolError

ToolFunc = Callable[..., dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFunc] = {}

    def register(self, name: str) -> Callable[[ToolFunc], ToolFunc]:
        def decorator(func: ToolFunc) -> ToolFunc:
            self._tools[name] = func
            return func

        return decorator

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        try:
            return {"result": self._tools[name](**kwargs), "error": None}
        except ToolError as exc:
            return {"result": None, "error": exc.to_envelope()}

    def names(self) -> list[str]:
        return list(self._tools)

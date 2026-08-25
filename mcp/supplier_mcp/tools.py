"""`Supplier.list_disruption_events` / `Supplier.ack_event`, verbatim per docs/mcp/mcp-reference.md §6."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.mcp_common.errors import ToolError
from backend.mcp_common.tool_base import ToolRegistry
from mock_systems.supplier_api import service

registry = ToolRegistry()

_VALID_STATUSES = ("new", "processed")


@registry.register("Supplier.list_disruption_events")
def list_disruption_events(since: str | None = None, status: str | None = None) -> dict[str, Any]:
    if status is not None and status not in _VALID_STATUSES:
        raise ToolError("INVALID_INPUT", f"Invalid status: {status}")
    if since is not None:
        try:
            datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ToolError("INVALID_INPUT", f"Malformed since: {since}") from exc

    try:
        events = service.list_events(since=since, status=status)
    except Exception as exc:  # feed unreachable/corrupt
        raise ToolError("UPSTREAM_UNAVAILABLE", "Supplier feed unavailable") from exc

    return {"events": events}


@registry.register("Supplier.ack_event")
def ack_event(event_id: str) -> dict[str, str]:
    try:
        return service.ack_event(event_id)
    except KeyError as exc:
        raise ToolError("NOT_FOUND", f"Unknown event_id: {event_id}") from exc


@registry.register("Supplier.get_disruption_event")
def get_disruption_event(event_id: str) -> dict[str, Any]:
    event = service.get_event(event_id)
    if event is None:
        raise ToolError("NOT_FOUND", f"Unknown event_id: {event_id}")
    return event

"""In-memory workflow state for this slice; VALIDATED/DISCARDED tracking only."""

from __future__ import annotations

from typing import Any

from backend.models.disruption_event import DisruptionEvent
from backend.models.workflow_handoff import ValidatedDisruptionHandoff

_validated: list[dict[str, Any]] = []
_discarded: list[dict[str, Any]] = []


def hand_off_to_impact_agent(event: DisruptionEvent | dict[str, Any]) -> dict[str, Any]:
    """Record a validated disruption before the Impact Agent runs."""
    disruption = event if isinstance(event, DisruptionEvent) else DisruptionEvent.model_validate(event)
    handoff = ValidatedDisruptionHandoff(disruption=disruption)
    payload = handoff.model_dump(mode="json")
    _validated.append(payload)
    return payload


def record_impact_result(
    event: DisruptionEvent | dict[str, Any],
    affected_orders: list[dict[str, Any]],
    workflow_state: str,
) -> dict[str, Any]:
    disruption = event if isinstance(event, DisruptionEvent) else DisruptionEvent.model_validate(event)
    payload = ValidatedDisruptionHandoff(
        disruption=disruption,
        affected_orders=affected_orders,
        workflow_state=workflow_state,
    ).model_dump(mode="json")
    for index, existing in enumerate(_validated):
        if existing["disruption"]["event_id"] == disruption.event_id:
            _validated[index] = payload
            break
    else:
        _validated.append(payload)
    return payload


def record_discarded(event: DisruptionEvent | dict[str, Any]) -> dict[str, Any]:
    disruption = event if isinstance(event, DisruptionEvent) else DisruptionEvent.model_validate(event)
    payload = {"disruption": disruption.model_dump(mode="json"), "workflow_state": "discarded"}
    _discarded.append(payload)
    return payload


def get_status() -> dict[str, list[dict[str, Any]]]:
    return {"validated": list(_validated), "discarded": list(_discarded)}


def reset() -> None:
    """Test-only helper to clear in-memory state between runs."""
    _validated.clear()
    _discarded.clear()

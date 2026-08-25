from __future__ import annotations

from agents.orchestrator import state
from agents.orchestrator.agent import handle_validated_disruption
from backend.models.disruption_event import DisruptionEvent


def _event(material_id: str) -> DisruptionEvent:
    return DisruptionEvent(
        event_id="EVT-ORCHESTRATOR-TEST",
        material_id=material_id,
        disruption_type="shipment_delay",
        severity="high",
        estimated_duration_days=8,
        reported_at="2026-08-24T10:00:00Z",
        status="processed",
        classification_confidence=1.0,
    )


def test_orchestrator_hands_valid_event_to_impact_agent() -> None:
    payload = handle_validated_disruption(_event("DYE-NAVY-4052"))

    assert payload["workflow_state"] == "impact_analyzed"
    assert {order["order_id"] for order in payload["affected_orders"]} == {"ORD-4521", "ORD-4522"}


def test_orchestrator_closes_known_material_with_no_impact() -> None:
    payload = handle_validated_disruption(_event("THR-POLY-22"))

    assert payload["workflow_state"] == "no_impact"
    assert payload["affected_orders"] == []
    assert state.get_status()["discarded"] == []

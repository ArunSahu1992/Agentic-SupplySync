from __future__ import annotations

from agents.impact_agent.agent import analyze_disruption
from backend.models.disruption_event import DisruptionEvent


def _event(material_id: str) -> DisruptionEvent:
    return DisruptionEvent(
        event_id="EVT-IMPACT-TEST",
        material_id=material_id,
        disruption_type="shipment_delay",
        severity="high",
        estimated_duration_days=8,
        reported_at="2026-08-24T10:00:00Z",
        status="processed",
        classification_confidence=1.0,
    )


def test_impact_agent_maps_affected_orders() -> None:
    result = analyze_disruption(_event("DYE-NAVY-4052"))

    assert result.workflow_state == "impact_analyzed"
    assert {order.order_id for order in result.affected_orders} == {"ORD-4521", "ORD-4522"}


def test_impact_agent_reports_no_impact() -> None:
    result = analyze_disruption(_event("THR-POLY-22"))

    assert result.workflow_state == "no_impact"
    assert result.affected_orders == []

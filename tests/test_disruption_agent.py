from __future__ import annotations

from agents.disruption_agent.agent import run_once
from agents.orchestrator import state as orchestrator_state


def test_run_once_validates_high_confidence_and_discards_noise() -> None:
    orchestrator_state.reset()

    results = run_once()

    by_id = {result.event_id: result for result in results}
    assert by_id["EVT-9001"].status == "VALIDATED"  # high severity, long duration
    assert by_id["EVT-9002"].status == "VALIDATED"  # medium severity, moderate duration
    assert by_id["EVT-9007"].status == "DISCARDED"  # low severity, short duration -> noise

    status = orchestrator_state.get_status()
    assert {event["disruption"]["event_id"] for event in status["validated"]} == {"EVT-9001", "EVT-9002"}
    assert {event["disruption"]["event_id"] for event in status["discarded"]} == {"EVT-9007"}

    valid_handoff = next(event for event in status["validated"] if event["disruption"]["event_id"] == "EVT-9001")
    assert valid_handoff["workflow_state"] == "impact_analyzed"
    assert {order["order_id"] for order in valid_handoff["affected_orders"]} == {"ORD-4521", "ORD-4522"}
    assert valid_handoff["disruption"]["disruption_type"] == "shipment_delay"
    assert "event_type" not in valid_handoff["disruption"]


def test_run_once_acks_every_processed_event() -> None:
    orchestrator_state.reset()
    run_once()

    from mcp.supplier_mcp.tools import registry

    remaining_new = registry.call("Supplier.list_disruption_events", status="new")
    assert remaining_new["result"]["events"] == []

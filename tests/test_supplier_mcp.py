from __future__ import annotations

from mcp.supplier_mcp.tools import registry


def test_list_disruption_events_returns_new_seeded_events() -> None:
    outcome = registry.call("Supplier.list_disruption_events", status="new")
    assert outcome["error"] is None
    event_ids = {event["event_id"] for event in outcome["result"]["events"]}
    assert event_ids == {"EVT-9001", "EVT-9002", "EVT-9007"}


def test_list_disruption_events_invalid_status() -> None:
    outcome = registry.call("Supplier.list_disruption_events", status="bogus")
    assert outcome["result"] is None
    assert outcome["error"]["code"] == "INVALID_INPUT"
    assert outcome["error"]["retryable"] is False


def test_list_disruption_events_malformed_since() -> None:
    outcome = registry.call("Supplier.list_disruption_events", since="not-a-date")
    assert outcome["result"] is None
    assert outcome["error"]["code"] == "INVALID_INPUT"


def test_ack_event_round_trip() -> None:
    ack = registry.call("Supplier.ack_event", event_id="EVT-9001")
    assert ack["error"] is None
    assert ack["result"] == {"event_id": "EVT-9001", "status": "processed"}

    remaining = registry.call("Supplier.list_disruption_events", status="new")
    event_ids = {event["event_id"] for event in remaining["result"]["events"]}
    assert "EVT-9001" not in event_ids


def test_ack_event_not_found() -> None:
    outcome = registry.call("Supplier.ack_event", event_id="EVT-DOES-NOT-EXIST")
    assert outcome["result"] is None
    assert outcome["error"]["code"] == "NOT_FOUND"
    assert outcome["error"]["retryable"] is False

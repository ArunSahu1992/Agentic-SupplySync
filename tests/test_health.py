import base64
import importlib
import json

from fastapi.testclient import TestClient

import agents.disruption_agent.agent as disruption_agent_module
from backend.api.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_valid_flow() -> None:
    response = client.post("/demo/flows/valid")
    assert response.status_code == 200

    payload = response.json()
    assert payload["flow"] == "valid"
    assert payload["processed_events"][0]["status"] == "VALIDATED"
    assert payload["workflow_status"]["validated"][0]["disruption"]["disruption_type"] == "shipment_delay"
    assert payload["workflow_status"]["validated"][0]["workflow_state"] == "impact_analyzed"
    assert payload["workflow_status"]["validated"][0]["affected_orders"]


def test_demo_noise_flow() -> None:
    response = client.post("/demo/flows/noise")
    assert response.status_code == 200

    payload = response.json()
    assert payload["flow"] == "noise"
    assert payload["processed_events"][0]["status"] == "DISCARDED"
    assert payload["workflow_status"]["validated"] == []
    assert payload["workflow_status"]["discarded"][0]["workflow_state"] == "discarded"


def test_supplier_disruption_webhook_accepts_without_processing_by_default() -> None:
    response = client.post(
        "/events/supplier-disruptions",
        json={
            "event_id": "EVT-WEBHOOK-VALID",
            "material_id": "DYE-NAVY-4052",
            "event_type": "shipment_delay",
            "severity": "high",
            "estimated_duration_days": 8,
            "reported_at": "2026-08-23T09:10:00Z",
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["created"] is True
    assert payload["processed_events"] == []


def test_supplier_disruption_webhook_triggers_disruption_agent_by_default() -> None:
    reset = client.post("/demo/reset")
    assert reset.status_code == 200

    response = client.post(
        "/events/supplier-disruptions",
        json={
            "event_id": "EVT-WEBHOOK-AUTO",
            "material_id": "DYE-NAVY-4052",
            "event_type": "shipment_delay",
            "severity": "high",
            "estimated_duration_days": 8,
            "reported_at": "2026-08-23T09:12:00Z",
        },
    )

    assert response.status_code == 202
    assert response.json()["created"] is True

    status_response = client.get("/demo/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["validated"][0]["disruption"]["event_id"] == "EVT-WEBHOOK-AUTO"


def test_supplier_disruption_webhook_processes_when_local_flag_enabled(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLYSYNC_LOCAL_EVENT_PROCESSING", "true")

    response = client.post(
        "/events/supplier-disruptions",
        json={
            "event_id": "EVT-WEBHOOK-LOCAL",
            "material_id": "DYE-NAVY-4052",
            "event_type": "shipment_delay",
            "severity": "high",
            "estimated_duration_days": 8,
            "reported_at": "2026-08-23T09:15:00Z",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_events"][0]["status"] == "VALIDATED"
    assert payload["workflow_status"]["validated"][0]["workflow_state"] == "impact_analyzed"


def test_pubsub_push_endpoint_processes_disruption_event() -> None:
    payload = {
        "event_id": "EVT-PUBSUB-VALID",
        "material_id": "DYE-NAVY-4052",
        "event_type": "shipment_delay",
        "severity": "high",
        "estimated_duration_days": 8,
        "reported_at": "2026-08-23T09:20:00Z",
    }
    envelope = {
        "message": {
            "data": base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8"),
            "message_id": "msg-1",
        },
        "subscription": "projects/demo/subscriptions/disruption-events-push",
    }

    response = client.post("/events/pubsub/disruption-events", json=envelope)

    assert response.status_code == 200
    body = response.json()
    assert body["event_id"] == "EVT-PUBSUB-VALID"
    assert body["processed_events"][0]["status"] == "VALIDATED"


def test_duplicate_event_id_is_idempotent(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLYSYNC_LOCAL_EVENT_PROCESSING", "true")
    payload = {
        "event_id": "EVT-DUPLICATE",
        "material_id": "DYE-NAVY-4052",
        "event_type": "shipment_delay",
        "severity": "high",
        "estimated_duration_days": 8,
        "reported_at": "2026-08-23T09:25:00Z",
    }

    first = client.post("/events/supplier-disruptions", json=payload)
    second = client.post("/events/supplier-disruptions", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["created"] is True
    assert second.json()["created"] is False
    assert second.json()["processed_events"] == []


def test_adk_demo_tools_hidden_unless_flag_enabled(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_ADK_DEMO_TOOLS", raising=False)
    reloaded = importlib.reload(disruption_agent_module)
    tool_names = [tool.func.__name__ for tool in reloaded.root_agent.tools]
    assert tool_names == ["check_new_disruption_events", "get_workflow_status"]

    monkeypatch.setenv("ENABLE_ADK_DEMO_TOOLS", "true")
    reloaded = importlib.reload(disruption_agent_module)
    tool_names = [tool.func.__name__ for tool in reloaded.root_agent.tools]
    assert "run_valid_disruption_flow" in tool_names
    assert "run_noise_disruption_flow" in tool_names

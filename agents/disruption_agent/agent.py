"""Poll → classify → self-correction checkpoint 1 (drop noise) → hand off to Orchestrator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from agents.disruption_agent.classifier import classify_confidence
from agents.disruption_agent.config import CONFIDENCE_THRESHOLD
from agents.orchestrator.agent import handle_validated_disruption
from agents.orchestrator import state as orchestrator_state
from backend.models.disruption_event import DisruptionEvent
from mcp.supplier_mcp.tools import registry
from mock_systems.supplier_api import service

_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
_ENABLE_ADK_DEMO_TOOLS = os.getenv("ENABLE_ADK_DEMO_TOOLS", "false").lower() == "true"


@dataclass
class DisruptionAgentResult:
    event_id: str
    status: str  # "VALIDATED" | "DISCARDED"
    classification_confidence: float
    payload: dict[str, Any]


def run_once() -> list[DisruptionAgentResult]:
    fetch = registry.call("Supplier.list_disruption_events", status="new")
    if fetch["error"] is not None:
        raise RuntimeError(f"Supplier MCP error: {fetch['error']}")

    results: list[DisruptionAgentResult] = []
    for event in fetch["result"]["events"]:
        result = process_event(event["event_id"])
        if result is not None:
            results.append(result)
    return results


def process_event(event_id: str) -> DisruptionAgentResult | None:
    event_result = registry.call("Supplier.get_disruption_event", event_id=event_id)
    if event_result["error"] is not None:
        raise RuntimeError(f"Supplier MCP lookup error: {event_result['error']}")

    event = event_result["result"]
    if event["status"] != "new":
        return None
    return _process_event(event)


def _process_event(event: dict[str, Any]) -> DisruptionAgentResult:
    confidence = classify_confidence(event)

    ack = registry.call("Supplier.ack_event", event_id=event["event_id"])
    if ack["error"] is not None:
        raise RuntimeError(f"Supplier MCP ack error: {ack['error']}")

    classified_event = _to_disruption_event(
        {**event, "status": ack["result"]["status"], "classification_confidence": confidence}
    )
    if confidence < CONFIDENCE_THRESHOLD:
        payload = orchestrator_state.record_discarded(classified_event)
        return DisruptionAgentResult(event["event_id"], "DISCARDED", confidence, payload)

    payload = handle_validated_disruption(classified_event)
    return DisruptionAgentResult(event["event_id"], "VALIDATED", confidence, payload)


def _to_disruption_event(event: dict[str, Any]) -> DisruptionEvent:
    return DisruptionEvent.model_validate(
        {
            "event_id": event["event_id"],
            "material_id": event["material_id"],
            "disruption_type": event["event_type"],
            "severity": event["severity"],
            "estimated_duration_days": event.get("estimated_duration_days"),
            "reported_at": event["reported_at"],
            "status": event["status"],
            "classification_confidence": event["classification_confidence"],
        }
    )


def check_new_disruption_events() -> dict[str, Any]:
    """Poll the Supplier MCP for new disruption events, classify each, and either
    discard it as noise (low confidence) or hand it off to the Orchestrator as VALIDATED.

    Returns:
        A dict with the list of processed events, each containing event_id,
        status ("VALIDATED" or "DISCARDED"), and classification_confidence.
    """
    results = run_once()
    return {
        "processed_events": [
            {
                "event_id": r.event_id,
                "status": r.status,
                "classification_confidence": r.classification_confidence,
                "payload": r.payload,
            }
            for r in results
        ]
    }


def get_workflow_status() -> dict[str, list[dict[str, Any]]]:
    """Return the current in-memory workflow state: events validated and handed off
    to the Impact Agent, and events discarded as noise."""
    return orchestrator_state.get_status()


def run_valid_disruption_flow() -> dict[str, Any]:
    """ADK Web demo-only helper: seeds one valid event and runs the first-slice workflow."""
    service.reset_events()
    orchestrator_state.reset()
    service.insert_event(
        event_id="EVT-ADK-VALID",
        material_id="DYE-NAVY-4052",
        event_type="shipment_delay",
        severity="high",
        estimated_duration_days=8,
        reported_at="2026-08-23T09:00:00Z",
    )
    return {
        "flow": "valid",
        "processed_events": [result.__dict__ for result in run_once()],
        "workflow_status": orchestrator_state.get_status(),
    }


def run_noise_disruption_flow() -> dict[str, Any]:
    """ADK Web demo-only helper: seeds one noisy event and runs the discard path."""
    service.reset_events()
    orchestrator_state.reset()
    service.insert_event(
        event_id="EVT-ADK-NOISE",
        material_id="FAB-COTTON-118",
        event_type="shipment_delay",
        severity="low",
        estimated_duration_days=1,
        reported_at="2026-08-23T09:05:00Z",
    )
    return {
        "flow": "noise",
        "processed_events": [result.__dict__ for result in run_once()],
        "workflow_status": orchestrator_state.get_status(),
    }


_tools = [
    FunctionTool(check_new_disruption_events),
    FunctionTool(get_workflow_status),
]
if _ENABLE_ADK_DEMO_TOOLS:
    _tools.extend(
        [
            FunctionTool(run_valid_disruption_flow),
            FunctionTool(run_noise_disruption_flow),
        ]
    )


root_agent = Agent(
    name="disruption_agent",
    model=_GEMINI_MODEL,
    description=(
        "Polls the Supplier/Logistics MCP server for disruption events, classifies "
        "each by confidence, drops noise, and hands validated events to the Orchestrator."
    ),
    instruction=(
        "You are the Disruption Agent in the Agentic SupplySync workflow. "
        f"Use `check_new_disruption_events` to poll for and classify new supplier disruption "
        f"events (ack + classify each; events below confidence {CONFIDENCE_THRESHOLD} are "
        "discarded as noise, the rest are handed off to the Orchestrator as VALIDATED). "
        "Demo seeding tools are available only when ENABLE_ADK_DEMO_TOOLS=true. "
        "Use `get_workflow_status` to report what has been validated or discarded so far. "
        "Never invent disruption events or classifications outside of these tools."
    ),
    tools=_tools,
)

import os
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from agents.disruption_agent.agent import process_event
from agents.orchestrator import state as orchestrator_state
from backend.services.event_ingress import (
    SupplierDisruptionPayload,
    handle_pubsub_disruption_event,
    handle_supplier_disruption_event,
)
from mock_systems.erp_api.seed import seed_data
from mock_systems.supplier_api import service

app = FastAPI(title="SupplySync API", version="0.1.0")


@app.on_event("startup")
def initialize_demo_data() -> None:
    seed_data()

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def api_root() -> dict[str, str]:
    return {
        "service": "SupplySync API",
        "health": "/health",
        "docs": "/docs",
        "workflow_status": "/demo/status",
    }


@app.post("/demo/reset")
def reset_demo() -> dict[str, str]:
    service.reset_events()
    orchestrator_state.reset()
    return {"status": "reset"}


@app.post("/demo/flows/{flow_name}")
def run_demo_flow(flow_name: str) -> dict[str, Any]:
    service.reset_events()
    orchestrator_state.reset()

    if flow_name == "valid":
        return {
            "flow": "valid",
            **handle_supplier_disruption_event(
                SupplierDisruptionPayload(
                    event_id="EVT-UI-VALID",
                    material_id="DYE-NAVY-4052",
                    event_type="shipment_delay",
                    severity="high",
                    estimated_duration_days=8,
                    reported_at="2026-08-23T09:00:00Z",
                ),
                process_immediately=True,
            ),
        }
    if flow_name == "noise":
        return {
            "flow": "noise",
            **handle_supplier_disruption_event(
                SupplierDisruptionPayload(
                    event_id="EVT-UI-NOISE",
                    material_id="FAB-COTTON-118",
                    event_type="shipment_delay",
                    severity="low",
                    estimated_duration_days=1,
                    reported_at="2026-08-23T09:05:00Z",
                ),
                process_immediately=True,
            ),
        }
    return {"error": f"Unknown demo flow: {flow_name}"}


@app.post("/events/supplier-disruptions", status_code=status.HTTP_202_ACCEPTED)
def ingest_supplier_disruption(
    payload: SupplierDisruptionPayload,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    process_immediately = os.getenv("SUPPLYSYNC_LOCAL_EVENT_PROCESSING", "false").lower() == "true"
    result = handle_supplier_disruption_event(payload, process_immediately=process_immediately)
    if not process_immediately and result["event_status"] == "new":
        background_tasks.add_task(process_event, payload.event_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK if process_immediately else status.HTTP_202_ACCEPTED,
        content=result,
    )


@app.post("/events/pubsub/disruption-events")
def ingest_pubsub_disruption(envelope: dict[str, Any]) -> dict[str, Any]:
    try:
        return handle_pubsub_disruption_event(envelope, process_immediately=True)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.errors(include_url=False),
        )


@app.get("/demo/status")
def get_demo_status() -> dict[str, list[dict[str, Any]]]:
    return orchestrator_state.get_status()

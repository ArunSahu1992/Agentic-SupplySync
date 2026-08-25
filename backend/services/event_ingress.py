from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from agents.disruption_agent.agent import process_event
from agents.orchestrator import state as orchestrator_state
from mock_systems.supplier_api import service

EventType = Literal["shortage", "shipment_delay", "quality_hold"]
Severity = Literal["low", "medium", "high"]


class SupplierDisruptionPayload(BaseModel):
    event_id: str
    material_id: str
    event_type: EventType
    severity: Severity
    estimated_duration_days: int | None = Field(default=None, ge=0)
    reported_at: datetime | None = None


class PubSubMessage(BaseModel):
    data: str
    message_id: str | None = None
    publish_time: str | None = None


class PubSubPushEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str | None = None


def handle_supplier_disruption_event(
    payload: SupplierDisruptionPayload | dict[str, Any],
    *,
    process_immediately: bool = False,
) -> dict[str, Any]:
    disruption = payload if isinstance(payload, SupplierDisruptionPayload) else SupplierDisruptionPayload.model_validate(payload)
    insert_result = service.insert_event(
        event_id=disruption.event_id,
        material_id=disruption.material_id,
        event_type=disruption.event_type,
        severity=disruption.severity,
        estimated_duration_days=disruption.estimated_duration_days,
        reported_at=disruption.reported_at.isoformat() if disruption.reported_at else None,
    )

    response: dict[str, Any] = {
        "event_id": disruption.event_id,
        "accepted": True,
        "created": insert_result["created"],
        "event_status": insert_result["status"],
        "processed_events": [],
        "workflow_status": orchestrator_state.get_status(),
    }

    if process_immediately and insert_result["created"]:
        processed = process_event(disruption.event_id)
        if processed is not None:
            response["processed_events"] = [processed.__dict__]
        response["workflow_status"] = orchestrator_state.get_status()

    return response


def handle_pubsub_disruption_event(envelope: dict[str, Any], *, process_immediately: bool = True) -> dict[str, Any]:
    pubsub_envelope = PubSubPushEnvelope.model_validate(envelope)
    try:
        raw_json = base64.b64decode(pubsub_envelope.message.data).decode("utf-8")
        payload = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValidationError.from_exception_data(
            "PubSubPushEnvelope",
            [
                {
                    "type": "value_error",
                    "loc": ("message", "data"),
                    "msg": "message.data must be base64-encoded JSON",
                    "input": pubsub_envelope.message.data,
                    "ctx": {"error": exc},
                }
            ],
        ) from exc

    return handle_supplier_disruption_event(payload, process_immediately=process_immediately)

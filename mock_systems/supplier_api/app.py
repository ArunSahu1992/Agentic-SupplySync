"""Standalone FastAPI app for the mock Supplier/Logistics feed (run: uvicorn mock_systems.supplier_api.app:app)."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
import httpx

from mock_systems.supplier_api import service
from mock_systems.supplier_api.seed import seed_events

app = FastAPI(title="Mock Supplier/Logistics API", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    seed_events()


@app.get("/events")
def get_events(since: str | None = None, status: str | None = None) -> dict[str, Any]:
    return {"events": service.list_events(since=since, status=status)}


@app.post("/events/{event_id}/ack")
def post_ack(event_id: str) -> dict[str, str]:
    try:
        return service.ack_event(event_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}")


@app.post("/events")
def post_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Manual insert endpoint for live demo triggering."""
    result = service.insert_event(**payload)
    trigger_url = os.getenv("SUPPLYSYNC_TRIGGER_URL")
    if result["created"] and trigger_url:
        try:
            response = httpx.post(
                trigger_url,
                json=payload,
                timeout=5.0,
            )
            response.raise_for_status()
            result["triggered"] = True
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Unable to trigger SupplySync backend: {exc}",
            ) from exc
    else:
        result["triggered"] = False
    return result

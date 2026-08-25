"""Canonical `DisruptionEvent` model, per docs/mcp/mcp-reference.md §6.1."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EventType = Literal["shortage", "shipment_delay", "quality_hold"]
Severity = Literal["low", "medium", "high"]
EventStatus = Literal["new", "processed"]


class DisruptionEvent(BaseModel):
    event_id: str
    material_id: str
    disruption_type: EventType
    severity: Severity
    estimated_duration_days: int | None = None
    reported_at: datetime
    status: EventStatus
    # Produced by the Disruption Agent during classification, not by the feed.
    classification_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

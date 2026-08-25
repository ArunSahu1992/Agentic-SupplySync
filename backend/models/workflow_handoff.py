"""Workflow handoff models between agents."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.models.affected_order_context import AffectedOrderContext
from backend.models.disruption_event import DisruptionEvent

WorkflowState = Literal["awaiting_impact_agent", "impact_analyzed", "no_impact"]


class ValidatedDisruptionHandoff(BaseModel):
    disruption: DisruptionEvent
    affected_orders: list[AffectedOrderContext] = Field(default_factory=list)
    workflow_state: WorkflowState = "awaiting_impact_agent"

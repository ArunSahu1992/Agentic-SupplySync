from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from backend.models.affected_order_context import AffectedOrderContext
from backend.models.disruption_event import DisruptionEvent
from mcp.erp_mcp.tools import registry


@dataclass(frozen=True)
class ImpactResult:
    event_id: str
    material_id: str
    affected_orders: list[AffectedOrderContext]
    workflow_state: str


def analyze_disruption(event: DisruptionEvent | dict[str, Any]) -> ImpactResult:
    disruption = event if isinstance(event, DisruptionEvent) else DisruptionEvent.model_validate(event)
    outcome = registry.call("ERP.get_affected_orders", material_id=disruption.material_id)
    if outcome["error"] is not None:
        raise RuntimeError(f"ERP MCP error: {outcome['error']}")

    affected_orders = [
        AffectedOrderContext(
            order_id=order["order_id"],
            product=order["product_name"],
            supplier=order["supplier"],
            ordered_qty=order["ordered_qty"],
            affected_qty=order["affected_qty"],
            total_order_amount=order["total_order_amount"],
            requester_name=order["requester_name"],
            requester_email=order["requester_email"],
            estimated_delivery_date=date.fromisoformat(order["estimated_delivery_date"])
            if order["estimated_delivery_date"]
            else None,
        )
        for order in outcome["result"]["orders"]
    ]
    return ImpactResult(
        event_id=disruption.event_id,
        material_id=disruption.material_id,
        affected_orders=affected_orders,
        workflow_state="impact_analyzed" if affected_orders else "no_impact",
    )

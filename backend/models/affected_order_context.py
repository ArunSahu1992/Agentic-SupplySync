"""Order-level context populated by the Impact Agent after ERP/OMS lookup."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class AffectedOrderContext(BaseModel):
    order_id: str
    product: str
    supplier: str | None = None
    ordered_qty: int = Field(ge=0)
    affected_qty: int = Field(ge=0)
    total_order_amount: float = Field(ge=0)
    requester_name: str
    requester_email: str
    estimated_delivery_date: date | None = None

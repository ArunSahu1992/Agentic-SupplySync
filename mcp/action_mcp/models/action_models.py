from pydantic import BaseModel, Field


class SupplyActionRequest(BaseModel):

    workflow_id: str

    order_id: str

    product: str

    supplier: str


    # ========================================================
    # ACTION
    # ========================================================

    recommended_action: str

    reason: str


    # ========================================================
    # ORDER QUANTITY
    # ========================================================

    ordered_qty: int = Field(
        gt=0
    )

    affected_qty: int = Field(
        ge=0
    )


    # ========================================================
    # FINANCIAL DATA
    # ========================================================

    total_order_amount: float = Field(
        ge=0
    )

    additional_discount_percent: float = Field(
        default=0,
        ge=0,
        le=100,
    )


    # ========================================================
    # DELIVERY / RESCHEDULE
    # ========================================================

    estimated_delivery_date: str | None = None

    reschedule_days: int = Field(
        default=0,
        ge=0,
    )


    # ========================================================
    # REQUESTER
    # ========================================================

    requester_name: str = ""

    requester_email: str = ""
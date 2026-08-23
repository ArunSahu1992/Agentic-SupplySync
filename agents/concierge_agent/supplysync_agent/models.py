from pydantic import BaseModel, Field
from typing import Optional


class SupplyOrder(BaseModel):

    """
    Canonical SupplySync input contract.
    """


    # ========================================================
    # WORKFLOW
    # ========================================================

    workflow_id: str = Field(
        description="Unique workflow identifier."
    )


    # ========================================================
    # ORDER
    # ========================================================

    order_id: str = Field(
        description="Unique supply order identifier."
    )

    product: str = Field(
        description="Product affected by the supply disruption."
    )

    supplier: str = Field(
        description="Supplier associated with the order."
    )


    # ========================================================
    # QUANTITY
    # ========================================================

    ordered_qty: int = Field(
        gt=0,
        description="Total quantity originally ordered."
    )

    affected_qty: int = Field(
        ge=0,
        description="Quantity affected by the disruption."
    )


    # ========================================================
    # DISRUPTION
    # ========================================================

    disruption_type: str = Field(
        description=(
            "Type of supply disruption."
        )
    )

    requested_action: str = Field(
        default="auto_recommend",
        description="Requested business action."
    )


    # ========================================================
    # BUSINESS IMPACT
    # ========================================================

    impact_value_usd: float = Field(
        default=0,
        ge=0,
        description="Estimated business impact in USD."
    )


    # ========================================================
    # DELAY / POLICY INPUT
    # ========================================================

    delay_days: int = Field(
        default=0,
        ge=0,
        description="Expected delay in calendar days."
    )

    customer_critical: bool = Field(
        default=False,
        description=(
            "Whether the order has a customer-critical commitment."
        )
    )

    patient_critical: bool = Field(
        default=False,
        description=(
            "Whether the order affects a patient-critical allocation."
        )
    )


    # ========================================================
    # FINANCIAL DATA
    # ========================================================

    total_order_amount: float = Field(
        default=0,
        ge=0,
        description="Original total order amount."
    )


    # ========================================================
    # REQUESTER
    # ========================================================

    requester_name: str = Field(
        default=""
    )

    requester_email: str = Field(
        default=""
    )


    # ========================================================
    # DELIVERY
    # ========================================================

    estimated_delivery_date: Optional[str] = Field(
        default=None,
        description=(
            "Current estimated delivery date before any "
            "rescheduling, in YYYY-MM-DD format."
        )
    )
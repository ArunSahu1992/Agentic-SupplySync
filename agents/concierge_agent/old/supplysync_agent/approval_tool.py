from google.adk.tools import FunctionTool


def approve_supply_action(
    order_id: str,
    product: str,
    supplier: str,
    recommended_action: str,
    reason: str,
    confidence: float,
    reschedule_days: int | None = None,
    additional_discount_percent: float = 0.0,
) -> dict:

    """
    Requires human confirmation before an approved
    SupplySync action can continue.

    The policy decision values are included in the
    confirmation arguments so the reviewer can see:

    - recommended action
    - policy reason
    - reschedule duration
    - customer discount
    - confidence
    """

    return {
        "approval_status": "APPROVED",

        "human_response": "YES",

        "order_id": order_id,

        "product": product,

        "supplier": supplier,

        "recommended_action": recommended_action,

        "reason": reason,

        "reschedule_days": reschedule_days,

        "additional_discount_percent":
            additional_discount_percent,

        "confidence": confidence,
    }


approval_tool = FunctionTool(

    func=approve_supply_action,

    require_confirmation=True,
)
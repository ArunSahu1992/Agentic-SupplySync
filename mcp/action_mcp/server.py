import json

from mcp.server.fastmcp import FastMCP

from config import settings

from models.action_models import (
    SupplyActionRequest,
)

from services.action_service import (
    ActionService,
)

from services.audit_service import (
    AuditService,
)

from services.notification_service import (
    NotificationService,
)


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP(

    "SupplySync Action Executor MCP Server",

    host=settings.ACTION_MCP_HOST,

    port=settings.ACTION_MCP_PORT,
)


# ============================================================
# SERVICES
# ============================================================

action_service = ActionService()

audit_service = AuditService()

notification_service = NotificationService()


# ============================================================
# MCP TOOL
# ============================================================

@mcp.tool()
def execute_supply_action(

    workflow_id: str,

    order_id: str,

    product: str,

    supplier: str,

    recommended_action: str,

    reason: str,


    # ========================================================
    # ORDER DATA
    # ========================================================

    ordered_qty: int,

    affected_qty: int,


    # ========================================================
    # FINANCIAL DATA
    # ========================================================

    total_order_amount: float,

    additional_discount_percent: float = 0,


    # ========================================================
    # REQUESTER
    # ========================================================

    requester_name: str = "",

    requester_email: str = "",


    # ========================================================
    # DELIVERY DATA
    # ========================================================

    estimated_delivery_date: str | None = None,

    reschedule_days: int = 0,

) -> str:

    """
    Execute an approved SupplySync business action.

    Supported actions:

    - reschedule_order
    - cancel_order_refund
    - partial_order_revised_payment
    """


    # ========================================================
    # CREATE REQUEST
    # ========================================================

    request = SupplyActionRequest(

        workflow_id=workflow_id,

        order_id=order_id,

        product=product,

        supplier=supplier,

        recommended_action=recommended_action,

        reason=reason,

        ordered_qty=ordered_qty,

        affected_qty=affected_qty,

        total_order_amount=total_order_amount,

        additional_discount_percent=(
            additional_discount_percent
        ),

        requester_name=requester_name,

        requester_email=requester_email,

        estimated_delivery_date=(
            estimated_delivery_date
        ),

        reschedule_days=reschedule_days,
    )


    # ========================================================
    # STEP 1 — EXECUTE ACTION
    # ========================================================

    action_result = action_service.execute(
        request
    )


    # ========================================================
    # NORMALIZE RESULT
    #
    # All services return dictionaries.
    # ========================================================

    action_status = action_result.get(
        "status",
        "FAILED",
    )


    # ========================================================
    # STEP 2 — AUDIT
    # ========================================================

    audit_result = audit_service.write_log(

        request=request,

        action_result=action_result,
    )


    audit_status = audit_result.get(
        "status",
        "FAILED",
    )


    # ========================================================
    # STEP 3 — NOTIFICATION
    # ========================================================

    notification_result = (
        notification_service.notify(

            request=request,

            action_result=action_result,
        )
    )


    notification_status = (
        notification_result.get(
            "status",
            "NOT_SENT",
        )
    )


    # ========================================================
    # EXECUTION DETAILS
    # ========================================================

    execution_details = action_result.get(
        "execution_details",

        action_result.get(
            "details",
            {},
        ),
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    response = {

        # ----------------------------------------------------
        # WORKFLOW
        # ----------------------------------------------------

        "workflow_id": workflow_id,

        "order_id": order_id,

        "product": product,

        "supplier": supplier,


        # ----------------------------------------------------
        # ACTION
        # ----------------------------------------------------

        "action_status": action_status,

        "executed_action": (
            action_result.get(
                "executed_action"
            )
        ),

        "executed_at": (
            action_result.get(
                "executed_at"
            )
        ),

        "action_error": (
            action_result.get(
                "error"
            )
        ),


        # ----------------------------------------------------
        # EXECUTION DETAILS
        # ----------------------------------------------------

        "execution_details": (
            execution_details
        ),


        # ----------------------------------------------------
        # AUDIT
        # ----------------------------------------------------

        "audit_status": audit_status,

        "audit_id": (
            audit_result.get(
                "audit_id"
            )
        ),

        "audit_logged_at": (
            audit_result.get(
                "logged_at"
            )
        ),

        "audit_error": (
            audit_result.get(
                "error"
            )
        ),


        # ----------------------------------------------------
        # NOTIFICATION
        # ----------------------------------------------------

        "notification_status": (
            notification_status
        ),

        "notification_recipient": (
            notification_result.get(
                "recipient_email"
            )
        ),

        "notification_error": (
            notification_result.get(
                "error"
            )
        ),
    }


    return json.dumps(

        response,

        indent=2,

        default=str,
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(

        "\n"
        "============================================================\n"
        "SupplySync Action Executor MCP Server\n"
        "============================================================\n"
        f"Host: {settings.ACTION_MCP_HOST}\n"
        f"Port: {settings.ACTION_MCP_PORT}\n"
        "============================================================\n"
    )


    mcp.run(

        transport="streamable-http"
    )
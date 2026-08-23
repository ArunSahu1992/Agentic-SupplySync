from fastmcp import FastMCP

from notification_mcp.email_service import send_email
from notification_mcp.audit_service import create_audit_log


# ============================================================
# CREATE MCP SERVER
# ============================================================

mcp = FastMCP(
    name="SupplySync Notification MCP"
)


# ============================================================
# PROCESS NOTIFICATION
# ============================================================

@mcp.tool()
def process_notification(

    notification_mode: str,

    workflow_id: str,

    order_id: str,

    workflow_decision: str,

    recommended_action: str,

    final_status: str,

    action_execution: dict,

    recipient: str | None = None,

    subject: str | None = None,

    message: str | None = None,

) -> dict:


    notification_mode = (
        notification_mode.upper().strip()
    )


    if notification_mode not in [

        "EMAIL",

        "LOG",

        "BOTH",

    ]:

        return {

            "notification_status": "FAILED",

            "error": (
                "notification_mode must be "
                "EMAIL, LOG, or BOTH."
            ),
        }


    result = {

        "notification_mode": notification_mode,

        "workflow_id": workflow_id,

        "order_id": order_id,

        "email_result": None,

        "audit_result": None,
    }


    # ========================================================
    # EMAIL
    # ========================================================

    if notification_mode in [

        "EMAIL",

        "BOTH",

    ]:


        email_result = send_email(

            recipient=recipient or "",

            subject=subject or "",

            message=message or "",
        )


        result[
            "email_result"
        ] = email_result


    # ========================================================
    # AUDIT LOG
    # ========================================================

    if notification_mode in [

        "LOG",

        "BOTH",

    ]:


        audit_result = create_audit_log(

            workflow_id=workflow_id,

            order_id=order_id,

            workflow_decision=workflow_decision,

            recommended_action=recommended_action,

            final_status=final_status,

            action_execution=action_execution,
        )


        result[
            "audit_result"
        ] = audit_result


    # ========================================================
    # FINAL STATUS
    # ========================================================

    result[
        "notification_status"
    ] = "SUCCESS"


    return result


# ============================================================
# RUN MCP SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run(

        transport="streamable-http",

        host="0.0.0.0",

        port=9002,
    )
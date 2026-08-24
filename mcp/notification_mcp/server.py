"""
SupplySync Notification MCP Tool Server.

This module exposes a FastMCP server tool that orchestrates outbound transactional 
notifications across multiple channels (EMAIL, SMS, or BOTH) for SupplySync workflows.
"""

from fastmcp import FastMCP

from notification_mcp.email_service import send_email
from notification_mcp.sms_service import send_sms


# ============================================================
# CREATE MCP SERVER
# ============================================================

# Initialize FastMCP server instance for registering tools and handling transport
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
    recipient: str | None = None,
    subject: str | None = None,
    message: str | None = None,
    mobile_number: str | None = None,
) -> dict:
    """Process and dispatch multi-channel notifications via standard Email and SMS services.

    Acts as an MCP tool interface to evaluate dispatch criteria, delegate payload delivery to 
    channel services based on `notification_mode`, and aggregate final delivery execution state.

    Args:
        notification_mode (str): Channel delivery target mode ("EMAIL", "SMS", or "BOTH").
        workflow_id (str): Unique identifier of the triggering business workflow instance.
        order_id (str): Unique order reference associated with the notification payload.
        recipient (str, optional): Target email address (Required for "EMAIL" / "BOTH").
        subject (str, optional): Title/Subject line of email (Required for "EMAIL" / "BOTH").
        message (str, optional): Text message payload content to transmit.
        mobile_number (str, optional): Destination phone number (Required for "SMS" / "BOTH").

    Returns:
        dict: Consolidated execution report including channel response details and overall status:
            {
                "notification_mode": str,
                "workflow_id": str,
                "order_id": str,
                "email_result": dict | None,
                "sms_result": dict | None,
                "notification_status": "SUCCESS" | "FAILED",
                "error": str (optional)
            }
    """
    # Standardize notification mode casing and strip whitespace
    notification_mode = (
        notification_mode.upper().strip()
    )

    # ========================================================
    # VALIDATE NOTIFICATION MODE
    # ========================================================

    # Enforce allowed notification routing strategy enum options
    if notification_mode not in [
        "EMAIL",
        "SMS",
        "BOTH",
    ]:
        return {
            "notification_status": "FAILED",
            "error": (
                "notification_mode must be "
                "EMAIL, SMS, or BOTH."
            ),
        }

    # ========================================================
    # INITIAL RESULT
    # ========================================================

    # Initialize tracking payload dictionary structure
    result = {
        "notification_mode": notification_mode,
        "workflow_id": workflow_id,
        "order_id": order_id,
        "email_result": None,
        "sms_result": None,
    }

    # ========================================================
    # SEND EMAIL
    # ========================================================

    # Dispatch to Email service module if designated by mode
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
    # SEND SMS
    # ========================================================

    # Dispatch to SMS service module if designated by mode
    if notification_mode in [
        "SMS",
        "BOTH",
    ]:
        sms_result = send_sms(
            mobile_number=mobile_number or "",
            message=message or "",
        )

        result[
            "sms_result"
        ] = sms_result

    # ========================================================
    # FINAL STATUS
    # ========================================================

    # Set initial verification flags
    email_success = True
    sms_success = True

    # Evaluate Email execution success status if executed
    if notification_mode in [
        "EMAIL",
        "BOTH",
    ]:
        email_success = (
            result["email_result"] is not None
            and
            result["email_result"].get(
                "email_status"
            ) == "SENT"
        )

    # Evaluate SMS execution success status if executed
    if notification_mode in [
        "SMS",
        "BOTH",
    ]:
        sms_success = (
            result["sms_result"] is not None
            and
            result["sms_result"].get(
                "sms_status"
            ) == "SENT"
        )

    # Calculate final aggregated status based on channel outcomes
    if email_success and sms_success:
        result[
            "notification_status"
        ] = "SUCCESS"
    else:
        result[
            "notification_status"
        ] = "FAILED"

    return result


# ============================================================
# RUN MCP SERVER
# ============================================================

# Execute MCP HTTP server entry point when run directly
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=9002,
    )
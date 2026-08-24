"""
Order Cancellation and Refund Processing Service.

This module provides the core service responsible for executing cancellation and refund 
workflows triggered by supply action requests, compiling standardized action execution results.
"""

from datetime import datetime, timezone

from models.action_models import SupplyActionRequest


class CancellationRefundService:
    """Service handling the orchestration of order cancellations and refund processing."""

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:
        """Execute the order cancellation and refund request.

        Args:
            request (SupplyActionRequest): Incoming request object carrying order identification
                and financial details required for cancellation and processing.

        Returns:
            dict: Standardized action execution response containing status, ISO-formatted UTC timestamp,
                and nested execution breakdown details.
        """

        # ====================================================
        # FUTURE INTEGRATION
        # ====================================================
        #
        # 1. Call Order API to cancel the order.
        # 2. Call Payment API to initiate refund.
        #
        # ====================================================

        # Capture audit timestamp in UTC for standard serialization
        executed_at = datetime.now(
            timezone.utc
        )

        # Retrieve total refundable value directly from the supply action payload
        refund_amount = (
            request.total_order_amount
        )

        # Construct and return standardized success outcome payload
        return {

            "status": "SUCCESS",

            "executed_action":
                "cancel_order_refund",

            "executed_at":
                executed_at.isoformat(),

            "error": None,


            "execution_details": {

                "order_id":
                    request.order_id,

                "order_status":
                    "CANCELLED",

                "refund_status":
                    "INITIATED",

                "refund_amount":
                    refund_amount,

                "message": (
                    f"Order {request.order_id} "
                    "cancelled and refund initiated."
                ),
            },
        }
from datetime import datetime, timezone

from models.action_models import SupplyActionRequest


class CancellationRefundService:

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:

        # ====================================================
        # FUTURE INTEGRATION
        # ====================================================
        #
        # 1. Call Order API to cancel the order.
        # 2. Call Payment API to initiate refund.
        #
        # ====================================================

        executed_at = datetime.now(
            timezone.utc
        )


        refund_amount = (
            request.total_order_amount
        )


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
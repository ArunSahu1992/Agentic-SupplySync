from models.action_models import SupplyActionRequest

from services.action_services.reschedule_service import (
    RescheduleService,
)

from services.action_services.cancellation_refund_service import (
    CancellationRefundService,
)

from services.action_services.partial_order_service import (
    PartialOrderService,
)


class ActionService:


    def __init__(self):

        self.reschedule_service = (
            RescheduleService()
        )

        self.cancellation_refund_service = (
            CancellationRefundService()
        )

        self.partial_order_service = (
            PartialOrderService()
        )


    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:


        # ====================================================
        # NORMALIZE ACTION
        # ====================================================

        action = (

            request.recommended_action

            .strip()

            .lower()

        )


        # ====================================================
        # ACTION 1
        # RESCHEDULE ORDER
        # ====================================================

        if action == "reschedule_order":

            return (
                self.reschedule_service.execute(
                    request
                )
            )


        # ====================================================
        # ACTION 2
        # CANCEL ORDER + REFUND
        # ====================================================

        if action in [

            "cancel_order_refund",

            "cancel_order_and_initiate_refund",

        ]:

            return (

                self.cancellation_refund_service.execute(
                    request
                )

            )


        # ====================================================
        # ACTION 3
        # PARTIAL ORDER + REVISED PAYMENT
        # ====================================================

        if action in [

            "partial_order_revised_payment",

            "confirm_partial_order_with_revised_payment",

            "partial_order",

        ]:

            return (

                self.partial_order_service.execute(
                    request
                )

            )


        # ====================================================
        # UNKNOWN ACTION
        # ====================================================

        return {

            "status": "FAILED",

            "executed_action":
                request.recommended_action,

            "executed_at": None,

            "error": (

                f"Unsupported action: "

                f"{request.recommended_action}"

            ),

            "execution_details": {},
        }
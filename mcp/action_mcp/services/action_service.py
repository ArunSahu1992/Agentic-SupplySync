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
    """Orchestrator service for handling supply action workflows.

    Dispatches incoming supply action requests to dedicated domain services
    (Reschedule, Cancellation/Refund, and Partial Order) based on the
    `recommended_action` specified in the request object.
    """

    def __init__(self):
        """Initializes the action service and instantiates all dependent sub-services.

        Creates instances of:
            - RescheduleService: Handles order rescheduling logic.
            - CancellationRefundService: Handles order cancellation and refund initiation.
            - PartialOrderService: Handles partial fulfillment and payment revision logic.
        """
        # Service responsible for processing order reschedule requests
        self.reschedule_service = (
            RescheduleService()
        )

        # Service responsible for processing order cancellations and refunds
        self.cancellation_refund_service = (
            CancellationRefundService()
        )

        # Service responsible for processing partial order fulfillments and payment adjustments
        self.partial_order_service = (
            PartialOrderService()
        )

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:
        """Executes the appropriate supply action based on the request configuration.

        Normalizes the `recommended_action` string (lowercasing and stripping whitespace)
        and evaluates it against supported action types to delegate execution to the 
        corresponding sub-service.

        Args:
            request (SupplyActionRequest): Data transfer object containing the 
                recommended action string and required contextual action parameters.

        Returns:
            dict: Response dictionary returned directly from the executed sub-service,
                or a standardized failure response dictionary if the action is unsupported.

        Failure Return Format:
            {
                "status": "FAILED",
                "executed_action": str,
                "executed_at": None,
                "error": str,
                "execution_details": dict
            }
        """

        # ====================================================
        # NORMALIZE ACTION
        # Clean input string to enable case-insensitive, trim-safe matching.
        # ====================================================

        action = (

            request.recommended_action

            .strip()

            .lower()

        )

        # ====================================================
        # ACTION 1
        # RESCHEDULE ORDER
        # Triggers logic to update order fulfillment timeline.
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
        # Triggers full cancellation and refund workflow.
        # Supports aliases: 'cancel_order_refund', 'cancel_order_and_initiate_refund'
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
        # Triggers partial fulfillment adjustment and payment recalculation.
        # Supports aliases: 'partial_order_revised_payment', 
        #                   'confirm_partial_order_with_revised_payment', 
        #                   'partial_order'
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
        # Fallback response for unhandled or invalid action strings.
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
from datetime import datetime, timezone

from models.action_models import SupplyActionRequest


class PartialOrderService:

    """
    Handles:

    partial_order_revised_payment

    The discount percentage comes from
    the Policy MCP decision.

    This service does NOT decide
    the discount percentage.
    """


    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:


        # ====================================================
        # QUANTITY CALCULATION
        # ====================================================

        fulfillable_qty = (

            request.ordered_qty

            -

            request.affected_qty

        )


        if fulfillable_qty < 0:

            fulfillable_qty = 0


        # ====================================================
        # PARTIAL RATIO
        # ====================================================

        partial_ratio = (

            fulfillable_qty

            /

            request.ordered_qty

        )


        # ====================================================
        # REVISED ORDER AMOUNT
        # ====================================================

        original_partial_amount = round(

            request.total_order_amount
            *
            partial_ratio,

            2,

        )


        # ====================================================
        # POLICY DISCOUNT
        # ====================================================

        additional_discount_percent = (

            request.additional_discount_percent

        )


        discount_amount = round(

            original_partial_amount
            *
            additional_discount_percent
            /
            100,

            2,

        )


        # ====================================================
        # FINAL AMOUNT
        # ====================================================

        revised_final_amount = round(

            original_partial_amount
            -
            discount_amount,

            2,

        )


        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {

            "status": "SUCCESS",

            "executed_action":
                "partial_order_revised_payment",

            "executed_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "error": None,


            "execution_details": {

                "ordered_qty":
                    request.ordered_qty,

                "affected_qty":
                    request.affected_qty,

                "fulfillable_qty":
                    fulfillable_qty,

                "fulfillment_percentage":
                    round(
                        partial_ratio * 100,
                        2,
                    ),

                "total_order_amount":
                    request.total_order_amount,

                "original_partial_amount":
                    original_partial_amount,

                "additional_discount_percent":
                    additional_discount_percent,

                "discount_amount":
                    discount_amount,

                "revised_final_amount":
                    revised_final_amount,
            },
        }
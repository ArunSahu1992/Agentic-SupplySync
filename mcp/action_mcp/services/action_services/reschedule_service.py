from datetime import datetime, timedelta, timezone

from models.action_models import SupplyActionRequest


class RescheduleService:

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> dict:

        try:

            # ====================================================
            # VALIDATE DELIVERY DATE
            # ====================================================

            if not request.estimated_delivery_date:

                return {
                    "status": "FAILED",

                    "executed_action":
                        "reschedule_order",

                    "executed_at":
                        None,

                    "error": (
                        "estimated_delivery_date is required "
                        "for reschedule_order."
                    ),

                    "execution_details": {},
                }


            # ====================================================
            # PARSE ORIGINAL DELIVERY DATE
            # ====================================================

            original_date = datetime.strptime(
                request.estimated_delivery_date,
                "%Y-%m-%d",
            ).date()


            # ====================================================
            # GET RESCHEDULE DAYS FROM POLICY
            # ====================================================

            additional_days = (
                request.reschedule_days
            )


            # ====================================================
            # CALCULATE REVISED DELIVERY DATE
            # ====================================================

            revised_date = (
                original_date
                + timedelta(
                    days=additional_days
                )
            )


            # ====================================================
            # DISCOUNT FROM POLICY
            #
            # The Action MCP does NOT decide the discount.
            # It uses additional_discount_percent received from
            # the Policy MCP through the SupplySync application.
            # ====================================================

            additional_discount_percent = (
                request.additional_discount_percent
            )


            # ====================================================
            # CALCULATE DISCOUNT
            #
            # For rescheduled orders, the discount applies to
            # the full order payment.
            # ====================================================

            discount_amount = round(

                request.total_order_amount
                *
                additional_discount_percent
                /
                100,

                2,
            )


            # ====================================================
            # CALCULATE FINAL PAYMENT
            # ====================================================

            revised_final_amount = round(

                request.total_order_amount
                -
                discount_amount,

                2,
            )


            # ====================================================
            # EXECUTION TIME
            # ====================================================

            executed_at = datetime.now(
                timezone.utc
            ).isoformat().replace(
                "+00:00",
                "Z",
            )


            # ====================================================
            # SUCCESS
            # ====================================================

            return {

                "status": "SUCCESS",

                "executed_action":
                    "reschedule_order",

                "executed_at":
                    executed_at,

                "error":
                    None,


                # ================================================
                # EXECUTION DETAILS
                # ================================================

                "execution_details": {

                    "order_id":
                        request.order_id,


                    # --------------------------------------------
                    # DELIVERY
                    # --------------------------------------------

                    "estimated_delivery_date":
                        original_date.isoformat(),

                    "additional_days":
                        additional_days,

                    "revised_delivery_date":
                        revised_date.isoformat(),


                    # --------------------------------------------
                    # PAYMENT
                    # --------------------------------------------

                    "total_order_amount":
                        request.total_order_amount,

                    "additional_discount_percent":
                        additional_discount_percent,

                    "discount_amount":
                        discount_amount,

                    "revised_final_amount":
                        revised_final_amount,
                },
            }


        except Exception as error:

            return {

                "status": "FAILED",

                "executed_action":
                    "reschedule_order",

                "executed_at":
                    None,

                "error":
                    str(error),

                "execution_details": {},
            }
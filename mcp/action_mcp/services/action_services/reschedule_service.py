"""Order rescheduling action service module.

This module processes order rescheduling requests by computing updated delivery dates
and applying policy-mandated discounts across full order payments.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from models.action_models import SupplyActionRequest


class RescheduleService:
    """Service responsible for processing order rescheduling workflows.

    Calculates new estimated delivery dates based on additional delay days and applies
    policy-provided discount percentages to total order values.
    """

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> Dict[str, Any]:
        """Executes order delivery date recalculation and revised pricing.

        Args:
            request (SupplyActionRequest): Incoming request object containing 
                delivery date strings, delay days, and policy discount percentages.

        Returns:
            Dict[str, Any]: Structured execution envelope containing action status, 
                timestamps, updated delivery schedules, and revised payment figures.
        """

        try:

            # ====================================================
            # VALIDATE DELIVERY DATE
            # Ensure mandatory baseline delivery date is supplied.
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
            # Convert YYYY-MM-DD input string to date object.
            # ====================================================

            original_date = datetime.strptime(
                request.estimated_delivery_date,
                "%Y-%m-%d",
            ).date()

            # ====================================================
            # GET RESCHEDULE DAYS FROM POLICY
            # Extract delay extension days determined by upstream Policy MCP.
            # ====================================================

            additional_days = (
                request.reschedule_days
            )

            # ====================================================
            # CALCULATE REVISED DELIVERY DATE
            # Shift baseline delivery date forward by specified day count.
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
            # Subtract computed discount from total original order price.
            # ====================================================

            revised_final_amount = round(

                request.total_order_amount
                -
                discount_amount,

                2,
            )

            # ====================================================
            # EXECUTION TIME
            # Format current UTC timestamp in ISO-8601 format with 'Z' suffix.
            # ====================================================

            executed_at = datetime.now(
                timezone.utc
            ).isoformat().replace(
                "+00:00",
                "Z",
            )

            # ====================================================
            # SUCCESS
            # Return payload detailing updated dates and financial adjustments.
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

            # Catch processing or parsing errors and encapsulate in failure response
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
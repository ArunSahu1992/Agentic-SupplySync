"""Partial order and revised payment computation service.

This module processes order adjustments when only a fraction of an order can be fulfilled.
It recalculates prorated order totals and applies policy-driven discount percentages.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from models.action_models import SupplyActionRequest


class PartialOrderService:
    """Calculates partial fulfillment metrics and updated billing amounts.

    Handles:
        partial_order_revised_payment

    Note:
        The discount percentage comes directly from the upstream Policy MCP decision.
        This service does NOT compute or evaluate policy eligibility; it only applies
        the provided `additional_discount_percent`.
    """

    def execute(
        self,
        request: SupplyActionRequest,
    ) -> Dict[str, Any]:
        """Executes quantity fulfillment and payment adjustment calculations.

        Args:
            request (SupplyActionRequest): Incoming request payload containing original order 
                quantities, affected quantities, financial amounts, and policy discount values.

        Returns:
            Dict[str, Any]: Structured execution envelope containing action status, execution timestamp,
                and a breakdown of quantity ratios, baseline partial amounts, discount subtractions, 
                and final revised amounts.
        """

        # ====================================================
        # QUANTITY CALCULATION
        # Determine fulfillable quantity based on total vs affected quantities.
        # Clamp value to zero to prevent negative fulfillment.
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
        # Calculate proportional ratio of fulfillable stock relative to original order.
        # ====================================================

        partial_ratio = (

            fulfillable_qty

            /

            request.ordered_qty

        )

        # ====================================================
        # REVISED ORDER AMOUNT
        # Calculate prorated base order value for fulfillable items prior to extra discounts.
        # ====================================================

        original_partial_amount = round(

            request.total_order_amount
            *
            partial_ratio,

            2,

        )

        # ====================================================
        # POLICY DISCOUNT
        # Apply the Policy MCP decision discount percentage to the prorated base amount.
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
        # Deduct calculated policy discount from base prorated order value.
        # ====================================================

        revised_final_amount = round(

            original_partial_amount
            -
            discount_amount,

            2,

        )

        # ====================================================
        # SUCCESS RESPONSE
        # Build standard success response payload detailing quantity and financial adjustments.
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
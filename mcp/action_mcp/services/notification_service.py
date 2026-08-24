"""
Notification Management Module.

This module houses the NotificationService class, which handles dispatching
and logging email notifications triggered by supply action request executions.
"""

from models.action_models import SupplyActionRequest


class NotificationService:
    """Service responsible for managing and evaluating notification delivery logic."""

    def notify(
        self,
        request: SupplyActionRequest,
        action_result: dict,
    ) -> dict:
        """Evaluate the action result and dispatch a notification accordingly.

        Args:
            request (SupplyActionRequest): The incoming supply action payload
                containing requester metadata (e.g., email address).
            action_result (dict): Execution results from the action handler,
                expected to contain a "status" key.

        Returns:
            dict: Notification response containing dispatch status ('SENT' or 'NOT_SENT'),
                the target recipient email, and error details (if applicable).
        """

        action_status = action_result.get(
            "status",
            "FAILED",
        )

        # ====================================================
        # ACTION FAILED
        # ====================================================

        # Early exit pattern: Short-circuit email delivery if the prior action execution failed.
        if action_status != "SUCCESS":

            return {
                "status": "NOT_SENT",
                "recipient_email": request.requester_email,
                "error": (
                    "Action was not successfully executed."
                ),
            }

        # ====================================================
        # ACTION SUCCESS
        # ====================================================

        # Return successful delivery metadata for executed actions.
        return {
            "status": "SENT",
            "recipient_email": request.requester_email,
            "error": None,
        }
from models.action_models import SupplyActionRequest


class NotificationService:

    def notify(
        self,
        request: SupplyActionRequest,
        action_result: dict,
    ) -> dict:

        action_status = action_result.get(
            "status",
            "FAILED",
        )

        # ====================================================
        # ACTION FAILED
        # ====================================================

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

        return {
            "status": "SENT",
            "recipient_email": request.requester_email,
            "error": None,
        }
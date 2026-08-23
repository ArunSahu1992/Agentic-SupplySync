from datetime import datetime, timezone
import uuid

from models.action_models import SupplyActionRequest


class AuditService:

    def write_log(
        self,
        request: SupplyActionRequest,
        action_result: dict,
    ) -> dict:

        # Future integration:
        #
        # Insert into database.
        #
        # Example:
        #
        # INSERT INTO action_audit_log (...)

        audit_id = str(
            uuid.uuid4()
        )

        logged_at = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "status": "SUCCESS",

            "audit_id": audit_id,

            "workflow_id": request.workflow_id,

            "order_id": request.order_id,

            "action": (
                action_result.get(
                    "executed_action"
                )
            ),

            "action_status": (
                action_result.get(
                    "status"
                )
            ),

            "logged_at": logged_at,

            "error": None,
        }
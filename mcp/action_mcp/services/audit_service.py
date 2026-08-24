"""Audit logging service for tracking supply action outcomes.

This module formats and generates audit log records following action execution.
It assigns unique audit IDs, stamps UTC timestamps, and builds standardized audit payloads.
"""

from datetime import datetime, timezone
from typing import Any, Dict
import uuid

from models.action_models import SupplyActionRequest


class AuditService:
    """Service responsible for constructing and persisting audit trail records.
    
    Acts as the audit boundary for the action execution pipeline, capturing key identifiers
    (workflow_id, order_id), timestamps, and execution status results.
    """

    def write_log(
        self,
        request: SupplyActionRequest,
        action_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generates an audit log entry for a completed or attempted supply action request.

        Args:
            request (SupplyActionRequest): The original incoming action request data model.
            action_result (Dict[str, Any]): The result envelope returned by the executed service handler.

        Returns:
            Dict[str, Any]: Structured audit log record ready for consumption or storage downstream.
                Format:
                {
                    "status": "SUCCESS",
                    "audit_id": str (UUID4),
                    "workflow_id": str,
                    "order_id": str,
                    "action": str | None,
                    "action_status": str | None,
                    "logged_at": str (ISO 8601 UTC timestamp),
                    "error": None
                }
        """

        # Future integration:
        #
        # Insert into database.
        #
        # Example:
        #
        # INSERT INTO action_audit_log (...)

        # Generate a unique version 4 UUID identifier for this specific audit log entry
        audit_id = str(
            uuid.uuid4()
        )

        # Capture current system time in ISO-8601 format with explicit UTC timezone offset
        logged_at = datetime.now(
            timezone.utc
        ).isoformat()

        # Construct standardized audit record payload dictionary
        return {
            "status": "SUCCESS",

            # Metadata identifiers
            "audit_id": audit_id,

            "workflow_id": request.workflow_id,

            "order_id": request.order_id,

            # Extract execution results safely from action response payload
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

            # Timestamp metadata
            "logged_at": logged_at,

            # Exception indicator placeholder
            "error": None,
        }
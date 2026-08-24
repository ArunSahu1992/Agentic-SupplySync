"""
Summary:
    Defines result models used across the SupplySync workflow.

Description:
    This module contains standardized Pydantic response models for
    action execution, audit logging, and notification processing.

    These models provide a consistent structure for communicating
    success, failure, timestamps, identifiers, recipients, and
    error details between different agents and workflow components.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ActionExecutionResult(BaseModel):
    """
    Summary:
        Represents the final outcome of an action executed by the
        Action Execution Agent.

    Description:
        This model is used after a workflow action has been approved
        and executed. It captures the execution status, the associated
        order, the action that was performed, the execution timestamp,
        and any error details if the execution fails.

    Usage:
        Returned by the Action Execution Agent after attempting to
        execute an approved business or supply-chain action.
    """

    status: str = Field(
        ...,
        description="Final status of the action execution, such as SUCCESS or FAILED.",
    )

    order_id: str = Field(
        ...,
        description="Unique identifier of the order associated with the executed action.",
    )

    executed_action: str = Field(
        ...,
        description="Name or description of the business action that was executed.",
    )

    executed_at: str = Field(
        ...,
        description="Timestamp indicating when the action execution was completed.",
    )

    error: Optional[str] = Field(
        default=None,
        description=(
            "Error message or failure details when execution fails. "
            "This value is None when execution is successful."
        ),
    )


class AuditResult(BaseModel):
    """
    Summary:
        Represents the outcome of recording workflow activity or
        decisions in the audit logging system.

    Description:
        This model provides traceability for important workflow events,
        including approved actions, rejected requests, policy decisions,
        revisions, and execution results.

    Usage:
        Returned by the audit or logging component after recording
        workflow activity for compliance, monitoring, and traceability.
    """

    status: str = Field(
        ...,
        description="Final status of the audit logging operation, such as SUCCESS or FAILED.",
    )

    audit_id: str = Field(
        ...,
        description="Unique identifier generated for the created audit record.",
    )

    logged_at: str = Field(
        ...,
        description="Timestamp indicating when the workflow event was logged.",
    )

    error: Optional[str] = Field(
        default=None,
        description=(
            "Error message or failure details when audit logging fails. "
            "This value is None when logging is successful."
        ),
    )


class NotificationResult(BaseModel):
    """
    Summary:
        Represents the final outcome of sending a workflow notification
        to an intended recipient.

    Description:
        This model captures whether a notification was successfully
        delivered or failed. It records the recipient and includes
        error information when the notification process encounters
        a failure.

    Usage:
        Returned by the Notification Agent after attempting to send
        an email or other supported notification.
    """

    status: str = Field(
        ...,
        description="Final notification delivery status, such as SENT or FAILED.",
    )

    recipient_email: str = Field(
        ...,
        description="Email address of the intended recipient of the notification.",
    )

    error: Optional[str] = Field(
        default=None,
        description=(
            "Error message or failure details when notification delivery fails. "
            "This value is None when the notification is sent successfully."
        ),
    )
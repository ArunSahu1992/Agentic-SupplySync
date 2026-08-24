from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class EmailMessage:
    """
    Data Transfer Object (DTO) for constructing outbound email payloads.
    
    Attributes:
        recipient: Target email address for the message.
        subject: Subject line header text.
        body: Main body content (plain text or HTML string).
        from_email: Originating email address (defaults to system fallback).
        metadata: Key-value dictionary for tracking dynamic header data, 
                  correlation IDs, or template variables.
    """
    recipient: str
    subject: str
    body: str
    from_email: str = "noreply@example.com"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    """
    Data model representing a persistent audit log entry for workflow actions.
    
    Attributes:
        workflow_id: Unique identifier for the executing workflow process.
        order_id: Target business order identifier associated with this event.
        workflow_decision: Policy or system evaluation result.
        recommended_action: Suggested operational action triggered by policy.
        final_status: Terminal state of the execution cycle.
        action_execution: Execution result details, payloads, or error trace maps.
        audit_id: Primary key/UUID of the recorded audit entry (populated post-persist).
        audit_status: Health/processing state of the audit event itself (defaults to 'SUCCESS').
    """
    workflow_id: str
    order_id: str
    workflow_decision: str
    recommended_action: str
    final_status: str
    action_execution: Dict[str, Any]
    audit_id: str | None = None
    audit_status: str = "SUCCESS"
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class EmailMessage:
    recipient: str
    subject: str
    body: str
    from_email: str = "noreply@example.com"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    workflow_id: str
    order_id: str
    workflow_decision: str
    recommended_action: str
    final_status: str
    action_execution: Dict[str, Any]
    audit_id: str | None = None
    audit_status: str = "SUCCESS"

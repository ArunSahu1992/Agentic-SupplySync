from typing import Optional

from pydantic import BaseModel


class ActionExecutionResult(BaseModel):

    status: str

    order_id: str

    executed_action: str

    executed_at: str

    error: Optional[str] = None


class AuditResult(BaseModel):

    status: str

    audit_id: str

    logged_at: str

    error: Optional[str] = None


class NotificationResult(BaseModel):

    status: str

    recipient_email: str

    error: Optional[str] = None
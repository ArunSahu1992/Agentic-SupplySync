import json
import os
from datetime import datetime
from pathlib import Path


def write_workflow_log(
    workflow_id: str,
    order_id: str,
    decision: str,
    message: str,
) -> str:
    """
    Write SupplySync workflow activity to a JSON Lines log.
    """

    log_file = Path(
        os.getenv(
            "LOG_FILE",
            "logs/supplysync.log"
        )
    )

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "workflow_id": workflow_id,
        "order_id": order_id,
        "decision": decision,
        "message": message,
    }

    with log_file.open(
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(entry) + "\n"
        )

    return (
        f"Log written successfully for "
        f"workflow {workflow_id}, "
        f"order {order_id}."
    )


def send_supply_email(
    workflow_id: str,
    order_id: str,
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """
    Demo email action.

    Currently logs the outgoing email.
    Replace this implementation with your real
    email service later.
    """

    email_file = Path("logs/outgoing_emails.log")

    email_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    email = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "workflow_id": workflow_id,
        "order_id": order_id,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }

    with email_file.open(
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(email) + "\n"
        )

    return (
        f"Email action completed for "
        f"{recipient}. "
        f"The email was recorded successfully."
    )
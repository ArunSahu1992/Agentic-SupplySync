"""
SupplySync SMTP Email Service Module.

This module manages the configuration and dispatching of outbound transactional email 
notifications using standard SMTP protocol over TLS via Python's `smtplib` and `EmailMessage`.
"""

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Read environment configuration key-value pairs from .env file
load_dotenv()


# ============================================================
# SMTP CONFIGURATION
# ============================================================

# Resolve target SMTP host server (defaults to Gmail SMTP)
SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com",
).strip()

# Resolve target SMTP server port (defaults to TLS port 587)
SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587",
    ).strip()
)

# Resolve authentication username for SMTP server
SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    "",
).strip()

# Resolve authentication password/app password for SMTP server
SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    "",
).strip()

# Fallback sender email address to SMTP username if explicitly missing
SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    SMTP_USERNAME,
).strip()


# ============================================================
# SEND EMAIL ROUTINE
# ============================================================

def send_email(
    recipient: str,
    subject: str,
    message: str,
) -> dict:
    """Construct and send a plain text email notification via SMTP with STARTTLS.

    Validates payload inputs and environment configuration, builds an `EmailMessage`, 
    establishes a TLS-encrypted SMTP connection, authenticates, and dispatches the payload.

    Args:
        recipient (str): Email address of the destination recipient.
        subject (str): Title or header line of the email.
        message (str): Plain-text body content of the email payload.

    Returns:
        dict: Execution status record structured as:
            {
                "email_status": "SENT" | "FAILED",
                "recipient": str,
                "subject": str,
                "error": str | None
            }
    """
    try:
        # Validate critical call inputs
        if not recipient:
            raise ValueError(
                "Email recipient is empty."
            )

        if not subject:
            raise ValueError(
                "Email subject is empty."
            )

        if not message:
            raise ValueError(
                "Email message is empty."
            )

        # Validate runtime SMTP credentials configuration
        if not SMTP_USERNAME:
            raise ValueError(
                "SMTP_USERNAME is not configured."
            )

        if not SMTP_PASSWORD:
            raise ValueError(
                "SMTP_PASSWORD is not configured."
            )

        # Build standardized RFC 5322 compliant message object
        email = EmailMessage()
        email["From"] = SMTP_FROM_EMAIL
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(
            message
        )

        # Open SMTP transport session with automated context closure
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
        ) as smtp:
            # Identify client to ESMTP server
            smtp.ehlo()

            # Upgrade connection encryption to TLS standard
            smtp.starttls()

            # Re-identify client over secure TLS channel
            smtp.ehlo()

            # Authenticate against SMTP host
            smtp.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            # Transmit email payload object
            smtp.send_message(
                email
            )

        return {
            "email_status": "SENT",
            "recipient": recipient,
            "subject": subject,
            "error": None,
        }

    except Exception as error:
        # Intercept and return descriptive runtime network or logic errors safely
        return {
            "email_status": "FAILED",
            "recipient": recipient,
            "subject": subject,
            "error": str(error),
        }
import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SMTP CONFIGURATION
# ============================================================

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com",
).strip()


SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587",
    ).strip()
)


SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    "",
).strip()


SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    "",
).strip()


SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    SMTP_USERNAME,
).strip()


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    recipient: str,
    subject: str,
    message: str,
) -> dict:

    try:

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

        if not SMTP_USERNAME:
            raise ValueError(
                "SMTP_USERNAME is not configured."
            )

        if not SMTP_PASSWORD:
            raise ValueError(
                "SMTP_PASSWORD is not configured."
            )

        email = EmailMessage()

        email["From"] = SMTP_FROM_EMAIL

        email["To"] = recipient

        email["Subject"] = subject

        email.set_content(
            message
        )


        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
        ) as smtp:

            smtp.ehlo()

            smtp.starttls()

            smtp.ehlo()

            smtp.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

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

        return {

            "email_status": "FAILED",

            "recipient": recipient,

            "subject": subject,

            "error": str(error),
        }
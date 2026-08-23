import os
import smtplib
import socket
import sys

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
    "smtp.gmail.com"
).strip()

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    ).strip()
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    ""
).strip()

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
).strip()


# ============================================================
# DEBUG INFORMATION
# ============================================================

print("\n========== SMTP DEBUG ==========")

print(
    "Python executable:",
    sys.executable
)

print(
    "Current directory:",
    os.getcwd()
)

print(
    "SMTP_HOST:",
    repr(SMTP_HOST)
)

print(
    "SMTP_PORT:",
    SMTP_PORT
)

print(
    "SMTP_USERNAME:",
    repr(SMTP_USERNAME)
)

print("================================\n")


# ============================================================
# TEST DNS
# ============================================================

try:

    print("Testing DNS...")

    resolved_ip = socket.gethostbyname(
        SMTP_HOST
    )

    print(
        f"DNS SUCCESS: "
        f"{SMTP_HOST} -> {resolved_ip}"
    )

except Exception as error:

    print("\nDNS FAILED:")

    print(
        type(error).__name__
    )

    print(
        error
    )

    raise


# ============================================================
# TEST SMTP CONNECTION + LOGIN
# ============================================================

try:

    print("\nTesting SMTP connection...")

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30,
    ) as smtp:

        smtp.set_debuglevel(1)

        print(
            "Connected successfully"
        )

        smtp.ehlo()

        smtp.starttls()

        smtp.ehlo()

        print(
            "Trying login..."
        )

        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        print(
            "\nLOGIN SUCCESS!"
        )


except Exception as error:

    print(
        "\nSMTP FAILED:"
    )

    print(
        type(error).__name__
    )

    print(
        error
    )
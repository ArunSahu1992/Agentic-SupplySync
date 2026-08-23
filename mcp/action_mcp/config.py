import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    ACTION_MCP_HOST = os.getenv(
        "ACTION_MCP_HOST",
        "0.0.0.0",
    )

    ACTION_MCP_PORT = int(
        os.getenv(
            "ACTION_MCP_PORT",
            "9001",
        )
    )

    AUDIT_LOG_FILE = os.getenv(
        "AUDIT_LOG_FILE",
        "data/audit_logs.json",
    )

    NOTIFICATION_MODE = os.getenv(
        "NOTIFICATION_MODE",
        "SIMULATION",
    )

    SMTP_HOST = os.getenv(
        "SMTP_HOST",
        "",
    )

    SMTP_PORT = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    SMTP_USERNAME = os.getenv(
        "SMTP_USERNAME",
        "",
    )

    SMTP_PASSWORD = os.getenv(
        "SMTP_PASSWORD",
        "",
    )

    SMTP_FROM = os.getenv(
        "SMTP_FROM",
        "",
    )


settings = Settings()
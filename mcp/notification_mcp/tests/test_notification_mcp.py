"""
SupplySync Notification MCP Integration Test Suite.

This module provides asynchronous test client execution against a running SupplySync 
Notification MCP Server using `mcp.ClientSession` over Streamable HTTP transport.
"""

import asyncio

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


# ============================================================
# MCP URL CONFIGURATION
# ============================================================

# Target HTTP endpoint address for the running FastMCP Notification server
MCP_URL = (
    "http://127.0.0.1:9002/mcp"
)


async def main() -> None:
    """Execute asynchronous end-to-end integration tests for the Notification MCP server.

    Establishes an HTTP transport stream, initializes an MCP client session, lists 
    available registered tools, and tests dispatch execution across EMAIL, SMS, and 
    dual-channel (BOTH) notification modes.
    """
    # Open streaming HTTP transport client context manager to target endpoint
    async with streamable_http_client(
        MCP_URL
    ) as (
        read,
        write,
        _,
    ):
        # Create client session over the read/write streaming channels
        async with ClientSession(
            read,
            write,
        ) as session:

            # ====================================================
            # INITIALIZE MCP SESSION
            # ====================================================

            # Perform initial MCP protocol handshake and capabilities negotiation
            await session.initialize()

            # ====================================================
            # VERIFY AVAILABLE TOOLS
            # ====================================================

            print(
                "\n========== AVAILABLE TOOLS ==========\n"
            )

            # Retrieve list of remote tools exposed by the MCP server instance
            tools = await session.list_tools()

            for tool in tools.tools:
                print(
                    f"- {tool.name}"
                )

            # ====================================================
            # TEST CASE 1: EMAIL ONLY NOTIFICATION MODE
            # ====================================================

            print(
                "\n========== TEST EMAIL ONLY ==========\n"
            )

            # Invoke remote process_notification tool configured exclusively for EMAIL channel
            email_result = await session.call_tool(
                "process_notification",
                arguments={
                    "notification_mode": "EMAIL",
                    "workflow_id": "WF-TEST-EMAIL-1001",
                    "order_id": "ORD-TEST-EMAIL-1001",
                    "recipient":
                        "arunsahungp@gmail.com",
                    "subject":
                        "SupplySync Test Email",
                    "message": """
Hello,

This is a test email from the
SupplySync Notification MCP.

The EMAIL mode is working successfully.

Thank you,
SupplySync
""",
                },
            )

            # Print raw MCP tool response payload
            print(
                email_result
            )

            # ====================================================
            # TEST CASE 2: SMS ONLY NOTIFICATION MODE
            # ====================================================

            print(
                "\n========== TEST SMS ONLY ==========\n"
            )

            # Invoke remote process_notification tool configured exclusively for SMS channel
            sms_result = await session.call_tool(
                "process_notification",
                arguments={
                    "notification_mode": "SMS",
                    "workflow_id": "WF-TEST-SMS-1001",
                    "order_id": "ORD-TEST-SMS-1001",
                    "mobile_number":
                        "+918983331829",
                    "message": (
                        "Hello, this is a test SMS from "
                        "the SupplySync Notification MCP. "
                        "The SMS mode is working successfully."
                    ),
                },
            )

            # Print raw MCP tool response payload
            print(
                sms_result
            )

            # ====================================================
            # TEST CASE 3: DUAL-CHANNEL (EMAIL AND SMS) MODE
            # ====================================================

            print(
                "\n========== TEST EMAIL AND SMS ==========\n"
            )

            # Invoke remote process_notification tool configured for BOTH EMAIL and SMS channels
            both_result = await session.call_tool(
                "process_notification",
                arguments={
                    "notification_mode": "BOTH",
                    "workflow_id": "WF-TEST-BOTH-1001",
                    "order_id": "ORD-TEST-BOTH-1001",

                    # --------------------------------------------
                    # EMAIL CHANNEL CONFIGURATION
                    # --------------------------------------------

                    "recipient":
                        "arunsahungp@gmail.com",
                    "subject":
                        "SupplySync Test Email and SMS",

                    # --------------------------------------------
                    # SMS CHANNEL CONFIGURATION
                    # --------------------------------------------

                    "mobile_number":
                        "+919876543210",

                    # --------------------------------------------
                    # PAYLOAD MESSAGE BODY (DISPATCHED TO BOTH CHANNELS)
                    # --------------------------------------------

                    "message": """
Hello,

This is a test of the SupplySync
Notification MCP.

Both EMAIL and SMS are being tested.

Thank you,
SupplySync
""",
                },
            )

            # Print raw MCP tool response payload
            print(
                both_result
            )


# Execute main async event loop entry point
if __name__ == "__main__":
    asyncio.run(
        main()
    )
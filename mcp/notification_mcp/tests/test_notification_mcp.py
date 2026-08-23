import asyncio

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


MCP_URL = (
    "http://127.0.0.1:9002/mcp"
)


async def main():

    async with streamable_http_client(
        MCP_URL
    ) as (

        read,

        write,

        _,

    ):

        async with ClientSession(

            read,

            write,

        ) as session:


            # ====================================================
            # INITIALIZE MCP
            # ====================================================

            await session.initialize()


            # ====================================================
            # AVAILABLE TOOLS
            # ====================================================

            print(
                "\n========== AVAILABLE TOOLS ==========\n"
            )


            tools = await session.list_tools()


            for tool in tools.tools:

                print(
                    f"- {tool.name}"
                )


            # ====================================================
            # TEST EMAIL ONLY
            # ====================================================

            print(
                "\n========== TEST EMAIL ONLY ==========\n"
            )


            email_result = await session.call_tool(

                "process_notification",

                arguments={

                    "notification_mode": "EMAIL",

                    "workflow_id": "WF-TEST-EMAIL-1001",

                    "order_id": "ORD-TEST-EMAIL-1001",

                    "workflow_decision": "APPROVED",

                    "recommended_action":
                        "reschedule_order",

                    "final_status": "COMPLETED",

                    "action_execution": {

                        "action_status": "SUCCESS",

                        "executed_action":
                            "reschedule_order",

                        "execution_details": {},
                    },

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


            print(
                email_result
            )


            # ====================================================
            # TEST AUDIT LOG ONLY
            # ====================================================

            print(
                "\n========== TEST AUDIT LOG ONLY ==========\n"
            )


            audit_result = await session.call_tool(

                "process_notification",

                arguments={

                    "notification_mode": "LOG",

                    "workflow_id": "WF-TEST-LOG-1001",

                    "order_id": "ORD-TEST-LOG-1001",

                    "workflow_decision": "APPROVED",

                    "recommended_action":
                        "reschedule_order",

                    "final_status": "COMPLETED",

                    "action_execution": {

                        "action_status": "SUCCESS",

                        "executed_action":
                            "reschedule_order",

                        "execution_details": {

                            "reschedule_days": 5,

                            "additional_discount_percent": 5.0,
                        },
                    },
                },
            )


            print(
                audit_result
            )


            # ====================================================
            # TEST EMAIL AND AUDIT LOG
            # ====================================================

            print(
                "\n========== TEST EMAIL AND LOG ==========\n"
            )


            both_result = await session.call_tool(

                "process_notification",

                arguments={

                    "notification_mode": "BOTH",

                    "workflow_id": "WF-TEST-BOTH-1001",

                    "order_id": "ORD-TEST-BOTH-1001",

                    "workflow_decision": "APPROVED",

                    "recommended_action":
                        "reschedule_order",

                    "final_status": "COMPLETED",

                    "action_execution": {

                        "action_status": "SUCCESS",

                        "executed_action":
                            "reschedule_order",

                        "execution_details": {

                            "reschedule_days": 5,

                            "additional_discount_percent": 5.0,

                            "discount_amount": 1250.0,

                            "revised_final_amount": 23750.0,
                        },
                    },

                    "recipient":
                        "arunsahungp@gmail.com",

                    "subject":
                        "SupplySync Test Email and Audit",

                    "message": """
Hello,

This is a test of the SupplySync
Notification MCP.

Both EMAIL and LOG processing
are being tested.

Thank you,
SupplySync
""",
                },
            )


            print(
                both_result
            )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
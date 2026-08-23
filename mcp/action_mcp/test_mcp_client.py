import asyncio

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


MCP_SERVER_URL = (
    "http://127.0.0.1:9001/mcp"
)


async def main():

    print("\n============================================")
    print("SUPPLYSYNC ACTION MCP CLIENT TEST")
    print("============================================")


    async with streamable_http_client(
        MCP_SERVER_URL
    ) as (
        read_stream,
        write_stream,
        _,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # Initialize session

            await session.initialize()

            print(
                "\nConnected to MCP Server successfully."
            )


            # List tools

            tools = await session.list_tools()

            print("\nAvailable MCP Tools:")

            for tool in tools.tools:

                print(
                    f" - {tool.name}"
                )


            # =================================================
            # TEST RESCHEDULE ORDER
            # =================================================

            print(
                "\n============================================"
            )

            print(
                "TEST: RESCHEDULE ORDER BY 3 DAYS"
            )

            print(
                "============================================"
            )


            result = await session.call_tool(
                "execute_supply_action",

                arguments={

                    "workflow_id":
                        "WF-TEST-001",

                    "order_id":
                        "ORD-TEST-1001",

                    "product":
                        "Critical Vaccine",

                    "supplier":
                        "ABC Pharma",

                    "recommended_action":
                        "reschedule_order",

                    "reason": (
                        "Supplier delay detected. "
                        "Order must be rescheduled "
                        "by 3 days."
                    ),

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        1000,

                    "total_order_amount":
                        10000.00,
                },
            )


            print(
                "\nMCP RESPONSE:"
            )

            print(
                "============================================"
            )


            for content in result.content:

                if hasattr(
                    content,
                    "text",
                ):

                    print(
                        content.text
                    )


            print(
                "============================================"
            )

            print(
                "TEST COMPLETED"
            )

            print(
                "============================================\n"
            )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
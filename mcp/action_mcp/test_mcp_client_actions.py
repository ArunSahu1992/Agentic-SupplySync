"""
Model Context Protocol (MCP) Action Server Integration Test Suite.

This script executes integration tests against the SupplySync Action MCP Server 
using HTTP streaming. It evaluates three supply chain remediation workflows:
1. Reschedule Order (with policy-driven discount)
2. Partial Order Fulfillment (with revised billing)
3. Order Cancellation (with full refund initiation)
"""

import asyncio
import json

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


# ============================================================
# MCP SERVER URL
# ============================================================

# Target endpoint for the local MCP Streamable HTTP service
MCP_SERVER_URL = (
    "http://127.0.0.1:9001/mcp"
)


# ============================================================
# HELPER
# ============================================================

def print_result(
    title: str,
    result,
):
    """Format and display tool call results.

    Parses JSON content returned by the MCP tool if available; falls back to raw 
    text rendering when JSON parsing fails or content is empty.

    Args:
        title (str): Header section label.
        result (CallToolResult): The response object returned from the MCP session.
    """

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    # Check for empty or non-existent response content
    if not result.content:

        print("No result returned.")

        return

    # Iterate through content payload blocks
    for content in result.content:

        if hasattr(
            content,
            "text",
        ):

            try:

                # Attempt to parse response text as JSON for pretty printing
                data = json.loads(
                    content.text
                )

                print(
                    json.dumps(
                        data,
                        indent=2,
                    )
                )

            except json.JSONDecodeError:

                # Print unformatted string if content is not valid JSON
                print(
                    content.text
                )

    print("=" * 70)


# ============================================================
# EXECUTE ACTION TEST
# ============================================================

async def execute_action_test(
    session,
    title: str,
    arguments: dict,
):
    """Asynchronously execute a specific tool action call over the MCP session.

    Args:
        session (ClientSession): Active Model Context Protocol client session.
        title (str): Display title for the test run.
        arguments (dict): Payload passed directly to the `execute_supply_action` tool.

    Returns:
        CallToolResult | None: Result object returned from MCP server, or None on failure.
    """

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    print("\nINPUT:")

    # Print input argument payload for test traceability
    print(
        json.dumps(
            arguments,
            indent=2,
        )
    )

    try:

        # Dispatch tool call to MCP server
        result = await session.call_tool(

            "execute_supply_action",

            arguments=arguments,
        )

        # Output parsed response
        print_result(

            f"{title} RESULT",

            result,
        )

        return result

    except Exception as error:

        # Catch transport, tool, or runtime errors during execution
        print(
            "\nACTION TEST FAILED"
        )

        print(
            f"Error: {error}"
        )

        return None


# ============================================================
# MAIN
# ============================================================

async def main():
    """Establish HTTP stream connection, initialize session, and execute end-to-end MCP action tests."""

    print("\n")
    print("=" * 70)
    print(
        "SUPPLYSYNC ACTION MCP SERVER TEST"
    )
    print("=" * 70)

    print(

        f"\nConnecting to MCP Server:\n"
        f"{MCP_SERVER_URL}"
    )


    # ========================================================
    # CONNECT TO STREAMABLE HTTP MCP SERVER
    # ========================================================

    # Establish HTTP streaming transport layer
    async with streamable_http_client(
        MCP_SERVER_URL
    ) as (

        read_stream,

        write_stream,

        _,

    ):

        # Bind transport streams to client session manager
        async with ClientSession(

            read_stream,

            write_stream,

        ) as session:


            # =================================================
            # INITIALIZE MCP SESSION
            # =================================================

            # Perform standard MCP protocol handshake and capability exchange
            await session.initialize()

            print(
                "\nConnected to MCP Server successfully."
            )


            # =================================================
            # LIST AVAILABLE TOOLS
            # =================================================

            # Fetch and print advertised capabilities from the server
            tools = await session.list_tools()

            print(
                "\nAvailable MCP Tools:"
            )

            for tool in tools.tools:

                print(
                    f" - {tool.name}"
                )


            # =================================================
            # TEST 1
            # RESCHEDULE ORDER
            #
            # POLICY RESULT:
            #
            # reschedule_days = 5
            # discount = 5%
            #
            # ORIGINAL DATE:
            # 2026-08-25
            #
            # EXPECTED REVISED DATE:
            # 2026-08-30
            #
            # ORDER AMOUNT:
            # 50000
            #
            # DISCOUNT:
            # 2500
            #
            # FINAL AMOUNT:
            # 47500
            # =================================================

            # Execute Test 1: Order rescheduling scenario with calculated date extension and discount
            await execute_action_test(

                session=session,

                title=(
                    "TEST 1: RESCHEDULE ORDER "
                    "+ 5 PERCENT DISCOUNT"
                ),

                arguments={

                    # ------------------------------------------
                    # WORKFLOW
                    # ------------------------------------------

                    "workflow_id":
                        "WF-RESCHEDULE-1001",

                    "order_id":
                        "ORD-RESCHEDULE-1001",


                    # ------------------------------------------
                    # ORDER
                    # ------------------------------------------

                    "product":
                        "Paracetamol 500mg",

                    "supplier":
                        "ACME Pharma",


                    # ------------------------------------------
                    # ACTION FROM POLICY MCP
                    # ------------------------------------------

                    "recommended_action":
                        "reschedule_order",

                    "reason": (
                        "Shipment delay requires a 5 day "
                        "reschedule. Policy applies a 5 percent "
                        "discount because the delay is greater "
                        "than 1 day."
                    ),


                    # ------------------------------------------
                    # QUANTITY
                    # ------------------------------------------

                    "ordered_qty":
                        10000,

                    "affected_qty":
                        0,


                    # ------------------------------------------
                    # FINANCIAL
                    # ------------------------------------------

                    "total_order_amount":
                        50000.00,


                    # From Policy MCP
                    "additional_discount_percent":
                        5.0,


                    # ------------------------------------------
                    # REQUESTER
                    # ------------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ------------------------------------------
                    # ORIGINAL DELIVERY DATE
                    # ------------------------------------------

                    "estimated_delivery_date":
                        "2026-08-25",


                    # ------------------------------------------
                    # POLICY DECISION
                    # ------------------------------------------

                    "reschedule_days":
                        5,
                },
            )


            # =================================================
            # TEST 2
            # PARTIAL ORDER + REVISED PAYMENT
            #
            # ORDERED:
            # 4000
            #
            # AFFECTED:
            # 1000
            #
            # FULFILLABLE:
            # 3000
            #
            # ORIGINAL PARTIAL AMOUNT:
            # 10000 * 3000 / 4000
            # = 7500
            #
            # DISCOUNT:
            # 2%
            #
            # DISCOUNT AMOUNT:
            # 150
            #
            # FINAL AMOUNT:
            # 7350
            # =================================================

            # Execute Test 2: Partial fulfillment with adjusted payment calculations
            await execute_action_test(

                session=session,

                title=(
                    "TEST 2: PARTIAL ORDER "
                    "+ REVISED PAYMENT"
                ),

                arguments={

                    # ------------------------------------------
                    # WORKFLOW
                    # ------------------------------------------

                    "workflow_id":
                        "WF-PARTIAL-1001",

                    "order_id":
                        "ORD-PARTIAL-1001",


                    # ------------------------------------------
                    # ORDER
                    # ------------------------------------------

                    "product":
                        "Critical Vaccine",

                    "supplier":
                        "ABC Pharma",


                    # ------------------------------------------
                    # ACTION FROM POLICY MCP
                    # ------------------------------------------

                    "recommended_action":
                        "partial_order_revised_payment",

                    "reason": (
                        "Supplier can fulfill 75 percent "
                        "of the committed quantity. "
                        "Apply the policy-approved "
                        "2 percent discount."
                    ),


                    # ------------------------------------------
                    # QUANTITY
                    # ------------------------------------------

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        1000,


                    # ------------------------------------------
                    # FINANCIAL
                    # ------------------------------------------

                    "total_order_amount":
                        10000.00,


                    # From Policy MCP
                    "additional_discount_percent":
                        2.0,


                    # ------------------------------------------
                    # REQUESTER
                    # ------------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ------------------------------------------
                    # NOT REQUIRED
                    # ------------------------------------------

                    "estimated_delivery_date":
                        None,

                    "reschedule_days":
                        0,
                },
            )


            # =================================================
            # TEST 3
            # CANCEL ORDER + REFUND
            #
            # ORDERED:
            # 4000
            #
            # AFFECTED:
            # 4000
            #
            # REFUND:
            # 10000
            # =================================================

            # Execute Test 3: Order cancellation workflow and refund triggering
            await execute_action_test(

                session=session,

                title=(
                    "TEST 3: CANCEL ORDER "
                    "+ INITIATE REFUND"
                ),

                arguments={

                    # ------------------------------------------
                    # WORKFLOW
                    # ------------------------------------------

                    "workflow_id":
                        "WF-CANCEL-1001",

                    "order_id":
                        "ORD-CANCEL-1001",


                    # ------------------------------------------
                    # ORDER
                    # ------------------------------------------

                    "product":
                        "Critical Medicine",

                    "supplier":
                        "ABC Pharma",


                    # ------------------------------------------
                    # ACTION FROM POLICY MCP
                    # ------------------------------------------

                    "recommended_action":
                        "cancel_order_refund",

                    "reason": (
                        "Supplier is unable to fulfill "
                        "the critical order. "
                        "Policy requires cancellation "
                        "and full refund."
                    ),


                    # ------------------------------------------
                    # QUANTITY
                    # ------------------------------------------

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        4000,


                    # ------------------------------------------
                    # FINANCIAL
                    # ------------------------------------------

                    "total_order_amount":
                        10000.00,

                    "additional_discount_percent":
                        0.0,


                    # ------------------------------------------
                    # REQUESTER
                    # ------------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ------------------------------------------
                    # NOT REQUIRED
                    # ------------------------------------------

                    "estimated_delivery_date":
                        None,

                    "reschedule_days":
                        0,
                },
            )


            # =================================================
            # EXPECTED RESULTS
            # =================================================

            # Print benchmark outputs for visual verification against actual returns
            print("\n")
            print("=" * 70)
            print("EXPECTED RESULTS")
            print("=" * 70)


            # =================================================
            # EXPECTED TEST 1
            # =================================================

            print(
                "\n1. RESCHEDULE + DISCOUNT"
            )

            print(
                json.dumps(
                    {

                        "action_status":
                            "SUCCESS",

                        "executed_action":
                            "reschedule_order",

                        "execution_details": {

                            "order_id":
                                "ORD-RESCHEDULE-1001",

                            "estimated_delivery_date":
                                "2026-08-25",

                            "additional_days":
                                5,

                            "revised_delivery_date":
                                "2026-08-30",

                            "total_order_amount":
                                50000.0,

                            "additional_discount_percent":
                                5.0,

                            "discount_amount":
                                2500.0,

                            "revised_final_amount":
                                47500.0,
                        },
                    },

                    indent=2,
                )
            )


            # =================================================
            # EXPECTED TEST 2
            # =================================================

            print(
                "\n2. PARTIAL ORDER"
            )

            print(
                json.dumps(
                    {

                        "action_status":
                            "SUCCESS",

                        "executed_action":
                            "partial_order_revised_payment",

                        "execution_details": {

                            "ordered_qty":
                                4000,

                            "affected_qty":
                                1000,

                            "fulfillable_qty":
                                3000,

                            "fulfillment_percentage":
                                75.0,

                            "original_partial_amount":
                                7500.0,

                            "additional_discount_percent":
                                2.0,

                            "discount_amount":
                                150.0,

                            "revised_final_amount":
                                7350.0,
                        },
                    },

                    indent=2,
                )
            )


            # =================================================
            # EXPECTED TEST 3
            # =================================================

            print(
                "\n3. CANCEL + REFUND"
            )

            print(
                json.dumps(
                    {

                        "action_status":
                            "SUCCESS",

                        "executed_action":
                            "cancel_order_refund",

                        "execution_details": {

                            "order_status":
                                "CANCELLED",

                            "refund_status":
                                "INITIATED",

                            "refund_amount":
                                10000.0,
                        },
                    },

                    indent=2,
                )
            )


            # =================================================
            # COMPLETED
            # =================================================

            print("\n")
            print("=" * 70)

            print(
                "ALL ACTION MCP TESTS COMPLETED"
            )

            print("=" * 70)

            print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    # Run the main asynchronous entry point using the event loop
    asyncio.run(
        main()
    )
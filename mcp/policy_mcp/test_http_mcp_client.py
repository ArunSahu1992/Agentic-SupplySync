import asyncio
import json

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


# ============================================================
# POLICY MCP URL
# ============================================================

# Endpoint for the local SupplySync Policy Engine MCP Server running over HTTP SSE
MCP_URL = (
    "http://127.0.0.1:9000/mcp"
)


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(
    title,
    result,
):
    """
    Utility function to format and display tool execution responses from the MCP Server.
    Parses JSON text responses if available; otherwise falls back to plain text printing.
    """

    print("\n")

    print("=" * 70)

    print(title)

    print("=" * 70)

    for item in result.content:

        if hasattr(
            item,
            "text",
        ):

            try:

                # Attempt to parse and pretty-print raw string content as JSON
                data = json.loads(
                    item.text
                )

                print(
                    json.dumps(
                        data,
                        indent=2,
                    )
                )

            except json.JSONDecodeError:

                # Print raw text directly if the content is not JSON-formatted
                print(
                    item.text
                )

    print("=" * 70)


# ============================================================
# CALL POLICY TOOL
# ============================================================

async def evaluate_test(
    session,
    title,
    arguments,
):
    """
    Asynchronously invokes the 'evaluate_supply_decision' tool on the MCP server 
    and handles input/output logging for validation.
    
    :param session: Active MCP ClientSession instance
    :param title: Descriptive test identifier for logging
    :param arguments: Dictionary of payload parameters passed to the policy tool
    :return: CallToolResult object containing the evaluation outcome
    """

    print("\n\n")

    print("=" * 70)

    print(title)

    print("=" * 70)

    print("\nINPUT:")

    print(
        json.dumps(
            arguments,
            indent=2,
        )
    )

    # Executing the target MCP tool on the server
    result = await session.call_tool(

        "evaluate_supply_decision",

        arguments=arguments,
    )

    # Display the structured response output
    print_result(

        f"{title} RESULT",

        result,
    )

    return result


# ============================================================
# MAIN
# ============================================================

async def main():
    """
    Main entry point for running the test suite across multiple supply disruption scenarios.
    Establishes the HTTP stream transport and initializes the ClientSession.
    """

    print("\n")

    print("=" * 70)

    print(
        "SUPPLYSYNC POLICY MCP CLIENT TEST"
    )

    print("=" * 70)


    # ========================================================
    # CONNECT TO POLICY MCP SERVER
    # ========================================================

    print(
        "\nConnecting to Policy MCP Server..."
    )


    # Context manager managing transport-layer connection (Streamable HTTP)
    async with streamable_http_client(
        MCP_URL
    ) as (

        read_stream,

        write_stream,

        _,

    ):


        # Context manager handling protocol-level interaction and handshakes
        async with ClientSession(

            read_stream,

            write_stream,

        ) as session:


            # =================================================
            # INITIALIZE
            # =================================================

            # Perform the MCP protocol initialization handshake
            await session.initialize()

            print(
                "Connected successfully!"
            )


            # =================================================
            # LIST TOOLS
            # =================================================

            # Fetch and display available tools exposed by the server for verification
            print(
                "\nAvailable tools:"
            )

            tools = (
                await session.list_tools()
            )

            for tool in tools.tools:

                print(
                    f"- {tool.name}"
                )


            # =================================================
            # TEST 1
            #
            # PARTIAL ORDER RECOVERY
            #
            # ORDERED = 4000
            # AFFECTED = 1000
            #
            # FULFILLABLE = 3000
            # FULFILLMENT = 75%
            #
            # EXPECTED:
            #
            # recommended_action =
            # partial_order_revised_payment
            #
            # additional_discount_percent = 2
            #
            # requires_approval = true
            # =================================================

            # Executing Test Case 1: Partial Fulfillment (75% recoverable)
            await evaluate_test(

                session=session,

                title=(
                    "TEST 1: PARTIAL ORDER RECOVERY"
                ),

                arguments={

                    # ----------------------------------------
                    # ORDER
                    # ----------------------------------------

                    "order_id":
                        "ORD-PARTIAL-1001",

                    "product":
                        "Critical Medicine",

                    "supplier":
                        "ABC Pharma",


                    # ----------------------------------------
                    # QUANTITY
                    # ----------------------------------------

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        1000,


                    # ----------------------------------------
                    # DISRUPTION
                    # ----------------------------------------

                    "disruption_type":
                        "partial_fulfillment",

                    "requested_action":
                        "auto_recommend",


                    # ----------------------------------------
                    # FINANCIAL
                    # ----------------------------------------

                    "total_order_amount":
                        10000,


                    # ----------------------------------------
                    # REQUESTER
                    # ----------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ----------------------------------------
                    # DELIVERY
                    # ----------------------------------------

                    "estimated_delivery_date":
                        "2026-08-30",
                },
            )


            # =================================================
            # TEST 2
            #
            # CANCEL ORDER + REFUND
            #
            # ORDERED = 4000
            # AFFECTED = 4000
            #
            # FULFILLABLE = 0
            #
            # EXPECTED:
            #
            # recommended_action =
            # cancel_order_refund
            #
            # additional_discount_percent = 0
            #
            # approval depends on your cancellation policy
            # =================================================

            # Executing Test Case 2: Complete Fulfillment Failure (0% recoverable)
            await evaluate_test(

                session=session,

                title=(
                    "TEST 2: CANCEL ORDER + REFUND"
                ),

                arguments={

                    # ----------------------------------------
                    # ORDER
                    # ----------------------------------------

                    "order_id":
                        "ORD-CANCEL-1001",

                    "product":
                        "Critical Medicine",

                    "supplier":
                        "ABC Pharma",


                    # ----------------------------------------
                    # QUANTITY
                    # ----------------------------------------

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        4000,


                    # ----------------------------------------
                    # DISRUPTION
                    # ----------------------------------------

                    "disruption_type":
                        "supplier_unable_to_fulfill",

                    "requested_action":
                        "auto_recommend",


                    # ----------------------------------------
                    # FINANCIAL
                    # ----------------------------------------

                    "total_order_amount":
                        10000,


                    # ----------------------------------------
                    # REQUESTER
                    # ----------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ----------------------------------------
                    # DELIVERY
                    # ----------------------------------------

                    "estimated_delivery_date":
                        "2026-08-30",
                },
            )


            # =================================================
            # TEST 3
            #
            # SHIPMENT DELAY / RESCHEDULE
            #
            # POLICY EXPECTED:
            #
            # recommended_action =
            # reschedule_order
            #
            # reschedule_days =
            # 5
            #
            # Because 5 > 1:
            #
            # additional_discount_percent =
            # 5
            #
            # Because 5 > 3:
            #
            # requires_approval =
            # true
            # =================================================

            # Executing Test Case 3: Shipment Delay & Extended Schedule Impact
            await evaluate_test(

                session=session,

                title=(
                    "TEST 3: SHIPMENT DELAY / RESCHEDULE"
                ),

                arguments={

                    # ----------------------------------------
                    # ORDER
                    # ----------------------------------------

                    "order_id":
                        "ORD-RESCHEDULE-1001",

                    "product":
                        "Critical Medicine",

                    "supplier":
                        "ABC Pharma",


                    # ----------------------------------------
                    # QUANTITY
                    # ----------------------------------------

                    "ordered_qty":
                        4000,

                    "affected_qty":
                        0,


                    # ----------------------------------------
                    # DISRUPTION
                    # ----------------------------------------

                    "disruption_type":
                        "shipment_delay",

                    "requested_action":
                        "auto_recommend",


                    # ----------------------------------------
                    # FINANCIAL
                    # ----------------------------------------

                    "total_order_amount":
                        50000,


                    # ----------------------------------------
                    # REQUESTER
                    # ----------------------------------------

                    "requester_name":
                        "Abhi",

                    "requester_email":
                        "anc@gmail.com",


                    # ----------------------------------------
                    # CURRENT DELIVERY DATE
                    #
                    # Action MCP will calculate:
                    #
                    # 2026-08-25 + 5 days
                    #
                    # = 2026-08-30
                    # ----------------------------------------

                    "estimated_delivery_date":
                        "2026-08-25",
                },
            )


            # =================================================
            # EXPECTED SUMMARY
            # =================================================

            # Output baseline assertion benchmarks for verification against MCP tool output
            print("\n\n")

            print("=" * 70)

            print(
                "EXPECTED POLICY RESULTS"
            )

            print("=" * 70)


            expected_results = {

                "TEST 1 - PARTIAL ORDER": {

                    "recommended_action":
                        "partial_order_revised_payment",

                    "additional_discount_percent":
                        2,

                    "requires_approval":
                        True,
                },


                "TEST 2 - CANCEL ORDER": {

                    "recommended_action":
                        "cancel_order_refund",

                    "additional_discount_percent":
                        0,
                },


                "TEST 3 - SHIPMENT DELAY": {

                    "recommended_action":
                        "reschedule_order",

                    "reschedule_days":
                        5,

                    "additional_discount_percent":
                        5,

                    "requires_approval":
                        True,

                    "estimated_delivery_date":
                        "2026-08-25",

                    "expected_revised_delivery_date":
                        "2026-08-30",
                },
            }


            print(

                json.dumps(

                    expected_results,

                    indent=2,

                )

            )


            # =================================================
            # COMPLETED
            # =================================================

            print("\n")

            print("=" * 70)

            print(
                "ALL POLICY MCP TESTS COMPLETED"
            )

            print("=" * 70)

            print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    # Run the main asynchronous execution loop
    asyncio.run(
        main()
    )
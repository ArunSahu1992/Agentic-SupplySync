import asyncio
import json

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


# ============================================================
# POLICY MCP URL
# ============================================================

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

    result = await session.call_tool(

        "evaluate_supply_decision",

        arguments=arguments,
    )

    print_result(

        f"{title} RESULT",

        result,
    )

    return result


# ============================================================
# MAIN
# ============================================================

async def main():

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


    async with streamable_http_client(
        MCP_URL
    ) as (

        read_stream,

        write_stream,

        _,

    ):


        async with ClientSession(

            read_stream,

            write_stream,

        ) as session:


            # =================================================
            # INITIALIZE
            # =================================================

            await session.initialize()

            print(
                "Connected successfully!"
            )


            # =================================================
            # LIST TOOLS
            # =================================================

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

    asyncio.run(
        main()
    )
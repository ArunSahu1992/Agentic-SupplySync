import asyncio
import json

from mcp import ClientSession

from mcp.client.streamable_http import (
    streamable_http_client,
)


# ============================================================
# MCP SERVER URL
# ============================================================

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

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    if not result.content:

        print("No result returned.")

        return

    for content in result.content:

        if hasattr(
            content,
            "text",
        ):

            try:

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

    print("\n")
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

    try:

        result = await session.call_tool(

            "execute_supply_action",

            arguments=arguments,
        )

        print_result(

            f"{title} RESULT",

            result,
        )

        return result

    except Exception as error:

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


            # =================================================
            # INITIALIZE MCP SESSION
            # =================================================

            await session.initialize()

            print(
                "\nConnected to MCP Server successfully."
            )


            # =================================================
            # LIST AVAILABLE TOOLS
            # =================================================

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

    asyncio.run(
        main()
    )
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    # ========================================================
    # TEST 1
    # RESCHEDULE ORDER
    # ========================================================

    {
        "name": "Reschedule order by 3 days - No approval",

        "expected_action": "reschedule_order",

        "expected_approval": False,

        "input": {
             "workflow_id": "WF-RESCHEDULE-1001",
  "order_id": "ORD-RESCHEDULE-1001",
  "product": "Critical Medicine",
  "supplier": "ABC Pharma",
  "ordered_qty": 4000,
  "affected_qty": 0,
  "disruption_events": [
    "shipment_delay"
  ],
  "estimated_duration_days": 5,
  "impact_value_usd": 50000,
  "requester_name": "Abhi",
  "requester_email": "anc@gmail.com"
        },
    },


    # ========================================================
    # TEST 2
    # PARTIAL ORDER - 75% FULFILLMENT
    # APPROVAL REQUIRED
    # ========================================================

    {
        "name": "Partial order - 75 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_approval": True,

        "input": {
            "order_id": "SO-1002",
            "product": "Paracetamol 500mg",
            "supplier": "BioSource",
            "ordered_qty": 10000,

            # 7,500 fulfillable
            # 2,500 affected
            # 75% fulfillment
            "affected_qty": 2500,

            "disruption_type": "supplier_partial_fulfillment",
            "requested_action": "auto_recommend",
            "impact_value_usd": 45000,
            "delay_days": 0,
            "customer_critical": False,
            "patient_critical": False,
        },
    },


    # ========================================================
    # TEST 3
    # PARTIAL ORDER - 90% FULFILLMENT
    # NO APPROVAL
    # ========================================================

    {
        "name": "Partial order - 90 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_approval": False,

        "input": {
            "order_id": "SO-1003",
            "product": "Paracetamol 500mg",
            "supplier": "ACME Pharma",
            "ordered_qty": 10000,

            # 9,000 fulfillable
            # 1,000 affected
            # 90% fulfillment
            "affected_qty": 1000,

            "disruption_type": "supplier_partial_fulfillment",
            "requested_action": "auto_recommend",
            "impact_value_usd": 10000,
            "delay_days": 0,
            "customer_critical": False,
            "patient_critical": False,
        },
    },


    # ========================================================
    # TEST 4
    # PARTIAL ORDER - BELOW 50%
    # APPROVAL REQUIRED
    # ========================================================

    {
        "name": "Partial order - 25 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_approval": True,

        "input": {
            "order_id": "SO-1004",
            "product": "Medicine-A",
            "supplier": "ABC Pharma",
            "ordered_qty": 4000,

            # 1,000 fulfillable
            # 3,000 affected
            # 25% fulfillment
            "affected_qty": 3000,

            "disruption_type": "supplier_partial_fulfillment",
            "requested_action": "auto_recommend",
            "impact_value_usd": 150000,
            "delay_days": 0,
            "customer_critical": False,
            "patient_critical": False,
        },
    },


    # ========================================================
    # TEST 5
    # CANCEL ORDER + REFUND
    # ========================================================

    {
        "name": "Supplier cannot fulfill - Cancel and refund",

        "expected_action": "cancel_order_refund",

        "expected_approval": True,

        "input": {
            "order_id": "SO-1005",
            "product": "Medicine-B",
            "supplier": "Unavailable Pharma",
            "ordered_qty": 5000,

            # Nothing can be fulfilled
            "affected_qty": 5000,

            "disruption_type": "supplier_unable_to_fulfill",
            "requested_action": "auto_recommend",
            "impact_value_usd": 50000,
            "delay_days": 0,
            "customer_critical": False,
            "patient_critical": False,
        },
    },
]


# ============================================================
# HELPER
# ============================================================

def get_text_from_result(result) -> str:

    parts = []

    for content in result.content:

        if hasattr(content, "text"):
            parts.append(content.text)

    return "\n".join(parts)


# ============================================================
# RUN SINGLE TEST
# ============================================================

async def run_test(session, case: dict) -> bool:

    print("\n")
    print("=" * 70)
    print(f"TEST: {case['name']}")
    print("=" * 70)

    print("\nINPUT:")

    print(
        json.dumps(
            case["input"],
            indent=2,
        )
    )


    # ========================================================
    # CALL MCP TOOL
    # ========================================================

    result = await session.call_tool(
        "evaluate_supply_decision",
        case["input"],
    )


    # ========================================================
    # GET RESPONSE TEXT
    # ========================================================

    response_text = get_text_from_result(
        result
    )

    print("\nMCP RESPONSE:")

    print(response_text)


    # ========================================================
    # PARSE JSON RESPONSE
    # ========================================================

    try:

        response_data = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        print(
            "\n❌ FAIL: MCP did not return valid JSON"
        )

        return False


    # ========================================================
    # VALIDATE ACTION
    # ========================================================

    actual_action = response_data.get(
        "recommended_action"
    )

    actual_approval = response_data.get(
        "requires_approval"
    )

    actual_execution = response_data.get(
        "execution_allowed"
    )


    expected_action = case[
        "expected_action"
    ]

    expected_approval = case[
        "expected_approval"
    ]


    action_pass = (
        actual_action
        == expected_action
    )

    approval_pass = (
        actual_approval
        == expected_approval
    )


    # ========================================================
    # DISPLAY VALIDATION
    # ========================================================

    print("\nVALIDATION:")

    print(
        f"Expected Action: {expected_action}"
    )

    print(
        f"Actual Action:   {actual_action}"
    )

    print(
        f"Action: "
        f"{'✅ PASS' if action_pass else '❌ FAIL'}"
    )

    print()

    print(
        f"Expected Approval: "
        f"{expected_approval}"
    )

    print(
        f"Actual Approval:   "
        f"{actual_approval}"
    )

    print(
        f"Approval: "
        f"{'✅ PASS' if approval_pass else '❌ FAIL'}"
    )

    print()

    print(
        f"Execution Allowed: "
        f"{actual_execution}"
    )


    return (
        action_pass
        and approval_pass
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    server_params = StdioServerParameters(

        command="python",

        args=[
            "policy_mcp_server.py"
        ],
    )


    # ========================================================
    # START MCP SERVER + CONNECT
    # ========================================================

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            print("\n")

            print(
                "=" * 70
            )

            print(
                "SUPPLYSYNC POLICY MCP CLIENT TEST"
            )

            print(
                "=" * 70
            )


            print(
                "\nConnecting to Policy MCP Server..."
            )

            await session.initialize()

            print(
                "Connected successfully!"
            )


            # =================================================
            # LIST TOOLS
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
            # RUN TESTS
            # =================================================

            passed = 0

            failed = 0


            for case in TEST_CASES:

                success = await run_test(
                    session,
                    case,
                )

                if success:

                    passed += 1

                else:

                    failed += 1


            # =================================================
            # FINAL SUMMARY
            # =================================================

            print("\n")

            print(
                "=" * 70
            )

            print(
                "FINAL TEST SUMMARY"
            )

            print(
                "=" * 70
            )

            print(
                f"Total Tests: {len(TEST_CASES)}"
            )

            print(
                f"Passed: {passed}"
            )

            print(
                f"Failed: {failed}"
            )

            print(
                "=" * 70
            )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
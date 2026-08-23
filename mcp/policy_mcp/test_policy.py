import json

from rag.rag_engine import evaluate_policy


cases = [

    # =========================================================
    # TEST 1
    # RESCHEDULE ORDER
    # =========================================================

    {
        "name": "Reschedule order by 3 days - No approval",

        "expected_action": "reschedule_order",

        "expected_requires_approval": False,

        "situation": {

            "order_id": "SO-1001",

            "product": "Paracetamol 500mg",

            "supplier": "Acme Pharma",

            "ordered_qty": 10000,

            "affected_qty": 0,

            "disruption_type": "supplier_delay",

            "requested_action": "auto_recommend",

            "delay_days": 3,

            "customer_critical": False,

            "patient_critical": False,

            "impact_value_usd": 2500,
        },
    },


    # =========================================================
    # TEST 2
    # PARTIAL ORDER - 75% FULFILLMENT
    # APPROVAL REQUIRED
    # =========================================================

    {
        "name": "Partial order - 75 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_requires_approval": True,

        "situation": {

            "order_id": "SO-1002",

            "product": "Paracetamol 500mg",

            "supplier": "BioSource",

            "ordered_qty": 10000,

            # 2,500 affected
            # 7,500 fulfillable
            # 75% fulfillment

            "affected_qty": 2500,

            "disruption_type": "supplier_partial_fulfillment",

            "requested_action": "auto_recommend",

            "impact_value_usd": 45000,
        },
    },


    # =========================================================
    # TEST 3
    # PARTIAL ORDER - 90% FULFILLMENT
    # NO APPROVAL
    # =========================================================

    {
        "name": "Partial order - 90 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_requires_approval": False,

        "situation": {

            "order_id": "SO-1003",

            "product": "Paracetamol 500mg",

            "supplier": "Acme Pharma",

            "ordered_qty": 10000,

            # 1,000 affected
            # 9,000 fulfillable
            # 90% fulfillment

            "affected_qty": 1000,

            "disruption_type": "supplier_partial_fulfillment",

            "requested_action": "auto_recommend",

            "impact_value_usd": 10000,
        },
    },


    # =========================================================
    # TEST 4
    # PARTIAL ORDER - BELOW 50%
    # APPROVAL REQUIRED
    # =========================================================

    {
        "name": "Partial order - Below 50 percent fulfillment",

        "expected_action": "partial_order_revised_payment",

        "expected_requires_approval": True,

        "situation": {

            "order_id": "SO-1004",

            "product": "Medicine-A",

            "supplier": "ABC Pharma",

            "ordered_qty": 4000,

            # 3,000 affected
            # 1,000 fulfillable
            # 25% fulfillment

            "affected_qty": 3000,

            "disruption_type": "supplier_partial_fulfillment",

            "requested_action": "auto_recommend",

            "impact_value_usd": 150000,
        },
    },


    # =========================================================
    # TEST 5
    # CANCEL ORDER + REFUND
    # =========================================================

    {
        "name": "Supplier cannot fulfill - Cancel and refund",

        "expected_action": "cancel_order_refund",

        "expected_requires_approval": True,

        "situation": {

            "order_id": "SO-1005",

            "product": "Medicine-B",

            "supplier": "Unavailable Pharma",

            "ordered_qty": 5000,

            # Nothing can be fulfilled

            "affected_qty": 5000,

            "disruption_type": "supplier_unable_to_fulfill",

            "requested_action": "auto_recommend",

            "impact_value_usd": 50000,
        },
    },
]


def run_test(case: dict):

    print("\n")

    print("=" * 70)

    print(
        f"TEST: {case['name']}"
    )

    print("=" * 70)

    print("\nINPUT:")

    print(
        json.dumps(
            case["situation"],
            indent=2,
        )
    )


    # =========================================================
    # CALL POLICY ENGINE
    # =========================================================

    result = evaluate_policy(
        case["situation"]
    )


    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    print("\nPOLICY RESULT:")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


    # =========================================================
    # VALIDATION
    # =========================================================

    actual_action = (
        result.get(
            "recommended_action"
        )
    )

    actual_approval = (
        result.get(
            "requires_approval"
        )
    )

    expected_action = (
        case[
            "expected_action"
        ]
    )

    expected_approval = (
        case[
            "expected_requires_approval"
        ]
    )


    action_pass = (
        actual_action
        == expected_action
    )

    approval_pass = (
        actual_approval
        == expected_approval
    )


    print("\nVALIDATION:")

    print(
        f"Expected Action: {expected_action}"
    )

    print(
        f"Actual Action:   {actual_action}"
    )

    print(
        f"Action Test: "
        f"{'PASS' if action_pass else 'FAIL'}"
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
        f"Approval Test: "
        f"{'PASS' if approval_pass else 'FAIL'}"
    )

    return (
        action_pass
        and approval_pass
    )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    print("\n")

    print("=" * 70)

    print(
        "SUPPLYSYNC POLICY RAG TEST"
    )

    print("=" * 70)


    passed = 0

    failed = 0


    for case in cases:

        success = run_test(
            case
        )

        if success:

            passed += 1

        else:

            failed += 1


    # =========================================================
    # FINAL SUMMARY
    # =========================================================

    print("\n")

    print("=" * 70)

    print(
        "FINAL TEST SUMMARY"
    )

    print("=" * 70)

    print(
        f"Total Tests: {len(cases)}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print("=" * 70)
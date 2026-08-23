import json

from mcp.server.fastmcp import FastMCP

from mcp.server.transport_security import (
    TransportSecuritySettings,
)

from rag.rag_engine import (
    evaluate_policy,
    retrieve,
)


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP(

    "SupplySync Policy Server",

    host="0.0.0.0",

    port=9000,

    streamable_http_path="/mcp",

    transport_security=TransportSecuritySettings(

        enable_dns_rebinding_protection=True,

        allowed_hosts=[

            "127.0.0.1:9000",

            "localhost:9000",

            "192.168.29.234:9000",
        ],

        allowed_origins=[

            "http://127.0.0.1:9000",

            "http://localhost:9000",

            "http://192.168.29.234:9000",
        ],
    ),
)


# ============================================================
# SEARCH POLICY TOOL
# ============================================================

@mcp.tool()
def search_policy(

    query: str,

    top_k: int = 5,

) -> str:

    """
    Search pharmaceutical policy/SOP/contract knowledge
    and return cited evidence.
    """

    return json.dumps(

        {

            "query": query,

            "results": retrieve(
                query,
                top_k,
            ),
        },

        indent=2,
    )


# ============================================================
# EVALUATE SUPPLY DECISION
# ============================================================

@mcp.tool()
def evaluate_supply_decision(

    order_id: str,

    product: str,

    supplier: str,

    ordered_qty: int,

    affected_qty: int,

    disruption_type: str,

    requested_action: str = "auto_recommend",

    total_order_amount: float = 0,

    requester_name: str = "",

    requester_email: str = "",

    estimated_delivery_date: str | None = None,

) -> str:

    """
    Evaluate a supply disruption against indexed policies.

    The Policy MCP determines:

    - recommended_action
    - requires_approval
    - approval_reason
    - reschedule_days
    - additional_discount_percent

    The Policy MCP never executes business actions.
    """


    # ========================================================
    # CREATE POLICY SITUATION
    # ========================================================

    situation = {

        "order_id": order_id,

        "product": product,

        "supplier": supplier,

        "ordered_qty": ordered_qty,

        "affected_qty": affected_qty,

        "disruption_type": disruption_type,

        "requested_action": requested_action,

        "total_order_amount":
            total_order_amount,

        "requester_name":
            requester_name,

        "requester_email":
            requester_email,

        "estimated_delivery_date":
            estimated_delivery_date,
    }


    # ========================================================
    # EVALUATE POLICY
    # ========================================================

    result = evaluate_policy(
        situation
    )


    # ========================================================
    # ADD ORDER ID
    # ========================================================

    result["order_id"] = order_id


    # ========================================================
    # NORMALIZE RESCHEDULE DAYS
    # ========================================================

    if (
        result.get(
            "recommended_action"
        )
        ==
        "reschedule_order"
    ):

        if (
            result.get(
                "reschedule_days"
            )
            is None
        ):

            result[
                "reschedule_days"
            ] = 0

    else:

        result[
            "reschedule_days"
        ] = None


    # ========================================================
    # NORMALIZE ADDITIONAL DISCOUNT
    # ========================================================

    if (
        result.get(
            "additional_discount_percent"
        )
        is None
    ):

        result[
            "additional_discount_percent"
        ] = 0


    # ========================================================
    # EXECUTION ALLOWED
    # ========================================================

    result[
        "execution_allowed"
    ] = bool(

        result.get(
            "recommended_action"
        )

        and

        not result.get(
            "requires_approval",
            True,
        )

        and

        float(
            result.get(
                "confidence",
                0,
            )
        )
        >=
        0.70

        and

        not result.get(
            "policy_conflict",
            False,
        )
    )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return json.dumps(

        result,

        indent=2,
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(

        "\n"
        "====================================================\n"
        "SupplySync Policy MCP Server\n"
        "====================================================\n"
        "Host: 0.0.0.0\n"
        "Port: 9000\n"
        "Path: /mcp\n"
        "====================================================\n"
    )


    mcp.run(
        transport="streamable-http"
    )
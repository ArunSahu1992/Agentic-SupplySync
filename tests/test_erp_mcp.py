from __future__ import annotations

from mcp.erp_mcp.tools import registry


def test_erp_returns_orders_for_known_material() -> None:
    outcome = registry.call("ERP.get_affected_orders", material_id="DYE-NAVY-4052")

    assert outcome["error"] is None
    assert {order["order_id"] for order in outcome["result"]["orders"]} == {"ORD-4521", "ORD-4522"}


def test_erp_returns_no_impact_for_known_material_without_open_orders() -> None:
    outcome = registry.call("ERP.get_affected_orders", material_id="THR-POLY-22")

    assert outcome == {"result": {"orders": []}, "error": None}


def test_erp_rejects_unknown_material() -> None:
    outcome = registry.call("ERP.get_affected_orders", material_id="UNKNOWN-MATERIAL")

    assert outcome["result"] is None
    assert outcome["error"]["code"] == "NOT_FOUND"

from __future__ import annotations

from typing import Any

from backend.mcp_common.errors import ToolError
from backend.mcp_common.tool_base import ToolRegistry
from mock_systems.erp_api import service

registry = ToolRegistry()


@registry.register("ERP.get_material")
def get_material(material_id: str) -> dict[str, Any]:
    material = service.get_material(material_id)
    if material is None:
        raise ToolError("NOT_FOUND", f"Unknown material_id: {material_id}")
    return material


@registry.register("ERP.get_affected_orders")
def get_affected_orders(material_id: str) -> dict[str, Any]:
    if service.get_material(material_id) is None:
        raise ToolError("NOT_FOUND", f"Unknown material_id: {material_id}")
    return {"orders": service.get_affected_orders(material_id)}

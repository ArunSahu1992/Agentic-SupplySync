from __future__ import annotations

from typing import Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from agents.impact_agent.agent import analyze_disruption
from agents.orchestrator import state
from backend.models.disruption_event import DisruptionEvent


def handle_validated_disruption(event: DisruptionEvent | dict[str, Any]) -> dict[str, Any]:
    disruption = event if isinstance(event, DisruptionEvent) else DisruptionEvent.model_validate(event)
    state.hand_off_to_impact_agent(disruption)
    impact = analyze_disruption(disruption)
    return state.record_impact_result(
        disruption,
        [order.model_dump(mode="json") for order in impact.affected_orders],
        impact.workflow_state,
    )


root_agent = Agent(
    name="orchestrator",
    model="gemini-2.0-flash",
    description="Coordinates validated supply disruptions and impact analysis.",
    instruction="Use get_workflow_status to report current disruption workflow state.",
    tools=[FunctionTool(state.get_status)],
)
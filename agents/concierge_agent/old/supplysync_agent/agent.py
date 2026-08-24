import os

from google.adk.agents import LlmAgent
from google.adk.apps.app import App, ResumabilityConfig

from .orchestrator_agent import orchestrator_agent
from .concierge_agent import concierge_agent
from .action_execution_agent import action_execution_agent
from .concierge_revise_agent import concierge_revise_agent
from .notification_agent import notification_agent


MODEL = os.getenv(
    "MODEL",
    "gemini-3.6-flash",
)


root_agent = LlmAgent(
    name="supplysync_workflow",

    model=MODEL,

    description=(
        "Root coordinator for the SupplySync supply disruption "
        "resolution workflow."
    ),

    instruction="""
You are the SupplySync Root Workflow Agent.

Your only responsibility is to start the workflow.

For every new SupplySync order request,
immediately transfer control to:

orchestrator_agent


Do not:

- evaluate policy
- call the Policy MCP
- call the Action MCP
- execute business actions
- send notifications
- perform audit logging
- produce the final workflow result


The workflow is:

orchestrator_agent
        ->
concierge_agent
        ->
        ┌───────────────────────────────┐
        │                               │
requires_approval                  no approval
        │                               │
        ▼                               ▼
Human Confirmation              Auto Authorized
        │                               │
   ┌────┴────┐                          │
   │         │                          │
APPROVED  REJECTED                      │
   │         │                          │
   ▼         ▼                          ▼
Action      Concierge                Action
Execution   Revise                   Execution
Agent       Agent                    Agent
   │         │                          │
   └─────────┴──────────────────────────┘
                     │
                     ▼
              Notification Agent
                     │
                     ▼
              Notification MCP
                     │
          EMAIL / LOG / ALL


Always start by transferring to:

orchestrator_agent
""",

    sub_agents=[
        orchestrator_agent,
        concierge_agent,
        action_execution_agent,
        concierge_revise_agent,
        notification_agent,
    ],
)


app = App(
    name="supplysync_app",

    root_agent=root_agent,

    resumability_config=ResumabilityConfig(
        is_resumable=True
    ),
)
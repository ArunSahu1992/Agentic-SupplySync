import os

from google.adk.agents import LlmAgent

from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)


# ============================================================
# MODEL
# ============================================================

MODEL = os.getenv(
    "MODEL",
    "gemini-3.6-flash",
)


# ============================================================
# NOTIFICATION MCP URL
# ============================================================

NOTIFICATION_MCP_URL = os.getenv(
    "NOTIFICATION_MCP_URL",
    "http://127.0.0.1:9002/mcp",
)


# ============================================================
# NOTIFICATION MCP CONNECTION
# ============================================================

notification_mcp_tools = McpToolset(

    connection_params=StreamableHTTPConnectionParams(

        url=NOTIFICATION_MCP_URL,

        timeout=30.0,

        sse_read_timeout=300.0,

        terminate_on_close=False,
    )
)


# ============================================================
# NOTIFICATION AGENT
# ============================================================

notification_agent = LlmAgent(

    name="notification_agent",

    model=MODEL,

    description=(
        "Processes post-action notifications and returns the "
        "complete SupplySync workflow result."
    ),

    instruction="""
You are the SupplySync Notification Agent.

You run after a successful business action.

You receive workflow state containing:

- order_data
- policy_result
- action_result
- workflow_decision
- human_response


============================================================
DO NOT CHANGE PREVIOUS RESULTS
============================================================

You MUST NOT:

- call the Policy MCP
- re-evaluate policy
- change policy_result
- change workflow_decision
- change human_response
- change action_result
- execute another business action
- calculate discounts
- calculate delivery dates
- invent missing business values


============================================================
VALIDATION
============================================================

Only process notification when:

workflow_decision is:

- APPROVED
- NO_APPROVAL_REQUIRED

AND:

action_result.action_status = SUCCESS


If action execution failed:

Do NOT send a success notification.


============================================================
CALL NOTIFICATION MCP
============================================================

Use the available MCP tool:

process_notification


Use the exact tool schema exposed by the
Notification MCP.

The MCP tool schema is authoritative.

Do not invent parameters.

Do not invent notification modes.

Use exact workflow values from order_data.


workflow_id:

order_data.workflow_id


order_id:

order_data.order_id


Use contact information exactly as available in
order_data.

Do not modify:

- workflow_id
- order_id
- email
- mobile number


============================================================
NOTIFICATION RESULT
============================================================

The response returned by:

process_notification

must be preserved completely.

Store that response as:

notification_result


Do NOT:

- remove fields
- rename fields
- summarize fields
- change notification_status
- modify email_result
- modify sms_result
- modify audit_result


============================================================
FINAL WORKFLOW RESPONSE
============================================================

After process_notification completes, return the
COMPLETE workflow response.

Do NOT return only notification_result.

Your final response MUST contain:

{
    "workflow_id": "...",
    "order_id": "...",
    "workflow_decision": "...",
    "human_response": "...",
    "policy_result": {},
    "action_result": {},
    "notification_result": {},
    "final_status": "COMPLETED"
}


============================================================
FIELD MAPPING
============================================================

workflow_id:

Use:

order_data.workflow_id


order_id:

Use:

order_data.order_id


workflow_decision:

Preserve the existing value exactly.


human_response:

Preserve the existing value exactly.


policy_result:

Preserve the COMPLETE existing policy_result.

Do not remove or modify any field.


action_result:

Preserve the COMPLETE existing action_result.

Do not remove or modify any field.


notification_result:

Use the COMPLETE response returned by:

process_notification


final_status:

If:

action_result.action_status = SUCCESS

AND:

notification_result.notification_status = SUCCESS

Then:

final_status = COMPLETED


Otherwise:

final_status = FAILED


============================================================
CRITICAL OUTPUT RULES
============================================================

Return valid JSON only.

Do NOT return:

- only notification_result
- a notification summary
- natural language
- explanations
- markdown
- comments
- text before JSON
- text after JSON


The final output MUST contain all of these:

workflow_id
order_id
workflow_decision
human_response
policy_result
action_result
notification_result
final_status


Example structure:

{
    "workflow_id": "WF-RESCHEDULE-1005",

    "order_id": "ORD-RESCHEDULE-1005",

    "workflow_decision": "APPROVED",

    "human_response": "YES",

    "policy_result": {
        "eligible_actions": [],
        "recommended_action": "...",
        "requires_approval": true
    },

    "action_result": {
        "workflow_id": "...",
        "order_id": "...",
        "action_status": "SUCCESS",
        "executed_action": "..."
    },

    "notification_result": {
        "notification_mode": "...",
        "workflow_id": "...",
        "order_id": "...",
        "notification_status": "SUCCESS"
    },

    "final_status": "COMPLETED"
}


Never return only this:

{
    "notification_mode": "EMAIL",
    "notification_status": "SUCCESS"
}


You must return the COMPLETE workflow result.
""",

    tools=[
        notification_mcp_tools,
    ],
)
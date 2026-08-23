import os

from google.adk.agents import LlmAgent


# ============================================================
# MODEL
# ============================================================

MODEL = os.getenv(
    "MODEL",
    "gemini-3.6-flash",
)


# ============================================================
# LOGGING AGENT
# ============================================================

logging_agent = LlmAgent(

    name="logging_agent",

    model=MODEL,

    description=(
        "Builds the final SupplySync workflow result using the "
        "order, policy, action or revision result, and the "
        "Notification MCP result."
    ),

    instruction="""
You are the SupplySync Final Result Agent.

You are the FINAL agent in the SupplySync workflow.

Your responsibility is to prepare and return the
complete final SupplySync workflow result.

The actual customer email and audit logging are
handled by the external Notification MCP through:

notification_agent


Do NOT:

- execute any business action
- call Action MCP
- call Policy MCP
- send an email directly
- create an audit log directly
- ask for approval
- re-evaluate policy
- transfer to another agent


============================================================
WORKFLOW STATE
============================================================

Read the existing workflow state.

The following data may exist:

- order_data
- policy_result
- action_result
- revision_result
- notification_result
- workflow_decision
- human_response


============================================================
IMPORTANT DATA SOURCES
============================================================

Original order information comes from:

order_data


Policy decision information comes from:

policy_result


For approved or automatically authorized workflows,
execution information comes from:

action_result


For rejected workflows,
rejection information comes from:

revision_result


Notification and audit information comes from:

notification_result


Do not invent missing information.

Use the actual values available in workflow state.


============================================================
ORDER DATA
============================================================

Read these values from:

order_data

- workflow_id
- order_id
- product
- supplier
- ordered_qty
- affected_qty
- total_order_amount
- requester_name
- requester_email
- estimated_delivery_date


============================================================
POLICY DATA
============================================================

Read these values from:

policy_result

- recommended_action
- requires_approval
- confidence
- policy_conflict
- execution_allowed
- approval_reason
- reason
- additional_discount_percent
- reschedule_days


Do not modify Policy MCP values.

Preserve the exact:

- recommended_action
- additional_discount_percent
- reschedule_days
- reason
- approval_reason
- confidence


============================================================
APPROVED WORKFLOW
============================================================

If:

workflow_decision = "APPROVED"

or:

workflow_decision = "NO_APPROVAL_REQUIRED"


Read execution information from:

action_result


Preserve the complete action_result.


If:

action_result.action_status = "SUCCESS"


Set:

final_status = "COMPLETED"


If action execution failed:

final_status = "ACTION_FAILED"


============================================================
REJECTED WORKFLOW
============================================================

If:

workflow_decision = "REJECTED"


Read rejection information from:

revision_result


The rejected workflow must preserve:

action_status = "SKIPPED"

executed_action = "NONE"


Set:

final_status = "REJECTED"


A human rejection does NOT mean:

- CANCELLED
- REFUNDED
- RESCHEDULED
- EXECUTED


unless such an action was actually approved and
executed.

Do not change the original Policy MCP decision.


============================================================
ACTION EXECUTION
============================================================

For approved or automatically authorized workflows,
use the complete:

action_result


The final output must preserve:

action_status

executed_action

execution_details


Do not remove execution details.


For example, preserve values such as:

- fulfillable_qty
- fulfillment_percentage
- total_order_amount
- original_partial_amount
- additional_discount_percent
- discount_amount
- revised_final_amount
- estimated_delivery_date
- reschedule_days
- revised_delivery_date


For rejected workflows use:

revision_result.action_execution


which should contain:

{
    "action_status": "SKIPPED",
    "executed_action": "NONE",
    "execution_details": {}
}


============================================================
NOTIFICATION MCP RESULT
============================================================

The Notification Agent calls the external
Notification MCP.

Read the actual result from:

notification_result


The Notification MCP may process:

- EMAIL
- AUDIT
- BOTH


Preserve only the actual results returned by
the Notification MCP.

Do not invent:

- notification_status
- notification_recipient
- email_subject
- email_error
- audit_status
- audit_id


============================================================
EMAIL RESULT
============================================================

If notification_result contains an email result,
preserve the actual values.

For example:

notification_status

notification_recipient

email_subject

email_error


If the email was successfully sent:

notification_status = "SENT"


If the email failed:

notification_status = "FAILED"


Preserve the actual error.

Do not invent delivery IDs or provider IDs.


If no email was requested or processed, preserve
the actual Notification MCP result.

Do not automatically mark the email as SENT.


============================================================
AUDIT RESULT
============================================================

If notification_result contains an audit result,
preserve the actual:

audit_status

audit_id


Do not generate or invent an audit ID.


If audit logging failed, preserve the actual
failure result.


============================================================
FINAL STATUS RULES
============================================================

Use these business workflow rules:


APPROVED

+

action executed successfully

=

COMPLETED



NO_APPROVAL_REQUIRED

+

action executed successfully

=

COMPLETED



APPROVED

+

action execution failed

=

ACTION_FAILED



NO_APPROVAL_REQUIRED

+

action execution failed

=

ACTION_FAILED



REJECTED

=

REJECTED


The Notification MCP result must not change the
business workflow decision.

For example:

If the business action succeeded but the email
fails, the business workflow can still remain:

COMPLETED


The actual notification failure must still be
preserved in:

notification_status

and:

email_error


============================================================
FINAL OUTPUT
============================================================

Return one complete structured result.

Use this structure:


{
    "workflow_id": "...",

    "order_id": "...",

    "workflow_decision": "...",

    "human_response": "...",


    "order": {

        "product": "...",

        "supplier": "...",

        "ordered_qty": 0,

        "affected_qty": 0,

        "total_order_amount": 0,

        "requester_name": "...",

        "requester_email": "...",

        "estimated_delivery_date": "..."
    },


    "policy_decision": {

        "recommended_action": "...",

        "requires_approval": false,

        "confidence": 0.0,

        "policy_conflict": false,

        "execution_allowed": false,

        "approval_reason": "...",

        "reason": "...",

        "additional_discount_percent": 0.0,

        "reschedule_days": null
    },


    "action_execution": {

        "action_status": "...",

        "executed_action": "...",

        "execution_details": {}
    },


    "revision_result": {},


    "audit_status": "...",

    "audit_id": "...",


    "notification_status": "...",

    "notification_recipient": "...",

    "email_subject": "...",

    "email_error": null,


    "final_status": "..."
}


============================================================
CRITICAL PRESERVATION RULE
============================================================

Do not replace actual values with:

- 0
- 0.0
- null
- empty strings
- invented values


For example, if policy_result contains:

recommended_action = "reschedule_order"

reschedule_days = 5

additional_discount_percent = 5.0


The final output MUST preserve:

recommended_action = "reschedule_order"

reschedule_days = 5

additional_discount_percent = 5.0


Do not convert:

reschedule_order

to:

reschedule


Do not change:

5

to:

0


Do not change:

5.0

to:

0.0


============================================================
FINAL RULE
============================================================

You are the final agent.

Do not transfer to another agent.

Return the complete final SupplySync workflow result.
""",

    output_key="logging_result",

    disallow_transfer_to_parent=True,

    disallow_transfer_to_peers=True,
)
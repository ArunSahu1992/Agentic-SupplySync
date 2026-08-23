# NovaPharm AI Agent Governance Policy

Policy ID: AI-GOV-003

Version: 1.1

Effective date: 2026-04-01

Status: Synthetic test document for SupplySync


## 1. Scope

This policy applies to AI agents that evaluate supply disruptions,
retrieve policies, recommend supply-chain actions, and initiate
approved workflow execution.

The policy applies to the following SupplySync governed actions:

- reschedule_order
- cancel_order_refund
- partial_order_revised_payment


## 2. Advisory vs execution

An AI agent may:

- retrieve and evaluate applicable policies
- summarize policy evidence
- identify impacted orders
- calculate fulfillment impact
- recommend a permitted action
- determine whether human approval is required

The AI agent must not execute a governed action when the applicable
policy requires human approval and that approval has not been granted.


## 3. Supported governed actions

SupplySync may recommend one of the following standardized actions.

### 3.1 reschedule_order

This action reschedules an affected order or delivery commitment.

The standard automated recovery period is up to 3 calendar days.

The action may only be recommended when:

- the supplier disruption is temporary
- the order can still be fulfilled
- no quality hold exists
- no patient-critical commitment is negatively affected
- the applicable policy permits rescheduling

The execution layer is responsible for applying the approved
rescheduled date.


### 3.2 cancel_order_refund

This action cancels the affected order and initiates the applicable
refund or payment reversal process.

The action may be recommended when:

- the supplier cannot fulfill the committed order
- the order cannot reasonably be recovered through rescheduling
- partial fulfillment is not permitted or is not acceptable
- cancellation does not violate an applicable quality, regulatory,
  contractual, or patient-critical commitment

The execution layer is responsible for:

- cancelling the order
- initiating the refund process
- recording the action
- notifying the requester or customer


### 3.3 partial_order_revised_payment

This action confirms the fulfillable portion of an order and creates
a revised payment amount.

For SupplySync demonstration workflows:

- the fulfillable quantity must be calculated from the committed
  quantity and affected quantity
- the revised payment must be based on the confirmed quantity
- an additional 2% discount is applied to the revised amount

The execution layer is responsible for:

- confirming the available quantity
- calculating the initial revised amount
- applying the 2% discount
- producing the final revised payment amount
- recording the action
- notifying the requester or customer


## 4. Approval gate

When approval is required, the workflow must enter:

WAITING_FOR_APPROVAL

The pending decision must contain:

- workflow ID
- order ID
- proposed action
- reason
- applicable policy reference
- evidence used for the recommendation
- confidence score

The AI agent must wait for the human decision before execution.

A human response of YES authorizes the approved action to continue
to the Action Executor.

A human response of NO rejects the proposed action.

A rejected action must not be executed.


## 5. No approval required

When the applicable policy explicitly allows automated execution,
the AI agent may mark the decision as:

NO_APPROVAL_REQUIRED

The workflow may proceed directly to the Action Executor only when:

- policy confidence is at least 0.70
- no policy conflict exists
- no quality hold exists
- the action is permitted by the applicable policy


## 6. Low confidence

If policy retrieval or interpretation confidence is below 0.70,
the agent must:

- require human review
- set requires_approval to true
- set execution_allowed to false until approval is received

The agent must not automatically execute an action based on a
low-confidence policy interpretation.


## 7. Policy conflicts

If two applicable policy sources conflict, the agent must:

- flag policy_conflict as true
- require human review
- not automatically execute the action

The agent must not select a rule merely because it produces a more
convenient outcome.


## 8. Execution boundary

The Policy MCP is a governance and decision component.

The Policy MCP must not:

- modify an order
- process a refund
- change a delivery date
- calculate or collect payment
- send operational customer notifications

The Policy MCP returns only the policy decision and recommended action.

Actual execution must be performed by the SupplySync Action Executor.


## 9. Audit trail

Every workflow decision must record:

- workflow ID
- order ID
- recommended action
- policy source
- policy section
- source chunk IDs
- policy evidence
- model confidence
- requires_approval
- human approval state
- execution result
- audit result
- notification result
- timestamp
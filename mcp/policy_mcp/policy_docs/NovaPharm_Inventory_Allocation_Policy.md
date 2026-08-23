# NovaPharm Supply Chain — Inventory Allocation & Critical Medicine Policy

Policy ID: SC-ALLOC-008

Version: 2.5

Effective date: 2026-03-01

Status: Synthetic test document for SupplySync


## 1. Critical medicines

Critical medicines are products designated by Medical Affairs or
Supply Chain Risk Management as patient-critical.


## 2. Allocation changes

An automated system may recommend an allocation change when:

- the change is within an existing allocation plan
- the quantity moved is 10% or less of available inventory

Any reallocation above 10% of available inventory requires Supply
Chain Director approval.


## 3. SupplySync action restrictions

For a patient-critical product or allocation, the following actions
require additional review when they negatively affect the protected
allocation:

- reschedule_order
- cancel_order_refund
- partial_order_revised_payment

The system must not automatically reduce a patient-critical
allocation to satisfy a lower-priority commercial order.


## 4. Partial order decisions

For a critical medicine, a partial order may be recommended only
when the available quantity can be allocated without violating an
existing patient-critical allocation.

If the proposed partial fulfillment changes or reduces a protected
patient-critical allocation:

- requires_approval = true
- Supply Chain Director approval is required
- execution_allowed = false until approval is granted


## 5. Rescheduling

A reschedule that affects a patient-critical commitment requires:

- Supply Chain Director approval

regardless of whether the delay is 3 days or less.


## 6. Cancellation

Cancellation of a patient-critical commitment requires human review
before execution when the cancellation may affect patient access or
an existing protected allocation.


## 7. Audit

Every allocation-related workflow must include:

- order ID
- product
- quantity before action
- quantity after action
- recommended action
- reason
- approval state
- approving person when required
- timestamp
- policy reference
## 2. Partial Order Recovery

### 2.1 Partial fulfillment

When a supplier cannot fulfill the complete order, the system may
recommend a partial order based on the fulfillable quantity.

Fulfillable Quantity:

Fulfillable Quantity = Ordered Quantity - Affected Quantity


### 2.2 Revised payment

When a partial order is confirmed, the revised order amount must be
calculated proportionally based on the fulfillable quantity.

Revised Order Amount:

Revised Order Amount =

Original Order Amount ×

(Fulfillable Quantity / Ordered Quantity)


### 2.3 Partial order customer discount

For an approved partial order, SupplySync may offer an additional
customer discount of 2 percent on the revised order amount.

The discount must be applied only to the revised order amount and not
to the original full order amount.

Discount Amount:

Discount Amount =

Revised Order Amount × 2%

Final Amount To Pay:

Final Amount To Pay =

Revised Order Amount - Discount Amount


### 2.4 Action recommendation

For a partial fulfillment scenario, the recommended action is:

partial_order_revised_payment

The policy decision must return:

- recommended_action
- additional_discount_percentage

For this policy:

additional_discount_percentage = 2


### 2.5 Approval thresholds

If the supplier can fulfill at least 80 percent of the committed
quantity, the partial order may proceed without human approval,
provided no quality hold or patient-critical restriction applies.

If the supplier can fulfill between 50 percent and 79 percent,
Operations Manager approval is required.

If the supplier can fulfill less than 50 percent,
Supply Chain Director approval is required.


## 3. Delivery Rescheduling

### 3.1 Temporary shipment delay

When a supplier experiences a temporary shipment delay and the order
can still be fulfilled, the system may recommend rescheduling the
delivery.

For this scenario, the disruption type may be:

shipment_delay


### 3.2 Action recommendation

For a temporary shipment delay where the supplier can still fulfill
the complete order, the recommended action is:

reschedule_order


### 3.3 Additional reschedule days

When the order is rescheduled, the policy determines the number of
additional calendar days that must be added to the existing estimated
delivery date.

The policy decision must return:

- recommended_action
- reschedule_days

For this policy:

reschedule_days = 5


### 3.4 Revised delivery date

The Policy MCP must not calculate the revised delivery date.

The order provides:

estimated_delivery_date

The Policy MCP provides:

reschedule_days

The Action Execution service calculates:

Revised Delivery Date =

Estimated Delivery Date + Reschedule Days


### 3.5 Customer discount for delivery delay

When an order is delayed for more than 1 calendar day, SupplySync provides an additional customer discount of 5 percent on the order payment.

The Policy MCP determines whether the discount applies.

The policy decision must return:

additional_discount_percent

Rule:

If:

reschedule_days > 1

Then:

additional_discount_percent = 5

Otherwise:

additional_discount_percent = 0

For this policy:

reschedule_days = 5

Therefore:

additional_discount_percent = 5

The Policy MCP must not calculate the discount amount.

The Action Execution service calculates:

Discount Amount =

Total Order Amount × Additional Discount Percentage

Final Amount To Pay:

Final Amount To Pay =

Total Order Amount - Discount Amount


### 3.6 Approval thresholds
If the shipment delay can be resolved within 3 calendar days, the reschedule may proceed without human approval, provided no quality hold, regulatory restriction, or patient-critical restriction applies.

If the policy determines that the shipment delay requires an extension greater than 3 calendar days, human approval is required.

For this policy:

reschedule_days = 5

Therefore:

requires_approval = true


### 3.7 Policy decision output

For a shipment delay under this policy, the Policy MCP should return:

recommended_action = reschedule_order

reschedule_days = 5

additional_discount_percent = 5

requires_approval = true
import uuid


# ============================================================
# CREATE AUDIT LOG
# ============================================================

def create_audit_log(

    workflow_id: str,

    order_id: str,

    workflow_decision: str,

    recommended_action: str,

    final_status: str,

    action_execution: dict,

) -> dict:


    audit_id = str(
        uuid.uuid4()
    )


    return {

        "audit_status": "SUCCESS",

        "audit_id": audit_id,

        "workflow_id": workflow_id,

        "order_id": order_id,

        "workflow_decision": workflow_decision,

        "recommended_action": recommended_action,

        "final_status": final_status,

        "action_execution": action_execution,
    }
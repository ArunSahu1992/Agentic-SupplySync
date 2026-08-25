# Local Supplier-to-Agent Testing

This guide runs the Supplier/Logistics feed separately from the SupplySync backend. A supplier event is sent to the Supplier API, which forwards it to the backend trigger endpoint. The backend automatically starts the Disruption Agent.

```text
Supplier API :8001
    POST /events
        |
        | HTTP forward using SUPPLYSYNC_TRIGGER_URL
        v
SupplySync API :8003
    POST /events/supplier-disruptions
        |
        v
Disruption Agent
    -> Supplier MCP tools
    -> VALIDATED or DISCARDED
    -> Orchestrator handoff record
```

The Orchestrator now invokes the deterministic Impact Agent service. A valid navy disruption should finish in `impact_analyzed` with affected order contexts; a known material without open orders finishes in `no_impact`.

## 1. Install dependencies

From the repository root:

```powershell
cd C:\EpamProject\Agentic-SupplySync
python -m pip install -r requirements.txt
```

## 2. Start the SupplySync backend

Open Terminal 1 and leave it running:

```powershell
cd C:\EpamProject\Agentic-SupplySync
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8003
```

Verify it from Terminal 2:

```powershell
Invoke-WebRequest http://127.0.0.1:8003/health -UseBasicParsing
```

Expected response:

```json
{"status":"ok"}
```

Reset workflow state before a test:

```powershell
Invoke-WebRequest http://127.0.0.1:8003/demo/reset -Method Post -UseBasicParsing
```

## 3. Start the separate Supplier API

Open Terminal 3 and leave it running:

```powershell
cd C:\EpamProject\Agentic-SupplySync
$env:SUPPLYSYNC_TRIGGER_URL = "http://127.0.0.1:8003/events/supplier-disruptions"
python -m uvicorn mock_systems.supplier_api.app:app --host 127.0.0.1 --port 8001
```

Supplier API endpoints:

```text
GET  http://127.0.0.1:8001/events
POST http://127.0.0.1:8001/events
```

## 4. Send a valid supplier event

Run this from Terminal 2:

```powershell
$body = @{
    event_id = "EVT-LOCAL-VALID-001"
    material_id = "DYE-NAVY-4052"
    event_type = "shipment_delay"
    severity = "high"
    estimated_duration_days = 8
    reported_at = "2026-08-24T10:00:00Z"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://127.0.0.1:8001/events `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  -UseBasicParsing
```

Expected Supplier response:

```json
{
  "event_id": "EVT-LOCAL-VALID-001",
  "status": "new",
  "created": true,
  "triggered": true
}
```

The `triggered: true` field confirms that the Supplier API forwarded the event to the backend. The backend returns `202` because processing is dispatched as a background task.

Because processing is asynchronous, query `/demo/status` again if the first request still shows empty lists. The event is complete when it appears there and has status `processed` in the Supplier API.

## 5. Confirm the Disruption Agent ran

Query the backend workflow state:

```powershell
(Invoke-WebRequest http://127.0.0.1:8003/demo/status -UseBasicParsing).Content
```

Expected result contains:

```json
{
  "validated": [
    {
      "disruption": {
        "event_id": "EVT-LOCAL-VALID-001"
      },
      "workflow_state": "impact_analyzed"
    }
  ],
  "discarded": []
}
```

This proves the path:

```text
Supplier API -> backend webhook -> Disruption Agent -> Orchestrator -> Impact Agent -> ERP MCP
```

Check the Supplier event status:

```powershell
(Invoke-WebRequest "http://127.0.0.1:8001/events?status=processed" -UseBasicParsing).Content
```

The event should have status `processed`, confirming the Disruption Agent acknowledged it through Supplier MCP.

## 6. Test the discard path

Send a low-confidence event:

```powershell
$body = @{
    event_id = "EVT-LOCAL-NOISE-001"
    material_id = "FAB-COTTON-118"
    event_type = "shipment_delay"
    severity = "low"
    estimated_duration_days = 1
    reported_at = "2026-08-24T10:05:00Z"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://127.0.0.1:8001/events `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  -UseBasicParsing
```

Check status again:

```powershell
(Invoke-WebRequest http://127.0.0.1:8003/demo/status -UseBasicParsing).Content
```

Expected:

```text
EVT-LOCAL-NOISE-001 -> discarded
```

The noise event must not appear in `validated`.

## 7. Test duplicate delivery

Send the same event ID again. The Supplier API should return:

```json
{
  "created": false,
  "triggered": false
}
```

Because the event already exists, it is not forwarded a second time.

## 8. Optional ADK Web inspection

ADK Web is separate from the automatic Supplier trigger. Start it in Terminal 4:

```powershell
cd C:\EpamProject\Agentic-SupplySync
$env:ENABLE_ADK_DEMO_TOOLS = "true"
python -m google.adk.cli web
```

Open:

http://127.0.0.1:8000

ADK Web can show manual tool calls such as `check_new_disruption_events` and `get_workflow_status`. The automatic Supplier-triggered request is initiated by the Supplier API, not by an ADK Web prompt.

## 9. Run automated tests

```powershell
python -m pytest -q
```

Expected result for the current implementation:

```text
23 passed
```

## Troubleshooting ports

Check listeners:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,8001,8003
```

ADK Web uses `8000`, Supplier API uses `8001`, and the SupplySync backend uses `8003` in this guide.
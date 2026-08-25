from __future__ import annotations

import os

# Threshold is injected config, not a vertical literal in agent logic (Canonical Spec §3.2).
CONFIDENCE_THRESHOLD = float(os.getenv("DISRUPTION_AGENT_CONFIDENCE_THRESHOLD", "0.6"))

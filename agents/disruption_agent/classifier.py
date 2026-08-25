"""Deterministic POC classification scorer; swappable for an LLM-based classifier later."""

from __future__ import annotations

from typing import Any

_SEVERITY_WEIGHT = {"high": 0.9, "medium": 0.65, "low": 0.35}


def classify_confidence(event: dict[str, Any]) -> float:
    severity = event.get("severity", "low")
    duration = event.get("estimated_duration_days") or 0
    base = _SEVERITY_WEIGHT.get(severity, 0.35)
    duration_bonus = min(duration / 10, 0.1)
    return round(min(base + duration_bonus, 1.0), 2)

from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

PROJECT = "event-log-explorer"
REQUIRED_FIELDS = ["stream","events"]

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)

def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def build_timeline(record: dict[str, Any]) -> list[dict[str, Any]]:
    events = record["events"]
    if not _text(record["stream"]) or not isinstance(events, list) or not events:
        raise ValueError("stream and events are required")
    timeline: list[dict[str, Any]] = []
    for expected, event in enumerate(events, start=1):
        if not isinstance(event, dict) or not _integer(event.get("sequence")) or event["sequence"] != expected or not _text(event.get("type")):
            raise ValueError("events must be contiguous and typed")
        timeline.append({"sequence": expected, "type": event["type"], "payload": event.get("payload", {})})
    return timeline

def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    artifact: Any = None
    if missing:
        status = "blocked"
        reason = "missing required fields: " + ", ".join(missing)
    else:
        try:
            artifact = build_timeline(record)
            status = "passed"
            reason = "build_timeline completed"
        except (TypeError, ValueError, KeyError) as exc:
            status = "failed"
            reason = str(exc)
    receipt = {"project": PROJECT, "status": status, "reason": reason, "record": record, "timeline": artifact}
    receipt["evidence_sha256"] = sha256(_canonical(receipt).encode()).hexdigest()
    return receipt


from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

PROJECT = "codebase-onboarding-guide-generator"
REQUIRED_FIELDS = ["project","entrypoints","commands","tests"]

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

def generate_guide(record: dict[str, Any]) -> str:
    project = record["project"]
    groups = [record["entrypoints"], record["commands"], record["tests"]]
    if not _text(project) or any(not _string_list(group) for group in groups):
        raise ValueError("project and guide sections must contain non-empty strings")
    return "\n".join([
        f"# {project}",
        "## Entrypoints", *[f"- {item}" for item in record["entrypoints"]],
        "## Commands", *[f"- `{item}`" for item in record["commands"]],
        "## Tests", *[f"- `{item}`" for item in record["tests"]],
    ]) + "\n"

def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    artifact: Any = None
    if missing:
        status = "blocked"
        reason = "missing required fields: " + ", ".join(missing)
    else:
        try:
            artifact = generate_guide(record)
            status = "passed"
            reason = "generate_guide completed"
        except (TypeError, ValueError, KeyError) as exc:
            status = "failed"
            reason = str(exc)
    receipt = {"project": PROJECT, "status": status, "reason": reason, "record": record, "guide_markdown": artifact}
    receipt["evidence_sha256"] = sha256(_canonical(receipt).encode()).hexdigest()
    return receipt


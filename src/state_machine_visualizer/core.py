from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

PROJECT = "state-machine-visualizer"
REQUIRED_FIELDS = ["name","states","initial","transitions"]

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

def render_state_machine(record: dict[str, Any]) -> str:
    states = record["states"]
    transitions = record["transitions"]
    if not _text(record["name"]) or not _string_list(states) or len(states) != len(set(states)):
        raise ValueError("states must be unique non-empty strings")
    if record["initial"] not in states or not isinstance(transitions, list) or not transitions:
        raise ValueError("initial state and transitions are required")
    graph: dict[str, set[str]] = {state: set() for state in states}
    for transition in transitions:
        if not isinstance(transition, list) or len(transition) != 2 or transition[0] not in graph or transition[1] not in graph:
            raise ValueError("invalid transition")
        graph[transition[0]].add(transition[1])
    reachable = {record["initial"]}
    frontier = [record["initial"]]
    while frontier:
        current = frontier.pop()
        for target in graph[current]:
            if target not in reachable:
                reachable.add(target); frontier.append(target)
    if reachable != set(states):
        raise ValueError("orphan states are not allowed")
    lines = ["stateDiagram-v2", f"    [*] --> {record['initial']}"]
    lines.extend(f"    {source} --> {target}" for source, target in transitions)
    return "\n".join(lines) + "\n"

def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    artifact: Any = None
    if missing:
        status = "blocked"
        reason = "missing required fields: " + ", ".join(missing)
    else:
        try:
            artifact = render_state_machine(record)
            status = "passed"
            reason = "render_state_machine completed"
        except (TypeError, ValueError, KeyError) as exc:
            status = "failed"
            reason = str(exc)
    receipt = {"project": PROJECT, "status": status, "reason": reason, "record": record, "mermaid": artifact}
    receipt["evidence_sha256"] = sha256(_canonical(receipt).encode()).hexdigest()
    return receipt


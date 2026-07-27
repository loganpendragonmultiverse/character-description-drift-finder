from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

PROJECT = "character-description-drift-finder"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _description_drift(data: dict[str, Any]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in _require(data, "observations"):
        if any(
            item.get(key) in (None, "") for key in ("character", "milestone", "trait", "value")
        ):
            raise ValueError("observations need character, milestone, trait, and value")
        groups[str(item["character"]).casefold(), str(item["trait"]).casefold()].append(dict(item))
    drifts = []
    for items in groups.values():
        items.sort(key=lambda item: item["milestone"])
        if len({str(item["value"]).strip().casefold() for item in items}) > 1:
            drifts.append(
                {"character": items[0]["character"], "trait": items[0]["trait"], "values": items}
            )
    return {"groups_checked": len(groups), "possible_drifts": drifts}


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_description_drift(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

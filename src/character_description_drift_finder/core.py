from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from itertools import pairwise
from typing import Any

PROJECT = "character-description-drift-finder"


def _finite_number(value: Any) -> bool:
    return type(value) is int or isinstance(value, float) and math.isfinite(value)


def _milestone(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return "text"
    if _finite_number(value):
        return "number"
    raise ValueError("milestones must be nonblank strings or finite numbers")


def _validate(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise TypeError("input must be an object")
    entries = data.get("observations")
    if not isinstance(entries, list) or not entries:
        raise ValueError("observations must be a nonempty list")
    kinds: dict[tuple[str, str], str] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise TypeError("observations must be objects")
        for field in ("character", "trait"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError("character and trait must be nonblank strings")
        value = item.get("value")
        if not (isinstance(value, str) and value.strip() or _finite_number(value)):
            raise ValueError("trait values must be nonblank strings or finite numbers")
        kind = _milestone(item.get("milestone"))
        key = (item["character"].casefold(), item["trait"].casefold())
        if key in kinds and kinds[key] != kind:
            raise ValueError("use one milestone type per character and trait")
        kinds[key] = kind


def _description_drift(data: dict[str, Any]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in data["observations"]:
        if any(item.get(key) in (None, "") for key in ("character", "milestone", "trait", "value")):
            raise ValueError("observations need character, milestone, trait, and value")
        groups[str(item["character"]).casefold(), str(item["trait"]).casefold()].append(dict(item))
    annotations: dict[tuple[str, str, Any], dict[str, Any]] = {}
    if "expected_changes" in data:
        entries = data["expected_changes"]
        if not isinstance(entries, list):
            raise ValueError("expected_changes must be a list")
        for entry in entries:
            if (
                not isinstance(entry, dict)
                or any(
                    not isinstance(entry.get(key), str) or not entry[key].strip()
                    for key in ("character", "trait", "reason")
                )
                or not isinstance(entry.get("milestone"), (str, int, float))
            ):
                raise ValueError("expected changes need character, trait, milestone and reason")
            _milestone(entry["milestone"])
            key = (entry["character"].casefold(), entry["trait"].casefold(), entry["milestone"])
            if key in annotations:
                raise ValueError("conflicting expected-change annotations")
            annotations[key] = dict(entry)
    used: set[tuple[str, str, Any]] = set()
    changes = []
    drifts = []
    for items in groups.values():
        items.sort(key=lambda item: item["milestone"])
        if "expected_changes" in data:
            for previous, current in pairwise(items):
                if (
                    str(previous["value"]).strip().casefold()
                    == str(current["value"]).strip().casefold()
                ):
                    continue
                milestone = current["milestone"]
                key = (
                    str(current["character"]).casefold(),
                    str(current["trait"]).casefold(),
                    milestone,
                )
                # Multiple observations at the same milestone cannot identify one exact change.
                if (
                    sum(item["milestone"] == milestone for item in items) != 1
                    and key in annotations
                ):
                    raise ValueError("expected change has ambiguous milestone observations")
                annotation = annotations.get(key)
                if annotation:
                    used.add(key)
                changes.append(
                    {
                        "character": current["character"],
                        "trait": current["trait"],
                        "milestone": milestone,
                        "before": dict(previous),
                        "after": dict(current),
                        "kind": "expected-change" if annotation else "unexplained-change",
                        "annotation": annotation,
                    }
                )
        if len({str(item["value"]).strip().casefold() for item in items}) > 1:
            drifts.append(
                {"character": items[0]["character"], "trait": items[0]["trait"], "values": items}
            )
    if annotations.keys() - used:
        raise ValueError("expected change must reference an exact observed change")
    result: dict[str, Any] = {"groups_checked": len(groups), "possible_drifts": drifts}
    if "expected_changes" in data:
        result["change_reviews"] = changes
    return result


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    _validate(data)
    return {"version": 1, "project": PROJECT, **_description_drift(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append("")
            payload = json.dumps(value, indent=2, ensure_ascii=False)
            fence = chr(96) * max(
                3, max((len(run) for run in re.findall(chr(96) + "+", payload)), default=0) + 1
            )
            lines.append(f"{fence}json\n{payload}\n{fence}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

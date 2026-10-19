import copy
import json

import pytest

from character_description_drift_finder.cli import main
from character_description_drift_finder.core import analyze, render_markdown


def observation(**extra):
    return {"character": "A", "trait": "hair", "milestone": 1, "value": "red", **extra}


@pytest.mark.parametrize(
    "data",
    [
        [],
        {},
        {"observations": []},
        {"observations": {}},
        {"observations": [None]},
        {"observations": [observation(character=" ")]},
        {"observations": [observation(trait=3)]},
        {"observations": [observation(value=None)]},
        {"observations": [observation(value=True)]},
        {"observations": [observation(milestone=True)]},
        {"observations": [observation(milestone=" ")]},
        {"observations": [observation(milestone=float("inf"))]},
        {"observations": [observation(), observation(milestone="2", value="blue")]},
    ],
)
def test_invalid_input_errors(data, tmp_path, capsys):
    source = tmp_path / "bad.json"
    source.write_text(json.dumps(data))
    with pytest.raises((TypeError, ValueError)):
        analyze(data)
    assert main([str(source)]) == 2
    assert "error:" in capsys.readouterr().err


def test_numeric_chronology_exact_annotations_and_long_fence():
    data = {
        "observations": [
            observation(milestone=10, value="blue"),
            observation(milestone=2, value="red"),
        ],
        "expected_changes": [
            {
                "character": "a",
                "trait": "HAIR",
                "milestone": 10,
                "reason": chr(96) * 5 + "\n# authored text",
            }
        ],
    }
    original = copy.deepcopy(data)
    result = analyze(data)
    change = result["change_reviews"][0]
    assert change["before"]["milestone"] == 2
    assert change["kind"] == "expected-change"
    assert len(result["possible_drifts"]) == 1
    markdown = render_markdown(result)
    assert chr(96) * 6 + "json" in markdown
    assert data == original


def test_string_chronology_remains_lexical_and_large_integers_work():
    result = analyze(
        {"observations": [observation(milestone="2"), observation(milestone="10", value="blue")]}
    )
    assert [x["milestone"] for x in result["possible_drifts"][0]["values"]] == ["10", "2"]
    assert analyze({"observations": [observation(milestone=10**500)]})["groups_checked"] == 1
    with pytest.raises(ValueError, match="milestones"):
        analyze(
            {
                "observations": [observation(), observation(milestone=2, value="blue")],
                "expected_changes": [
                    {"character": "A", "trait": "hair", "milestone": True, "reason": "x"}
                ],
            }
        )

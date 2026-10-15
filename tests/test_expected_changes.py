import copy

import pytest

from character_description_drift_finder.core import analyze


def observations():
    return [
        {"character": "Mara", "trait": "hair", "milestone": n, "value": v}
        for n, v in [(1, "black"), (2, "white"), (3, "red")]
    ]


def annotation(**fields):
    return {"character": "Mara", "trait": "hair", "milestone": 2, "reason": "disguise", **fields}


def test_exact_annotation_keeps_drift_and_unexplained_changes():
    data = {"observations": observations(), "expected_changes": [annotation()]}
    original = copy.deepcopy(data)
    report = analyze(data)
    assert report["possible_drifts"][0]["values"] == observations()
    reviews = report["change_reviews"]
    assert [r["kind"] for r in reviews] == ["expected-change", "unexplained-change"]
    assert reviews[0]["annotation"]["reason"] == "disguise"
    assert reviews[1]["annotation"] is None
    assert data == original
    assert "change_reviews" not in analyze({"observations": observations()})


@pytest.mark.parametrize(
    "entries",
    [
        None,
        [None],
        [annotation(reason=" ")],
        [annotation(milestone=None)],
        [annotation(character="Other")],
        [annotation(trait="eyes")],
        [annotation(milestone=1)],
        [annotation(milestone=9)],
        [annotation(), annotation(reason="injury")],
    ],
)
def test_invalid_annotations_reject(entries):
    with pytest.raises(ValueError):
        analyze({"observations": observations(), "expected_changes": entries})


def test_identical_observations_and_ambiguous_milestones():
    items = observations()
    items[1]["value"] = "BLACK"
    assert len(analyze({"observations": items, "expected_changes": []})["change_reviews"]) == 1
    with pytest.raises(ValueError):
        analyze({"observations": items, "expected_changes": [annotation()]})
    items = observations() + [dict(observations()[1], value="blue")]
    with pytest.raises(ValueError, match="ambiguous"):
        analyze({"observations": items, "expected_changes": [annotation()]})
    assert len(analyze({"observations": items, "expected_changes": []})["change_reviews"]) == 3

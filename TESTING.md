# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`.

`tests/test_expected_changes.py` covers exact annotation scope, missing reasons, unknown and conflicting references, identical observations and ambiguous milestones. Existing CLI output refusal tests remain required.

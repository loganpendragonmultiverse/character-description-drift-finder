# Character Description Drift Finder

[![CI](https://github.com/loganpendragonmultiverse/character-description-drift-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/character-description-drift-finder/actions/workflows/ci.yml)

Gather character trait observations by milestone and flag possible description contradictions over time. The command runs locally, uses explicit UTF-8 JSON input, and produces deterministic JSON or Markdown reports without modifying the supplied source material.

## Three-minute start

```bash
python -m pip install .
description-drift examples/sample.json
description-drift examples/sample.json --format json --output report.json
```

The example documents the complete v1 input shape. Markdown is intended for immediate review; JSON preserves structured evidence for scripts and later comparison. An existing output file is never overwritten.

## Privacy and platforms

All character data stays local.

Python 3.10 or newer is supported on Windows, macOS, and Linux. The package has no runtime dependencies, telemetry, account, or hosted service.

## Interpretation boundary

The tool compares explicitly keyed traits. A changed value may reflect disguise, injury, aging, perspective, or intentional development rather than an error.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Expected changes (1.1)

An optional `expected_changes` list explains exact observed transitions:
`[{"character": "Mara", "trait": "hair", "milestone": 2, "reason": "disguise"}]`.
Character and trait matching use the same case folding as observations; milestones
match their supplied value. Observations retain the existing
milestone sort order, so use one consistent type and sortable chronology.

`possible_drifts` retains all observations and warnings. A new `change_reviews`
list labels each adjacent differing value as `expected-change` or
`unexplained-change` and includes before/after evidence and the matched annotation.
An explanation is an author assertion, not a verified resolution. It never explains
another trait, character or milestone. Missing reasons, duplicate annotations,
unknown or unchanged references, and annotated milestones with multiple observations
reject. Identical adjacent values do not create changes. Omitting the field preserves
the legacy report shape.

## Report and release behavior

Install the wheel from the GitHub release with python -m pip install ./PACKAGE.whl,
using the actual downloaded filename. The source distribution can also be installed
with pip. The wheel includes these handoff documents and supplied examples under
share/character-description-drift-finder/ in the installation prefix. A repository checkout is the easiest
way to run the README examples as written.

Invalid inputs or failed output writes return exit status 2. A successful command
returns 0. Report files must be new: existing files, directories and symlinks are
refused. Keep reports outside scanned folders to avoid counting prior reports.
A failed write may leave a partial newly created report; no power-loss transaction
is promised. Closed stdout pipes return 2. Filenames, story data and paths in
reports can be sensitive; review before sharing.

Character and trait names must be nonblank text; trait values are nonblank text or
finite numbers. Within each character/trait group, use either finite numeric
milestones or nonblank text milestones consistently. Text milestones sort
lexically, so "10" sorts before "2"; numeric milestones sort numerically.
Whitespace in character and trait identities is significant. Boolean milestones
and mixed numeric/text chronology are rejected rather than guessed.

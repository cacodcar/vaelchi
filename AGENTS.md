# Working on Vael

Changes require explicit task approval. Complete approved scope without asking
again. Commits, pushes, merges, publication, deletion, and archival require
separate authorization. Preserve existing work; manuscript content is read-only.

Document modified code with clear docstrings and useful comments. Add nearby
assistant/model authorship comments to new code; credit ports with their source
version and preserve original authorship. Keep functions cohesive and Radon
complexity at A or B, including AHC and its helpers. Preserve defaults and compare
algorithm changes against historical inputs, reporting exact or tolerant agreement.

Use `.venv` and all applicable `.vscode/tasks.json` checks: tests, statement and
branch coverage, Radon complexity/maintainability/raw metrics, Flake8, Ruff lint
and formatting, and configured CI/Codacy checks. Record before/after results and
separate existing failures from regressions. Do not suppress findings, weaken
checks, or add trivial tests to inflate coverage. Inspect actual hook results
when commits are authorized. Mypy is configured through the shared quality runner.

See `docs/QUALITY.md` for commands and baseline rules. Never overwrite a recorded
baseline to hide regressions. Numerical correctness takes priority over metrics.

Git test hooks are tracked in `.githooks/` and activated using
`git config --local core.hooksPath .githooks`. They propagate failures. Do not
bypass them to obtain a passing commit or push. Run the tox Python 3.12/3.13
matrix when validating interpreter compatibility. Remote protection and service
requirements are documented in `docs/QUALITY.md`.

Use `.quality-venv/bin/python tools/quality.py all` for the shared blocking
gates and `--baseline` for hash-locked verification. See `docs/QUALITY_GATES.md`.
The original Gana `.venv` and dated baseline are preserved separately.

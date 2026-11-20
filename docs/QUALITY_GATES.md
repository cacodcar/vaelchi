# Enforced quality gates

Vaelchi uses the same Python quality policy as Gana. Run the dedicated environment:

```sh
python3.13 -m venv .quality-venv
.quality-venv/bin/python -m pip install -e '.[test,quality,docs]'
.quality-venv/bin/python tools/quality.py all
```

The VS Code tasks, tox matrix, Git hooks and GitHub Quality workflow all call
`tools/quality.py`. Each invocation writes commands, exit codes, installed
versions and source hashes to a new directory under `quality/runs/`. All
requested gates run even if an earlier gate fails. Existing dated evidence is
never overwritten. Activate the checked-in hooks after cloning with
`git config --local core.hooksPath .githooks`; both hooks propagate gate failures.
No commit or push is needed to run the checks.

## Blocking checks

- Pytest, with Hypothesis seed 20260928 and isolated test/cache files.
- Independent statement and branch coverage floors of **90% and 88%**.
  These preserve Vaelchi's own baseline and are not reduced to Gana's 53%/35%.
- Radon A/B for every function, method and nested closure. Parse failures fail
  the gate. Maintainability and raw metrics are retained as reports.
- Ruff lint, Ruff formatting, and full Flake8 checks. Ruff 0.16.9 is pinned,
  with a 79-character formatting target. Flake8 retains strict E501 checking.
- Mypy checks annotated and unannotated function bodies. Missing dependency
  typing is not ignored. The quality extra pins pandas/SciPy stubs compatible
  with Vaelchi's numerical environment: pandas-stubs 3.0.5.260914 and scipy-stubs
  1.18.1.1. Scikit-learn's unmarked Python modules are analyzed using
  `follow_untyped_imports`, matching Gana's approach to unmarked dependencies.
- Sphinx with warnings treated as errors, and `pip check`.

The Ruff rule selection is shared with Gana. Vaelchi keeps its existing stricter
positional-argument policy and does not copy Gana-specific exceptions for
mathematical class names, import cycles, or serialization tests. Tests are now
included in ordinary Ruff discovery as well as the explicit quality commands.
No new lint suppressions or relaxed coverage/complexity thresholds were added.

## Source and documentation preservation

Tests and their caches run in temporary directories. Linters run from the
repository root so file-pattern rules match, with caches redirected to scratch.
The documentation build uses a disposable copy of `docs/`, `examples/`, and
root-level include targets. Autosummary may change only that copy. Notebooks
are rendered without execution; saved outputs and research computations are
not regenerated. Source hashes include code, tests, tooling, documentation,
examples, requirements, workflow/hook files, and root publication metadata.

## Automatic function profiling

The root `conftest.py` loads the shared profiler for repository pytest runs,
including direct pytest, quality tasks, tox and Git hooks. It records setup,
test calls and teardown in the main thread. Collection/import startup and
subprocess/thread internals are outside that scope. Profiles are diagnostic;
they include instrumentation overhead and are not release performance claims.

Each quality run contains `profile/profile.pstats`, `profile.txt`,
`profile.json` and `comparison.json`. Direct pytest writes unique directories
under `quality/profiles/`. Comparisons require matching tests/data, outcomes,
host, interpreter, dependencies, numerical settings, seed and instrumentation.
Failed or empty runs cannot become automatic references; existing artifacts
are never overwritten. Source changes remain recorded but do not by themselves
prevent comparison of the same workload. Cumulative function times overlap and
must not be summed.

```sh
.quality-venv/bin/python -m pytest tests --function-profile-output /tmp/fresh-vaelchi-profile
.quality-venv/bin/python -m pytest tests --function-profile-reference /path/to/prior/profile.json
```

The profiling modules and runner changes were ported from Gana commit
`cf8f0cd850209db676ee5c04184963de8ab06e2a`. Vaelchi adaptations copy its included
example into the documentation sandbox and omit Gana's Rust-specific source
paths. Profiling introduces no runtime dependency into the Vaelchi package.

## Reproducible environment

`requirements/quality-macos-x86_64-py313.lock` and its JSON manifest record
wheel hashes, exact installed versions and platform identity. The reference is
specific to CPython 3.13.7 on Intel macOS; other platforms require their own
independently measured reference. Verify it with:

```sh
.quality-venv/bin/python tools/quality_lock.py verify
.quality-venv/bin/python tools/quality.py all --baseline
```

To reconstruct in a fresh matching environment:

```sh
python -m pip install --require-hashes --only-binary=:all: --no-deps -r requirements/quality-macos-x86_64-py313.lock
python -m pip install --no-deps --no-build-isolation -e .
python tools/quality.py all --baseline
```

`quality_lock.py create` is an explicit reference-creation operation and refuses
to overwrite an existing lock or manifest. Historical measurements in
`quality/baselines/` remain separate. Environment verification never excuses
a failing code gate.

## Python matrix and hosted checks

`python -m tox` runs the full gate set on Python 3.12 and 3.13. The GitHub
workflow retains the same matrix, builds distributions, smoke-tests the wheel,
and retains quality/build artifacts. Codecov upload failures fail the workflow.
Remote workflow execution, Codecov/Codacy account configuration and branch
protections require separate hosted verification; local success does not claim
that those services ran. No publication or visibility change is performed by
these quality commands.

## Preparing a release

Keep the package version in `pyproject.toml` and `src/vaelchi/__init__.py` aligned
with the README, changelog, and installation guide. The changelog remains
unreleased until publication.

Run the complete gates and Python matrix before building:

```sh
.quality-venv/bin/python tools/quality.py all --baseline
.quality-venv/bin/python -m tox
```

Build a source distribution and a wheel from a clean staging copy. Rebuild the
wheel from the source distribution, inspect both archives, and install the wheel
outside the checkout on each supported test interpreter (3.12 and 3.13).
Check the installed version, representative-day example, calendar filling, and
package tests without adding the checkout's `src` directory to `PYTHONPATH`.
Retain automatic test profiles and record the installed dependency versions.

Validate distribution metadata and README rendering with `twine check --strict`
using a separate packaging environment; installing Twine into the locked
quality environment would change that baseline. Keep artifact checksums and
commands with the release evidence. These checks do not upload distributions.
Verify hosted checks and obtain separate authorization for commits, pushes,
tags, or publication before performing those actions.

The editor uses the pinned Ruff executable. Format-on-save is enabled, with
automatic lint fixes and import sorting disabled. Intentional formatting uses
`.quality-venv/bin/python -m ruff format path/to/file.py`. Black and standalone
isort are not part of this workflow.

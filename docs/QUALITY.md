# Current gate policy

The current enforced configuration is documented in [QUALITY_GATES.md](QUALITY_GATES.md).
The setup descriptions and measurements below record earlier stages and are
not the current release status. In particular, the old missing-license,
uncommitted-repository, `.venv` task, and nonblocking-gate descriptions below
are historical. The MIT license is present, the initial commit is on GitHub,
and current tasks use `.quality-venv` with blocking gates. Hosted CI and service
configuration still need independent verification.

The November 9, 2026 local validation passed all gates on Python 3.12 and 3.13.
Its final Python 3.13 run recorded 83 passing tests, 92.92% statement coverage,
and 92.68% branch coverage. The seven typing errors recorded in October were
resolved. Dated evidence remains under `quality/runs/`; subsequent release
checks must retain their own evidence rather than replace those records.

# Historical quality setup — September 2026

Use Vael's dedicated `.venv` (reference: CPython 3.13.7). From this directory:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pip check
```

VS Code provides **Vael: All Quality Checks** in `.vscode/tasks.json` and
individual tasks. Every task uses `.venv/bin/python`; the aggregate runs checks
independently so a lint failure does not prevent coverage or metrics collection.

Equivalent commands:

```sh
.venv/bin/python -m pytest tests --cov --cov-report=term-missing --cov-report=xml --cov-report=json:quality/reports/coverage.json
.venv/bin/python -m radon cc src/vael -s -a
.venv/bin/python -m radon cc src/vael --min B -s -a
.venv/bin/python -m radon mi src/vael -s
.venv/bin/python -m radon raw src/vael
.venv/bin/python -m flake8 src tests
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ruff format --check src tests
```

Coverage measures both statements and branches, including unimported namespace
package modules. XML and JSON reports go to ignored `quality/reports/`.
No arbitrary coverage threshold has been added: compare both measures against
the recorded baseline and explain regressions. Tests must establish meaningful
behavior, including historical numerical agreement for AHC ports.

Radon reports do not fail on low grades. Review every function against the A/B
requirement; Ruff's C90 rule additionally enforces McCabe complexity <= 10,
which is a related measure rather than an exact substitute for Radon.
Ruff uses the rule selection and exceptions in `ruff.toml`. Explicit `src tests`
arguments also check tests; Flake8 and formatting checks are non-mutating.
No type checker was configured in the inspected reference projects.

The GitHub workflow checks Python 3.12 and 3.13, fails on lint/format findings,
and retains coverage artifacts. `.codacy.yaml` configures code analysis.
The private GitHub repository is `cacodcar/vael`. Remote CI and Codacy
have not run: no commits or workflow files have been pushed. No publishing
workflow or upload credentials were added. The referenced LICENSE file remains missing and needs an author
provided license before release, although editable installation succeeds.

## Additional quality gates

The following records the gate configuration on 2026-09-28.

- `tox.ini` runs test/branch-coverage checks in isolated Python 3.12 and 3.13
  environments. Run `.venv/bin/python -m tox`, or **Vael: Python Version Matrix**.
  Both Python interpreters must be installed. The aggregate VS Code task includes
  the matrix. Each environment writes its own reports under `.tox/`.
- VS Code pytest discovery is enabled, with unittest discovery disabled.
- The workflow uploads `quality/reports/coverage.xml` with Codecov's v5 action.
  Upload failures fail CI. A private-project `CODECOV_TOKEN` repository secret
  and the appropriate Codecov repository connection are required; neither was
  provisioned. Coverage remains available as GitHub workflow artifacts.
- `.githooks/pre-commit` and `.githooks/pre-push` run the shared test/coverage
  gate with `.venv`. They propagate failures, including a missing environment.
  They gate tests/coverage collection; CI separately gates lint and formatting.
  At that stage, Vael had no numeric coverage floor.

Hooks are activated in this checkout. After cloning, activate them with:

```sh
git config --local core.hooksPath .githooks
```

The tox matrix passed all 26 tests on each of Python 3.12 and 3.13.
Expanded tox configuration confirms separate coverage-data paths per environment.
Direct hook validation ran the test suite successfully (26 tests, exit 0) and
injected an invalid pytest option into pre-push (exit 4), confirming errors are
propagated. No commit or push was performed. Shell syntax and YAML/JSON/TOML/INI
configuration parsing passed. The existing five Flake8 findings, four Ruff
findings, and two formatting failures remain unchanged. Radon metrics pass;
A/B ranks remain the required review standard.

### Hosted protection limitation

GitHub returned HTTP 403 for both Vael rulesets and branch protection with:
"Upgrade to GitHub Pro or make this repository public to enable this feature."
Vael was private at the time of this check. Enabling branch protection required
the GitHub plan capability and an initial branch. Configuration files alone
do not establish remote protection or connect Codecov/Codacy.

Reports for this setup are in `quality/runs/gate-parity/`. The original dated
baseline below remains unchanged as historical evidence.

## Initial baseline: 2026-09-28

Raw outputs, commands and exit codes, Python version, exact installed package
versions, source hashes, and coverage reports are in
`quality/baselines/2026-09-28/`. This is a measured local snapshot, not Gana's
platform-specific hash-locked rebuild system. Dependency versions are recorded
in `requirements.txt`; no claim of cross-platform reproducibility is made.
Use a new dated directory for future baselines; retain earlier results.

- Tests: 1 passed.
- Statements: 7/23 covered (30.43%). Branches: 2/8 covered (25%).
- Combined statement/branch coverage: 29.03%.
- Radon: connectivity_matrix A (2), euclidean_distance A (2), normalize B (10).
- All modules have maintainability rank A; raw metrics are saved separately.
- Flake8: six existing findings; same findings as before quality setup.
- Ruff: five findings in unchanged source/tests (newline, exception message,
  unused pytest import, and two test assertions flagged by S101).
- Formatting: three existing files would change. No formatter was applied.
- Dependency consistency and editable package installation passed.

The previous 100% report omitted unimported namespace modules. The lower result
reflects complete measurement, not changed behavior. Source algorithms and tests
were not rewritten to make these checks green. CI will report the existing
lint/format failures until they are addressed. Ruff also warns about the inherited
COM812 rule's possible formatter conflict; it has not been silently disabled.

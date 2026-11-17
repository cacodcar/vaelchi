# Publishing Vaelchi

Releases use the `Publish to PyPI` workflow in `.github/workflows/release.yml`.
It runs the full quality workflow on Python 3.12 and 3.13, verifies that the tag
matches the package version, and publishes the validated Python 3.12 wheel and
source distribution through PyPI Trusted Publishing.

## One-time PyPI setup

Register a GitHub publisher using these exact values:

| Field | Value |
| --- | --- |
| PyPI project | `vaelchi` |
| GitHub owner | `cacodcar` |
| GitHub repository | `vaelchi` |
| Workflow filename | `release.yml` |
| GitHub environment | `pypi` |

For the first upload, use a pending publisher on the PyPI account's Publishing
page. No PyPI API token is stored in the repository.

## Release procedure

1. Follow the distribution validation instructions in
   [Quality gates](QUALITY_GATES.md), under "Preparing a release".
2. Keep the package version, README files, and changelog aligned. The PyPI
   description uses `README-PYPI.md` so that it displays one logo.
3. Confirm that the release commit passes the hosted Python matrix.
4. Publish a GitHub release with the matching tag, for example `v0.1.0`.
5. Check the `Publish to PyPI` workflow and the resulting PyPI project page.
6. Verify installation from PyPI in a clean environment.

If an upload fails, inspect the failed job before rerunning it. PyPI release
files cannot be overwritten; use a new version for changed distributions.

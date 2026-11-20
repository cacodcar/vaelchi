<p align="center">
  <img class="only-dark" src="https://raw.githubusercontent.com/cacodcar/vaelchi/main/docs/_static/vaelchi-logo-dark.png#gh-dark-mode-only" alt="Vaelchi logo" width="75%">
  <img class="only-light" src="https://raw.githubusercontent.com/cacodcar/vaelchi/main/docs/_static/vaelchi-logo-light.png#gh-light-mode-only" alt="Vaelchi logo" width="75%">
</p>

<!-- Version and documentation -->
[![PyPI](https://img.shields.io/pypi/v/vaelchi)](https://pypi.org/project/vaelchi/)
[![Version](https://img.shields.io/badge/version-0.1.1--pre--alpha-orange)](https://github.com/cacodcar/vaelchi/blob/main/CHANGELOG.md)
[![Python Versions](https://img.shields.io/badge/python-3.12%2B-blue)](https://github.com/cacodcar/vaelchi/blob/main/pyproject.toml)
[![Documentation](https://img.shields.io/readthedocs/vaelchi/latest)](https://vaelchi.readthedocs.io/en/latest/index.html)

<!-- Quality and development -->
[![Quality](https://github.com/cacodcar/vaelchi/actions/workflows/quality.yml/badge.svg)](https://github.com/cacodcar/vaelchi/actions/workflows/quality.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/908094a913d94522a0aec929f213f0cb)](https://app.codacy.com/gh/cacodcar/vaelchi/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Coverage](https://codecov.io/gh/cacodcar/vaelchi/graph/badge.svg)](https://codecov.io/gh/cacodcar/vaelchi)
[![License](https://img.shields.io/github/license/cacodcar/vaelchi)](https://github.com/cacodcar/vaelchi/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/cacodcar/vaelchi)](https://github.com/cacodcar/vaelchi/commits/main)

# Vaelchi

Vaelchi is a pre-alpha Python package for time-series analysis. It provides
preprocessing and adjacency-constrained agglomerative hierarchical clustering
(AHC) for one or more aligned numeric time series.

## Features

- Cluster consecutive periods with configurable period and parent lengths.
- Complete timestamped calendars and fill missing values with forward fill,
  backward fill, or time interpolation.
- Select observed representative profiles and retain their original units.
- Export profiles, chronological mappings, weights, and errors as plain data
  for other applications.

## Installation

Python 3.12 or newer is required. Install Vaelchi from PyPI:

```sh
python -m pip install vaelchi
python -c "import vaelchi; print(vaelchi.__version__)"
```

The version check prints the installed version. The pre-alpha API may change
in later releases.

For development, clone the repository and install the optional tools:

```sh
git clone https://github.com/cacodcar/vaelchi.git
cd vaelchi
python -m pip install -e '.[test,quality,docs]'
```

## Quick start

```python

from vaelchi import ahc

result = ahc(
    [10, 12, 10, 12, 20, 24, 20, 24],
    periods=2,
    period_length=2,
)
payload = result.to_dict()
chronological_values = result.reconstruct()
print(payload["weights"])  # [2, 2]
```

Each positional input is one feature. Here, four two-timestep periods become
two representative periods. `labels` maps each original period to a representative
row; `weights` counts the original periods assigned to each row. Profiles retain
input units. The default, `nearest_centroid`, selects an observed member of
each cluster. Pass `selection="legacy"` to reproduce the Vaelchi 0.1.0 default.

## License and authorship

MIT license, copyright Rahul Kakodkar. Original author credits and numerical
validation records are retained.

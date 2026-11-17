# Vael

Vael is a standalone Python package for time-series preprocessing,
clustering, and representative periods. Version **0.1.0** is the first pre-alpha
release candidate, providing adjacency-constrained agglomerative hierarchical
clustering (AHC) for one or more aligned numeric time series.

## Features

- Cluster consecutive periods with configurable period and parent lengths.
- Complete timestamped calendars and fill missing values with forward fill,
  backward fill, or time interpolation.
- Select observed representative profiles and retain their original units.
- Export profiles, chronological mappings, weights, and errors as plain data
  for other applications.

## Installation

Python 3.12 or newer is required. Clone the repository and install Vael:

```sh
git clone https://github.com/cacodcar/vael.git
cd vael
python -m pip install .
```

For development, install the optional tools:

```sh
python -m pip install -e '.[test,quality,docs]'
```

Version 0.1.0 is available from this repository; it has not been published to PyPI.
You can also install a supplied release wheel in a separate environment:

```sh
python -m pip install /path/to/vael-0.1.0-py3-none-any.whl
python -c "import vael; print(vael.__version__)"
```

The printed version should be `0.1.0`. The pre-alpha API may change in later
releases.

## Quick start

```python

from vael import ahc

result = ahc(
    [10, 12, 10, 12, 20, 24, 20, 24],
    periods=2,
    period_length=2,
    selection="nearest_centroid",
)
payload = result.to_dict()
chronological_values = result.reconstruct()
print(payload["weights"])  # [2, 2]
```

Each positional input is one feature. Here, four two-timestep periods become
two representative periods. `labels` maps each original period to a representative
row; `weights` counts the original periods assigned to each row. Profiles retain
input units. The default selection mode is `legacy`, which uses a global
distance lookup to select profiles. The example explicitly selects
`nearest_centroid` to choose an observed member of each cluster.

## Example and documentation

Run the two-feature example from the repository root:

```sh
python examples/representative_days.py
```

The script prints JSON that other applications can read. A matching
notebook is in `docs/examples/representative_days.ipynb`. For years → days →
hours, see `docs/examples/multiyear_representative_days.ipynb`, which selects
20 days per year and explains calendar mappings, weights, and energy accounting.
Its plots require `matplotlib` in the notebook environment. Documentation uses
Sphinx Book Theme and includes tutorials, examples, API reference, and project
information.

Build the documentation locally:

```sh
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. For the output contract, see
[Clustering](https://github.com/cacodcar/vael/blob/main/docs/CLUSTERING.md).
Quality commands are documented in
[Quality gates](https://github.com/cacodcar/vael/blob/main/docs/QUALITY_GATES.md).

## License and authorship

MIT license, copyright Rahul Kakodkar. Original author credits and numerical
validation records are retained.

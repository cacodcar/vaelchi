![Vaelchi](https://raw.githubusercontent.com/cacodcar/vaelchi/main/docs/_static/vaelchi-logo-light.png)

# Vaelchi

Vaelchi is a **pre-alpha** Python package for time-series analysis, including
preprocessing, clustering, and representative periods. Its API may change in
later releases.

## Installation

Python 3.12 or newer is required.

```sh
python -m pip install vaelchi
```

## Features

- Cluster consecutive periods with adjacency-constrained agglomerative
  hierarchical clustering (AHC).
- Complete timestamped calendars and fill missing values using forward fill,
  backward fill, or time interpolation.
- Select observed representative profiles and retain their original units.
- Export profiles, chronological mappings, weights, and errors as plain data.

## Quick start

```python
from vaelchi import ahc

result = ahc(
    [10, 12, 10, 12, 20, 24, 20, 24],
    periods=2,
    period_length=2,
)
print(result.weights)  # [2 2]
payload = result.to_dict()
chronological_values = result.reconstruct()
```

Each positional input is one feature. Four two-timestep periods become two
representative periods. Profiles retain input units; weights count the original
periods assigned to each representative. The default, `nearest_centroid`,
selects an observed member of each cluster. Pass `selection="legacy"` to
reproduce the Vaelchi 0.1.0 default.

See the [repository and installation guide](https://github.com/cacodcar/vaelchi),
[examples](https://github.com/cacodcar/vaelchi/tree/main/docs/examples), and
[documentation](https://vaelchi.readthedocs.io/en/latest/index.html).
Report problems through [GitHub Issues](https://github.com/cacodcar/vaelchi/issues).

MIT license, copyright Rahul Kakodkar. Original author credits and numerical
validation records are retained.

# Time-series clustering

Vaelchi is a standalone package for clustering aligned numeric time series.
`ahc` and `kmeans` share the `ClusterResult` output contract. AHC continues to
return `AHCResult`, now a subclass of `ClusterResult`; existing imports,
constructor fields/defaults, pickle paths, and dictionary keys are preserved.
Standalone `dtw`, `dtw_matrix`, and `dtw_path` align scalar sequences; they do
not perform clustering. See the [worked examples](tutorials/kmeans_and_dtw.rst).

```python

from vaelchi import ahc

result = ahc([10, 11, 12, 11, 20, 21, 22, 21], periods=2)
reconstructed = result.reconstruct()
payload = result.to_dict()  # JSON-compatible lists/scalars; detached copies.
```

Pass one one-dimensional series per positional argument, all equally long and
aligned. `period_length` is timesteps per period; `parent_length` is original
periods per independent parent. `periods` is representatives per parent.
Features retain argument order. Inputs and outputs are positional: labels are
not timestamps. Callers retain feature names and units outside the result.

## Output contract

| Field | Shape / meaning |
| --- | --- |
| `representatives` | `(representatives, period_length, features)`, original units |
| `labels` | One zero-based representative-row index per original period |
| `representative_indices` | Original zero-based period positions, across all parents |
| `weights` | Original periods assigned to each representative row; sum equals period count |
| `inertia` | Sum of squared distances to actual centroids in standardized space |
| `reconstruction_error` | Sum of squared distances to selected profiles in standardized space |
| `selection` | Representative-selection policy |

`reconstruct()` returns `(original_timesteps, features)` by indexing representative
rows with labels. `to_dict()` preserves the same structure in plain lists and
scalars. A consumer can use `numpy.asarray(payload["representatives"])[payload[
"labels"]]` and flatten the first two axes to reconstruct the original chronology.
Applications can map the columns to their own components and use the weights
when constructing reduced models.

Scaling is per feature/timestep column within each parent. AHC adjacency is
linear, without wraparound. Its default `selection="nearest_centroid"` selects a cluster
member and resolves numerical ties chronologically. Specify `selection="legacy"`
to reproduce the Vaelchi 0.1.0 default. Legacy mode uses a global distance
lookup that can repeat a representative or select outside its cluster. Preserve
all representative rows because labels and weights address them independently.
Both policies select the nearest member for a single cluster.

K-means uses Euclidean Lloyd iterations with k-means++ initialization. It can
group nonadjacent periods and always selects the nearest observed member of
each final cluster. It does not expose the AHC-only `legacy` selection policy.
Both algorithms order nearest-centroid clusters by their earliest member;
k-means representative indices themselves need not be increasing. Labels
retain the mapping to the original chronology.

K-means defaults to `random_state=0`, `n_init=10`, `max_iter=300`, and `tol=1e-4`.
Each parent is fitted independently using the same controls. Repeated calls
are reproducible within the same numerical environment; different dependency
versions/platforms can change clustering. A parent with fewer distinct profiles
than requested clusters raises `ValueError`, rather than returning too few
representatives. Numerical collapse into fewer nonempty clusters also raises.
Inertia uses the means of final memberships even when the iteration limit is
reached. It may then differ from the estimator's last-center inertia.

DTW retains the original Energia absolute-difference local cost. Its distance
is the sum along a complete endpoint-to-endpoint alignment, without scaling,
normalization, or squaring. `DTWResult` contains only `distance` and `path` and
provides a detached JSON-compatible `to_dict()`. Paths are chronological,
zero-based input indices. The lower-level accumulated matrix has an extra
row and column, a zero origin, and infinite remaining boundaries; its padding
is deliberately not part of the JSON result. Exact DTW takes O(n*m) time and
memory for input lengths n and m. This first implementation accepts finite,
nonempty scalar sequences, including different lengths.

The DTW port corrects Energia v1.0.7's free-prefix boundary initialization and
reverse padded-coordinate backtracking. For `[0, 10]` aligned with `[10]`, the
corrected distance is 10, whereas the historical code returned 0. Numerical
ties prefer diagonal, then source-only, then target-only predecessor steps.
The original MIT notice and authorship are retained in the DTW source.

`vaelchi.functions.legacy` provides the historical standalone squared-distance
and connectivity helper APIs, including their edge behavior. The newer helpers
in `vaelchi.functions` remain available. AHC uses its sparse adjacency internally.

## Authorship and historical validation

Original author credits include Rahul Kakodkar and Efstratios N. Pistikopoulos.
Revision identifiers and adaptation credits are recorded in the source files.

The following measurements describe the historical validation snapshot.

- 26 tests passed in Vaelchi's standalone environment.
- AHC, result and legacy helper modules had 100% statement and branch coverage.
- Entire Vaelchi coverage was 90.53% of statements and 88% of branches.
- All functions and classes had Radon A/B complexity, and all modules had
  maintainability rank A.
- 26 exact comparisons to the saved reference implementation covered five
  historical 8,760-hour datasets, 20/35 representatives, both selection modes,
  and six multi-parent, identity, and single-cluster cases. Labels, indices,
  weights, profiles, reconstruction, and both scalar errors matched exactly
  in the same environment.
- Ten comparisons to revision `0604a26e` matched legacy indices, weights, and
  profiles exactly. Nearest-centroid membership and independent SSE checks
  passed with SSE relative tolerance `1e-12`.

Saved evidence is in `validation/ahc/`. The source hashes identify the original
tested snapshots. `historical.json` records reference comparisons, and
`port-parity.json` records the 26 exact comparisons. These reports are historical
evidence and do not replace validation of the current source and dependencies.

Current quality commands and coverage requirements are documented in
`QUALITY_GATES.md`.

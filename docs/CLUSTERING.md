# Time-series clustering

Vaelchi is a standalone package for clustering aligned numeric time series.
`from vaelchi import ahc, AHCResult` is the public API.

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

Scaling is per feature/timestep column within each parent. Adjacency is linear,
without wraparound. The default `selection="legacy"` uses a global distance lookup,
including repeated or out-of-cluster representatives. Do not deduplicate rows:
labels and weights address the selected rows independently. The alternative
`selection="nearest_centroid"` selects a cluster member and resolves numerical
ties chronologically. One-cluster legacy input uses the existing nearest-member
fallback. Defaults, error definitions, and numerical choices are unchanged.

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

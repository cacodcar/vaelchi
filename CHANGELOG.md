# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0 — 2026-11-20

- Add Euclidean k-means for observed representative periods, with independent
  parent groups, reproducible initialization, and shared reconstruction/error
  semantics. Uses the existing scikit-learn dependency.
- Add exact standalone absolute-cost DTW, accumulated matrices, and forward
  zero-based paths. Correct the free-prefix initialization and backtracking
  behavior in the Energia v1.0.7 source, retaining its MIT attribution.
- Add `ClusterResult` for common clustering output and `DTWResult` for
  alignments. Preserve `AHCResult` as a compatible subclass with unchanged
  constructor fields/defaults and dictionary keys.

## 0.1.1 — 2026-11-19

- Default to `selection="nearest_centroid"` so each cluster receives one of
  its own observed periods. Pass `selection="legacy"` to reproduce results
  from calls that omitted `selection` in Vaelchi 0.1.0.

## 0.1.0 — 2026-11-17

- Release Vaelchi as a standalone time-series preprocessing and clustering package.
- Provide calendar-aware missing-value filling for pandas Series and DataFrames,
  with forward fill, backward fill, and time interpolation.
- Add multiyear representative-day examples with chronological mappings and
  weighted energy accounting.

- Align Python quality gates with Gana, including automatic test profiles,
  isolated documentation builds, and checked numerical dependency typing.

- Prepare the first pre-alpha distribution for Python 3.12 and newer.
- Provide adjacency-constrained AHC and framework-independent results.
- Retain the default `legacy` selection policy and original author credits.
- Add a two-feature representative-day script and notebook example.
- Provide Sphinx Book Theme documentation with tutorials and API reference.

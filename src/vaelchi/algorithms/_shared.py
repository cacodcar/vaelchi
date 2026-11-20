"""Shared profile preparation, observed representatives, and result assembly.

Original AHC routines: Rahul Kakodkar and Efstratios N. Pistikopoulos.
OpenAI Codex: extracted without numerical changes from Vaelchi 547cfb9f;
shared assembly supports independent clustering algorithms.
"""

from numbers import Integral

import numpy as np

from vaelchi.result import ClusterResult


def _positive_integer(value: int, name: str) -> int:
    """Require a positive integer while rejecting booleans and fractions."""
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        message = f"{name} must be a positive integer"
        raise ValueError(message)
    return int(value)


def _validated_series(data):
    """Convert aligned input series and reject empty or nonfinite values."""
    if not data:
        message = "provide at least one time series"
        raise ValueError(message)
    series = [np.asarray(values, dtype=float) for values in data]
    if any(values.ndim != 1 or not values.size for values in series):
        message = "each time series must be nonempty and one-dimensional"
        raise ValueError(message)
    if any(len(values) != len(series[0]) for values in series):
        message = "time series must have equal lengths"
        raise ValueError(message)
    if any(not np.isfinite(values).all() for values in series):
        message = "time series must contain only finite values"
        raise ValueError(message)
    return series


def _prepare_profiles(data, periods, period_length, parent_length, selection):
    """Validate aggregation dimensions and build complete parent profiles."""
    periods = _positive_integer(periods, "periods")
    period_length = _positive_integer(period_length, "period_length")
    if selection not in ("nearest_centroid", "legacy"):
        message = "selection must be 'nearest_centroid' or 'legacy'"
        raise ValueError(message)
    series = _validated_series(data)
    if len(series[0]) % period_length:
        message = "time series must contain complete periods"
        raise ValueError(message)
    profiles = np.column_stack(series).reshape(-1, period_length, len(series))
    count = len(profiles)
    parent_length = (
        count
        if parent_length is None
        else _positive_integer(
            parent_length,
            "parent_length",
        )
    )
    if count % parent_length:
        message = "time series must contain complete parent groups"
        raise ValueError(message)
    if periods > parent_length:
        message = "periods cannot exceed the original periods per parent"
        raise ValueError(message)
    return profiles, periods, parent_length


def _representative_statistics(scaled, members, representative):
    """Select the earliest nearest member if needed and compute cluster
    errors."""
    centroid = scaled[members].mean(axis=0)
    distances = ((scaled[members] - centroid) ** 2).sum(axis=1)
    if representative is None:
        # Members are chronological, so the first numerical tie is the
        # earliest.
        tied = np.flatnonzero(
            np.isclose(
                distances,
                distances.min(),
                rtol=1e-12,
                atol=1e-12,
            ),
        )
        representative = members[tied[0]]
    inertia = float(distances.sum())
    reconstruction_error = float(
        ((scaled[members] - scaled[representative]) ** 2).sum(),
    )
    return representative, inertia, reconstruction_error


def _cluster_members(assignments):
    """Order nonempty clusters by their earliest original member."""
    clusters = [
        np.flatnonzero(assignments == label)
        for label in np.unique(assignments)
    ]
    clusters.sort(key=lambda members: members[0])
    return [(members, None) for members in clusters]


def _assemble_result(
    profiles,
    parents,
    *,
    selection,
    result_type=ClusterResult,
):
    """Map parent-local clusters into shared representative-period output.

    Each parent supplies its start position, standardized profiles, and
    (members, optional preset representative) pairs. Summation order matches
    the original AHC implementation, including legacy representative choices.
    """
    labels = np.empty(len(profiles), dtype=np.int64)
    selected: list[int] = []
    weights: list[int] = []
    inertia = reconstruction_error = 0.0
    for start, scaled, choices in parents:
        for members, preset in choices:
            representative, cluster_inertia, cluster_error = (
                _representative_statistics(scaled, members, preset)
            )
            labels[start + members] = len(selected)
            selected.append(start + representative)
            weights.append(len(members))
            inertia += cluster_inertia
            reconstruction_error += cluster_error
    indices = np.asarray(selected, dtype=np.int64)
    return result_type(
        labels=labels,
        representative_indices=indices,
        weights=np.asarray(weights, dtype=np.int64),
        representatives=profiles[indices].copy(),
        inertia=inertia,
        reconstruction_error=reconstruction_error,
        selection=selection,
    )

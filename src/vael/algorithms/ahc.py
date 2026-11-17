"""Chronology-constrained aggregation of aligned time series.

Standardize profiles, apply adjacent-period Ward clustering, and select
observed profiles. Historical reference implementation revision 0604a26e.
Original author: Rahul Kakodkar. Original credits also include
Efstratios N. Pistikopoulos (Multi-parametric Optimization & Control Lab).
"""

from numbers import Integral
from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.sparse import diags
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import StandardScaler

from vael.result import AHCResult


def _positive_integer(value: int, name: str) -> int:
    """Require a positive integer while rejecting booleans and fractions."""
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        message = f"{name} must be a positive integer"
        raise ValueError(message)
    return int(value)


def _legacy_selection(scaled, assignments):
    """Reproduce 0604a26e's centroid labeling and global distance lookup.

    Keep pandas ordering and Python distance summation as in the historical
    code. This compatibility policy deliberately retains its selection quirks;
    error metrics are still calculated from the actual cluster memberships.
    """
    frame = pd.DataFrame(scaled)
    centroids = NearestCentroid().fit(scaled, assignments).centroids_
    frame["cluster_no"] = assignments
    distances = []
    for centroid, label in zip(centroids, frame["cluster_no"].unique()):
        for point in scaled[assignments == label]:
            distances.append(
                sum((a - b) ** 2 for a, b in zip(point, centroid)),
            )
    frame["ED"] = distances
    selected = pd.DataFrame(
        {
            "label": frame["cluster_no"].value_counts().index.values,
        },
    )
    selected["representative"] = [
        int(
            frame.index[
                frame["ED"]
                == frame.loc[
                    frame["cluster_no"] == label,
                    "ED",
                ].min()
            ][0],
        )
        for label in selected["label"]
    ]
    selected = selected.sort_values("representative")
    return [
        (np.flatnonzero(assignments == label), int(representative))
        for label, representative in selected.itertuples(
            index=False,
            name=None,
        )
    ]


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


def _cluster_parent(block, periods, selection):
    """Standardize one parent and cluster with linear temporal adjacency."""
    parent_length = len(block)
    if selection == "legacy":
        # Match historical feature-major arithmetic order as well as values.
        block = block.transpose(0, 2, 1)
    scaled = StandardScaler().fit_transform(block.reshape(parent_length, -1))
    if periods == 1:
        assignments = np.zeros(parent_length, dtype=np.int64)
    elif periods == parent_length and selection != "legacy":
        assignments = np.arange(parent_length)
    else:
        connectivity = diags(
            # Both off-diagonals contain identical unit weights. A single
            # array also expresses SciPy's documented rectangular input.
            np.ones((2, parent_length - 1)),
            offsets=[-1, 1],
            shape=(parent_length, parent_length),
            format="csr",
        )
        assignments = AgglomerativeClustering(
            n_clusters=periods,
            linkage="ward",
            connectivity=connectivity,
            compute_full_tree=True if selection == "legacy" else "auto",
        ).fit_predict(scaled)
    return scaled, assignments


def _cluster_choices(scaled, assignments, periods, selection):
    """Order clusters and supply historical representatives when requested."""
    if selection == "legacy" and periods > 1:
        return _legacy_selection(scaled, assignments)
    # Cluster ids from sklearn are arbitrary; order by first original member.
    cluster_ids = np.unique(assignments)
    clusters = [np.flatnonzero(assignments == c) for c in cluster_ids]
    clusters.sort(key=lambda members: members[0])
    return [(members, None) for members in clusters]


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


def ahc(
    *data: ArrayLike,
    periods: int,
    period_length: int = 1,
    parent_length: int | None = None,
    selection: Literal["nearest_centroid", "legacy"] = "legacy",
) -> AHCResult:
    """Cluster aligned one-dimensional series into representative periods.

    :param data: One or more finite numeric series with equal lengths. Features
        retain their argument order; inputs are aligned positionally.
    :param periods: Number of representative periods **per parent group**.
    :param period_length: Timesteps in each original period, e.g. 24 for days
        sampled hourly. All periods must be complete and equally long.
    :param parent_length: Original periods per independent parent group, e.g.
        365 days per year. Defaults to all periods in one group. All parent
        groups must be complete; clustering never crosses their boundaries.
    :param selection: Defaults to ``legacy``. ``nearest_centroid`` selects
        the nearest cluster member,
        breaking numerical ties with the earliest period. ``legacy`` reproduces
        historical centroid-label association and representative lookup,
        including
        possible repeated or out-of-cluster representatives. Both policies
        retain
        the corrected error metrics. For a single cluster, where the historical
        NearestCentroid call cannot run, use nearest-member selection.

    Each feature/timestep column is standardized across periods within its
    parent group, matching the legacy profile scaling. Ward linkage uses a
    linear adjacency graph (no wraparound). Legacy representative selection is
    the default; nearest-centroid selection is an explicit alternative.
    Inputs are not modified. This function does not construct a reduced model.
    """
    profiles, periods, parent_length = _prepare_profiles(
        data,
        periods,
        period_length,
        parent_length,
        selection,
    )
    count = len(profiles)
    labels = np.empty(count, dtype=np.int64)
    selected: list[int] = []
    weights: list[int] = []
    inertia = reconstruction_error = 0.0
    for start in range(0, count, parent_length):
        # Scaling and clustering stay within each parent's chronological
        # boundary.
        stop = start + parent_length
        scaled, assignments = _cluster_parent(
            profiles[start:stop],
            periods,
            selection,
        )
        choices = _cluster_choices(scaled, assignments, periods, selection)
        for members, preset_representative in choices:
            statistics = _representative_statistics(
                scaled,
                members,
                preset_representative,
            )
            representative, cluster_inertia, cluster_error = statistics
            # Translate parent-local positions into the full input's mapping.
            labels[start + members] = len(selected)
            selected.append(start + representative)
            weights.append(len(members))
            inertia += cluster_inertia
            reconstruction_error += cluster_error

    indices = np.asarray(selected, dtype=np.int64)
    return AHCResult(
        labels=labels,
        representative_indices=indices,
        weights=np.asarray(weights, dtype=np.int64),
        representatives=profiles[indices].copy(),
        inertia=inertia,
        reconstruction_error=reconstruction_error,
        selection=selection,
    )

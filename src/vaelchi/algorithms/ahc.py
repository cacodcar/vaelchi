"""Chronology-constrained aggregation of aligned time series.

Standardize profiles, apply adjacent-period Ward clustering, and select
observed profiles. Historical reference implementation revision 0604a26e.
Original author: Rahul Kakodkar. Original credits also include
Efstratios N. Pistikopoulos (Multi-parametric Optimization & Control Lab).
"""

from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.sparse import diags
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import StandardScaler

from vaelchi.result import AHCResult

from ._shared import _assemble_result, _cluster_members, _prepare_profiles


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
    return _cluster_members(assignments)


# OpenAI Codex: retain parent arithmetic while sharing result assembly.
def _ahc_parents(profiles, periods, parent_length, selection):
    """Yield independent parent clusters without changing legacy ordering."""
    for start in range(0, len(profiles), parent_length):
        stop = start + parent_length
        scaled, assignments = _cluster_parent(
            profiles[start:stop],
            periods,
            selection,
        )
        choices = _cluster_choices(scaled, assignments, periods, selection)
        yield start, scaled, choices


def ahc(
    *data: ArrayLike,
    periods: int,
    period_length: int = 1,
    parent_length: int | None = None,
    selection: Literal["nearest_centroid", "legacy"] = "nearest_centroid",
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
    :param selection: The default, ``nearest_centroid``, selects the nearest
        cluster member, breaking numerical ties with the earliest period.
        Specify ``legacy`` to reproduce the historical representative lookup,
        which can repeat a period or select outside a cluster. Both policies
        use nearest-member selection for a single cluster.

    Each feature/timestep column is standardized across periods within its
    parent group, matching the legacy profile scaling. Ward linkage uses a
    linear adjacency graph (no wraparound).
    Inputs are not modified. This function does not construct a reduced model.
    """
    profiles, periods, parent_length = _prepare_profiles(
        data,
        periods,
        period_length,
        parent_length,
        selection,
    )
    return _assemble_result(
        profiles,
        _ahc_parents(profiles, periods, parent_length, selection),
        selection=selection,
        result_type=AHCResult,
    )

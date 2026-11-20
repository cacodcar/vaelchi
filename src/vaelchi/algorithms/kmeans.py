"""Euclidean k-means with observed representative periods.

OpenAI Codex: adapt scikit-learn's public KMeans API to Vaelchi's shared
profile preparation and result contract. No third-party implementation is
vendored; scikit-learn is already a runtime dependency.
"""

from numbers import Integral, Real

import numpy as np
from numpy.typing import ArrayLike
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from vaelchi.result import ClusterResult

from ._shared import (
    _assemble_result,
    _cluster_members,
    _positive_integer,
    _prepare_profiles,
)


def _random_seed(random_state):
    """Accept an optional NumPy-compatible integer seed, not booleans."""
    if random_state is None:
        return None
    if (
        isinstance(random_state, bool)
        or not isinstance(random_state, Integral)
        or not 0 <= int(random_state) <= int(np.iinfo(np.uint32).max)
    ):
        message = "random_state must be None or an integer from 0 to 2**32-1"
        raise ValueError(message)
    return int(random_state)


def _kmeans_options(random_state, n_init, max_iter, tol):
    """Validate solver controls, including degenerate single-cluster calls."""
    if (
        isinstance(tol, bool)
        or not isinstance(tol, Real)
        or not np.isfinite(float(tol))
        or tol < 0
    ):
        message = "tol must be a finite nonnegative number"
        raise ValueError(message)
    return {
        "random_state": _random_seed(random_state),
        "n_init": _positive_integer(n_init, "n_init"),
        "max_iter": _positive_integer(max_iter, "max_iter"),
        "tol": float(tol),
        "init": "k-means++",
        "algorithm": "lloyd",
    }


def _kmeans_parents(profiles, periods, parent_length, options):
    """Fit each standardized parent independently and order its clusters."""
    for start in range(0, len(profiles), parent_length):
        stop = start + parent_length
        block = profiles[start:stop]
        scaled = StandardScaler().fit_transform(
            block.reshape(parent_length, -1)
        )
        if len(np.unique(scaled, axis=0)) < periods:
            message = (
                "periods cannot exceed the distinct profiles in any parent"
            )
            raise ValueError(message)
        assignments = KMeans(n_clusters=periods, **options).fit_predict(scaled)
        choices = _cluster_members(assignments)
        if len(choices) != periods:
            message = (
                "k-means produced fewer nonempty clusters than periods; "
                "reduce periods or check the input scale"
            )
            raise ValueError(message)
        yield start, scaled, choices


def kmeans(
    *data: ArrayLike,
    periods: int,
    period_length: int = 1,
    parent_length: int | None = None,
    random_state: int | None = 0,
    n_init: int = 10,
    max_iter: int = 300,
    tol: float = 1e-4,
) -> ClusterResult:
    """Cluster aligned series with Euclidean k-means and select real periods.

    :param data: One or more finite, equally long, one-dimensional features.
    :param periods: Number of nonempty clusters per parent. Each parent must
        contain at least this many distinct profiles after standardization.
    :param period_length: Timesteps per complete period, e.g. 24 for days.
    :param parent_length: Original periods per independent parent, e.g. 365
        for years. Defaults to all periods. Partial parents are rejected.
    :param random_state: Integer seed used independently for each parent;
        default 0 gives repeatable calls in the same numerical environment.
        None allows random initialization between calls.
    :param n_init: Positive number of k-means++ starts; the best fit is kept.
    :param max_iter: Positive Lloyd iteration limit per start.
    :param tol: Finite, nonnegative convergence tolerance passed to KMeans.
    :returns: Observed representatives, labels, counts, and squared errors.

    Features retain argument order. Standardization is per feature/timestep
    column within each parent, as in AHC. Clusters may contain nonadjacent
    periods. Each representative is the nearest member to its cluster mean;
    numerical ties select the earliest member. Output rows are ordered by
    each cluster's first member. Inputs are not modified.

    Inertia is recomputed against means of the final memberships, even if
    the iteration limit is reached. Reconstruction error measures distance
    to the selected observed profiles. Both use standardized profile space.

    Examples
    --------
    >>> result = kmeans([0, 10, 0, 10], periods=2)
    >>> result.labels.tolist()
    [0, 1, 0, 1]
    >>> result.weights.tolist()
    [2, 2]
    """
    profiles, periods, parent_length = _prepare_profiles(
        data,
        periods,
        period_length,
        parent_length,
        "nearest_centroid",
    )
    options = _kmeans_options(random_state, n_init, max_iter, tol)
    return _assemble_result(
        profiles,
        _kmeans_parents(profiles, periods, parent_length, options),
        selection="nearest_centroid",
    )

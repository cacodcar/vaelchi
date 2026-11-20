"""OpenAI Codex: verify memberships and independent error accounting."""

import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning

from vaelchi import ClusterResult, kmeans


def test_nonadjacent_clusters_and_observed_profiles():
    """Similar days can cluster across intervening days; inputs stay intact."""
    values = np.array([0, 1, 10, 11, 0, 1, 10, 11], dtype=float)
    original = values.copy()
    result = kmeans(values, values * 2, periods=2, period_length=2)
    np.testing.assert_equal(isinstance(result, ClusterResult), True)
    np.testing.assert_array_equal(result.labels, [0, 1, 0, 1])
    np.testing.assert_array_equal(result.representative_indices, [0, 1])
    np.testing.assert_array_equal(result.weights, [2, 2])
    np.testing.assert_array_equal(
        result.reconstruct(), np.c_[values, values * 2]
    )
    np.testing.assert_array_equal(values, original)
    np.testing.assert_equal(result.inertia, 0)
    np.testing.assert_equal(result.reconstruction_error, 0)


def test_independent_parents_and_chronological_ties():
    """Each parent uses its own scale; nearest-member ties choose the first."""
    result = kmeans([0, 2, 100, 104], periods=1, parent_length=2)
    np.testing.assert_array_equal(result.labels, [0, 0, 1, 1])
    np.testing.assert_array_equal(result.representative_indices, [0, 2])
    np.testing.assert_array_equal(result.weights, [2, 2])
    np.testing.assert_allclose(result.inertia, 4)
    np.testing.assert_allclose(result.reconstruction_error, 8)


@pytest.mark.parametrize("max_iter", [1, 300])
def test_memberships_and_errors_against_independent_accounting(max_iter):
    """Compare sklearn assignments and independently recompute both SSEs."""
    profiles = np.random.default_rng(7).normal(size=(30, 2, 2))
    profiles[:, :, 1] *= 4
    raw = profiles.reshape(30, -1)
    scaled = (raw - raw.mean(axis=0)) / raw.std(axis=0)
    reference = KMeans(
        n_clusters=4,
        n_init=10,
        random_state=0,
        max_iter=max_iter,
        init="k-means++",
        algorithm="lloyd",
    ).fit_predict(scaled)
    result = kmeans(
        *profiles.reshape(-1, 2).T,
        periods=4,
        period_length=2,
        max_iter=max_iter,
    )
    np.testing.assert_array_equal(
        result.labels[:, None] == result.labels,
        reference[:, None] == reference,
    )
    inertia = reconstruction_error = 0.0
    for label, representative in enumerate(result.representative_indices):
        members = np.flatnonzero(result.labels == label)
        np.testing.assert_equal(representative in members, True)
        np.testing.assert_equal(result.weights[label], len(members))
        center = scaled[members].mean(axis=0)
        distances = np.linalg.norm(scaled[members] - center, axis=1) ** 2
        inertia += distances.sum()
        reconstruction_error += (
            np.linalg.norm(scaled[members] - scaled[representative], axis=1)
            ** 2
        ).sum()
        np.testing.assert_allclose(
            np.linalg.norm(scaled[representative] - center) ** 2,
            distances.min(),
        )
    np.testing.assert_allclose(result.inertia, inertia, rtol=1e-12)
    np.testing.assert_allclose(
        result.reconstruction_error,
        reconstruction_error,
        rtol=1e-12,
    )
    np.testing.assert_array_equal(
        result.representatives,
        profiles[result.representative_indices],
    )


def test_repeatability_and_parent_isolation():
    """Adding a later parent cannot alter the earlier parent's clustering."""
    values = np.random.default_rng(8).normal(size=24)
    first = kmeans(values, periods=3, period_length=2, random_state=13)
    again = kmeans(values, periods=3, period_length=2, random_state=13)
    np.testing.assert_equal(first.to_dict(), again.to_dict())
    combined = kmeans(
        np.r_[values, values * 10 + 100],
        periods=3,
        period_length=2,
        parent_length=12,
        random_state=13,
    )
    np.testing.assert_array_equal(combined.labels[:12], first.labels)
    np.testing.assert_array_equal(
        combined.representative_indices[:3],
        first.representative_indices,
    )
    np.testing.assert_equal(
        np.all(combined.labels[12:] >= len(first.weights)),
        True,
    )


@pytest.mark.parametrize(
    "values, periods, indices, weights",
    [
        ([5], 1, [0], [1]),
        ([5, 5, 5], 1, [0], [3]),
        ([2, 4, 8], 3, [0, 1, 2], [1, 1, 1]),
    ],
)
def test_single_constant_and_identity(values, periods, indices, weights):
    """Degenerate valid datasets retain exact profiles and full weights."""
    result = kmeans(values, periods=periods, random_state=None)
    np.testing.assert_array_equal(result.representative_indices, indices)
    np.testing.assert_array_equal(result.weights, weights)
    np.testing.assert_array_equal(result.reconstruct()[:, 0], values)


@pytest.mark.parametrize(
    "data, options",
    [
        ([], {}),
        ([[]], {}),
        ([[1], [1, 2]], {}),
        ([[[1]]], {}),
        ([[np.inf]], {}),
        ([[np.nan]], {}),
        ([[1, 2]], {"periods": 3}),
        ([[1, 2]], {"periods": True}),
        ([[1, 2, 3]], {"period_length": 2}),
        ([[1, 2, 3]], {"parent_length": 2}),
        ([[1, 2]], {"n_init": 0}),
        ([[1, 2]], {"n_init": 1.5}),
        ([[1, 2]], {"max_iter": False}),
        ([[1, 2]], {"max_iter": -1}),
        ([[1, 2]], {"tol": -1}),
        ([[1, 2]], {"tol": np.nan}),
        ([[1, 2]], {"tol": np.inf}),
        ([[1, 2]], {"tol": True}),
        ([[1, 2]], {"tol": "small"}),
        ([[1, 2]], {"random_state": True}),
        ([[1, 2]], {"random_state": -1}),
        ([[1, 2]], {"random_state": 2**32}),
        ([[1, 2]], {"random_state": 0.5}),
    ],
)
def test_invalid_data_and_solver_controls(data, options):
    """Reject invalid profiles and controls, even for a single cluster."""
    with pytest.raises(ValueError):
        kmeans(*data, **{"periods": 1, **options})


def test_insufficient_distinct_profiles_in_later_parent():
    """Never silently return fewer representative periods than requested."""
    with pytest.raises(ValueError, match="distinct profiles"):
        kmeans([0, 1, 2, 5, 5, 5], periods=2, parent_length=3)


def test_numerically_collapsed_clusters_raise():
    """Underflowing squared distances cannot support distinct clusters."""
    with (
        pytest.warns(ConvergenceWarning),
        pytest.raises(
            ValueError,
            match="fewer nonempty clusters",
        ),
    ):
        kmeans([0, 1e-300, 2e-300], periods=2)

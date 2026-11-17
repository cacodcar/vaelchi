"""Behavioral checks for chronology-constrained representative periods.

Ported expectations use NumPy assertions under Vael's lint policy.
"""
#  assertion API adaptation.

import numpy as np
import pytest

from vael import ahc


def test_known_clusters_and_mapping():
    """Known clusters and mapping."""
    demand = np.array([10, 11, 12, 11, 20, 21, 22, 21])
    availability = [0.2, 0.3, 0.4, 0.3, 0.6, 0.7, 0.8, 0.7]
    result = ahc(demand, availability, periods=2, selection="nearest_centroid")
    np.testing.assert_array_equal(result.labels, [0, 0, 0, 0, 1, 1, 1, 1])
    np.testing.assert_array_equal(result.representative_indices, [1, 5])
    np.testing.assert_array_equal(result.weights, [4, 4])
    np.testing.assert_array_equal(
        result.reconstruct()[:, 0],
        [11] * 4 + [21] * 4,
    )
    np.testing.assert_array_equal(demand, [10, 11, 12, 11, 20, 21, 22, 21])


def test_profile_reshape_and_identity():
    """Profile reshape and identity."""
    result = ahc(
        np.arange(12),
        np.arange(12) * 2,
        periods=4,
        period_length=3,
        selection="nearest_centroid",
    )
    np.testing.assert_equal(
        result.representatives.shape == (4, 3, 2),
        True,
    )
    np.testing.assert_array_equal(result.reconstruct()[:, 0], np.arange(12))
    np.testing.assert_array_equal(result.weights, np.ones(4))
    np.testing.assert_equal(
        result.inertia == result.reconstruction_error == 0,
        True,
    )


def test_independent_parents_and_errors():
    # Each parent has standardized values [-1, 1]; earliest wins the tie.
    """Independent parents and errors."""
    result = ahc([0, 2, 100, 104], periods=1, parent_length=2)
    np.testing.assert_array_equal(result.representative_indices, [0, 2])
    np.testing.assert_array_equal(result.labels, [0, 0, 1, 1])
    np.testing.assert_array_equal(result.weights, [2, 2])
    np.testing.assert_equal(
        result.inertia == pytest.approx(4),
        True,
    )
    np.testing.assert_equal(
        result.reconstruction_error == pytest.approx(8),
        True,
    )


def test_constant_and_single_period():
    """Constant and single period."""
    result = ahc([5, 5, 5, 5], periods=1)
    np.testing.assert_array_equal(result.representative_indices, [0])
    np.testing.assert_equal(result.weights[0], 4)
    np.testing.assert_equal(
        result.inertia == result.reconstruction_error == 0,
        True,
    )
    single = ahc([5], periods=1)
    np.testing.assert_equal(
        single.representative_indices[0] == 0,
        True,
    )
    np.testing.assert_equal(
        single.weights[0] == 1,
        True,
    )


def test_contiguity_and_membership():
    # Similar observations separated in time cannot form disconnected clusters.
    """Contiguity and membership."""
    values = [0, 100, 0, 100, 0, 100, 0, 100]
    result = ahc(values, periods=3, selection="nearest_centroid")
    for cluster, representative in enumerate(result.representative_indices):
        members = np.flatnonzero(result.labels == cluster)
        np.testing.assert_equal(
            representative in members,
            True,
        )
        np.testing.assert_equal(
            np.all(np.diff(members) == 1),
            True,
        )
        np.testing.assert_equal(
            result.weights[cluster] == len(members),
            True,
        )
    np.testing.assert_equal(
        result.weights.sum() == len(values),
        True,
    )
    np.testing.assert_equal(
        np.all(np.diff(result.representative_indices) > 0),
        True,
    )


@pytest.mark.parametrize("parents", [1, 2])
def test_legacy_selection_and_corrected_errors(parents):
    # Frozen output of the unchanged 0604a26e historical function: it selects
    # day 2 for BOTH clusters, including its out-of-cluster lookup behavior.
    """Legacy selection and corrected errors."""
    block = np.array([10, 11, 12, 11, 20, 21, 22, 21])
    values = np.concatenate([block + 100 * p for p in range(parents)])
    legacy = ahc(values, periods=2, parent_length=8)
    explicit_legacy = ahc(
        values,
        periods=2,
        parent_length=8,
        selection="legacy",
    )
    np.testing.assert_array_equal(
        legacy.representative_indices,
        explicit_legacy.representative_indices,
    )
    current = ahc(
        values,
        periods=2,
        parent_length=8,
        selection="nearest_centroid",
    )
    np.testing.assert_array_equal(
        legacy.representative_indices,
        [index for p in range(parents) for index in (8 * p + 2, 8 * p + 2)],
    )
    np.testing.assert_array_equal(legacy.labels, current.labels)
    np.testing.assert_array_equal(legacy.weights, [4] * (2 * parents))
    np.testing.assert_array_equal(
        legacy.reconstruct()[:, 0],
        np.concatenate([np.full(8, 12 + 100 * p) for p in range(parents)]),
    )
    np.testing.assert_equal(
        legacy.selection == "legacy",
        True,
    )
    np.testing.assert_equal(
        current.selection == "nearest_centroid",
        True,
    )
    np.testing.assert_equal(
        legacy.inertia == pytest.approx(parents * 4 / 25.5),
        True,
    )
    np.testing.assert_equal(
        legacy.inertia == pytest.approx(current.inertia),
        True,
    )
    np.testing.assert_equal(
        legacy.reconstruction_error == pytest.approx(parents * 332 / 25.5),
        True,
    )


def test_legacy_single_cluster_fallback():
    # Historical NearestCentroid requires multiple classes; the documented
    # extension uses nearest-member selection for one cluster.
    """Legacy single cluster fallback."""
    result = ahc([0, 1, 2], periods=1, selection="legacy")
    np.testing.assert_array_equal(result.representative_indices, [1])
    single = ahc([5], periods=1, selection="legacy")
    np.testing.assert_array_equal(single.representative_indices, [0])
    np.testing.assert_equal(
        single.reconstruction_error == 0,
        True,
    )


@pytest.mark.parametrize(
    "data, kwargs",
    [
        ([], {"periods": 1}),
        ([[]], {"periods": 1}),
        ([[1, 2], [1]], {"periods": 1}),
        ([[float("nan")]], {"periods": 1}),
        ([[float("inf")]], {"periods": 1}),
        ([[[1, 2]]], {"periods": 1}),
        ([[1, 2]], {"periods": 0}),
        ([[1, 2]], {"periods": True}),
        ([[1, 2]], {"periods": 1.5}),
        ([[1, 2]], {"periods": 3}),
        ([[1, 2, 3]], {"periods": 1, "period_length": 2}),
        ([[1, 2]], {"periods": 1, "period_length": 0}),
        ([[1, 2, 3]], {"periods": 1, "parent_length": 2}),
        ([[1, 2]], {"periods": 1, "parent_length": 0}),
        ([[1, 2]], {"periods": 1, "selection": "unknown"}),
    ],
)
def test_invalid_input(data, kwargs):
    """Invalid input."""
    with pytest.raises(ValueError):
        ahc(*data, **kwargs)

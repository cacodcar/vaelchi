"""Check generic output transport and weighted reconstruction semantics."""

import json

import numpy as np
import pytest

from vael import ahc
from vael.functions.legacy import (
    find_euclidean_distance,
    generate_connectivity_matrix,
)


def test_json_export_is_detached_and_reconstructable():
    """A consumer can reconstruct all features from plain JSON."""
    values = np.arange(24, dtype=float)
    result = ahc(
        values,
        values * 2,
        periods=2,
        period_length=3,
        parent_length=4,
        selection="nearest_centroid",
    )
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    representatives = np.asarray(payload["representatives"])
    restored = representatives[payload["labels"]].reshape(-1, 2)
    np.testing.assert_array_equal(restored, result.reconstruct())
    weighted = representatives * np.asarray(payload["weights"])[:, None, None]
    np.testing.assert_array_equal(
        weighted.sum(axis=(0, 1)),
        restored.sum(axis=0),
    )
    payload["labels"][0] = -1
    payload["representatives"][0][0][0] = -999
    np.testing.assert_array_equal(result.labels[0], 0)
    observed = values.reshape(-1, 3)[result.representative_indices]
    np.testing.assert_array_equal(
        result.representatives,
        observed[:, :, None] * [1, 2],
    )


def test_legacy_numeric_helpers():
    """The relocated helper APIs retain distances and endpoint behavior."""
    np.testing.assert_equal(find_euclidean_distance([1, 2], [4, 6]), 25)
    np.testing.assert_array_equal(
        generate_connectivity_matrix(3),
        [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
    )
    np.testing.assert_equal(generate_connectivity_matrix(0).shape, (0, 0))
    with pytest.raises(IndexError):
        generate_connectivity_matrix(1)

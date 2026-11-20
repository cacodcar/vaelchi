"""OpenAI Codex: shared output with AHC constructor compatibility."""

import json
from dataclasses import fields

import numpy as np
import pytest

from vaelchi import AHCResult, ClusterResult, ahc, kmeans


@pytest.mark.parametrize("cluster", [ahc, kmeans])
def test_shared_json_contract_and_weighted_reconstruction(cluster):
    """Consumers use the same keys and axes for either clustering method."""
    values = np.array([1, 2, 10, 12, 2, 3, 11, 13], dtype=float)
    result = cluster(values, values * 2, periods=2, period_length=2)
    np.testing.assert_equal(isinstance(result, ClusterResult), True)
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    np.testing.assert_equal(
        set(payload),
        {
            "labels",
            "representative_indices",
            "weights",
            "representatives",
            "inertia",
            "reconstruction_error",
            "selection",
        },
    )
    profiles = np.asarray(payload["representatives"])
    reconstructed = profiles[payload["labels"]].reshape(-1, 2)
    np.testing.assert_array_equal(reconstructed, result.reconstruct())
    np.testing.assert_allclose(
        (profiles * np.asarray(payload["weights"])[:, None, None]).sum((0, 1)),
        reconstructed.sum(axis=0),
    )
    payload["representatives"][0][0][0] = -999
    np.testing.assert_equal(np.all(result.representatives >= 0), True)


def test_original_ahc_class_and_constructor_default():
    """AHC retains its public type and positional constructor field order."""
    result = ahc([0, 2], periods=1)
    np.testing.assert_equal(type(result), AHCResult)
    names = [field.name for field in fields(AHCResult)]
    np.testing.assert_equal(
        names,
        [
            "labels",
            "representative_indices",
            "weights",
            "representatives",
            "inertia",
            "reconstruction_error",
            "selection",
        ],
    )
    values = [getattr(result, name) for name in names[:-1]]
    historical = AHCResult(*values)
    generic = ClusterResult(*values)
    np.testing.assert_equal(historical.selection, "legacy")
    np.testing.assert_equal(generic.selection, "nearest_centroid")
    np.testing.assert_array_equal(
        historical.reconstruct(), result.reconstruct()
    )

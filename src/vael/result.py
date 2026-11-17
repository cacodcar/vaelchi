"""Framework-independent clustering output in original input units."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class AHCResult:
    """Representative profiles and their mapping to the original periods.

    ``labels`` maps every original period to a row in ``representatives``.
    ``representative_indices`` identifies those periods in the original input.
    ``weights`` counts represented periods, not timesteps or elapsed hours.
    Representatives have shape (clusters, period_length, features) in original
    units. Nearest-centroid selection orders clusters chronologically. Legacy
    selection
    orders by selected period and can select outside a cluster or repeat a
    representative, preserving historical behavior. Errors are sums of squared
    distances in standardized profile
    space: to centroids (``inertia``) and to selected profiles
    (``reconstruction_error``). Each parent is standardized independently.
    """

    labels: NDArray[np.int64]
    representative_indices: NDArray[np.int64]
    weights: NDArray[np.int64]
    representatives: NDArray[np.float64]
    inertia: float
    reconstruction_error: float
    selection: str = "legacy"

    def reconstruct(self) -> NDArray[np.float64]:
        """Expand representatives to (original timesteps, features)."""
        return self.representatives[self.labels].reshape(
            -1,
            self.representatives.shape[-1],
        )

    def to_dict(self) -> dict:
        """Export detached, JSON-compatible values without framework objects.

        Lists retain the array axis order documented on this class. Labels and
        representative indices are zero-based, and weights count periods. The
        consumer retains responsibility for feature names and physical units.
        """
        return {
            "labels": self.labels.tolist(),
            "representative_indices": self.representative_indices.tolist(),
            "weights": self.weights.tolist(),
            "representatives": self.representatives.tolist(),
            "inertia": float(self.inertia),
            "reconstruction_error": float(self.reconstruction_error),
            "selection": self.selection,
        }

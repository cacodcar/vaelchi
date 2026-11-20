"""Framework-independent clustering output in original input units."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


# OpenAI Codex: share the existing output contract across clustering methods.
@dataclass
class ClusterResult:
    """Representative profiles and their mapping to the original periods.

    ``labels`` maps every original period to a row in ``representatives``.
    ``representative_indices`` identifies those periods in the original input.
    ``weights`` counts represented periods, not timesteps or elapsed hours.
    Representatives have shape (clusters, period_length, features) in original
    units. Nearest-centroid selection orders clusters by their first member.
    Members need not be contiguous for algorithms such as k-means. Errors are
    sums of squared distances in standardized profile space: to the means of
    the final cluster memberships (``inertia``) and to selected profiles
    (``reconstruction_error``). Each parent is standardized independently.
    """

    labels: NDArray[np.int64]
    representative_indices: NDArray[np.int64]
    weights: NDArray[np.int64]
    representatives: NDArray[np.float64]
    inertia: float
    reconstruction_error: float
    selection: str = "nearest_centroid"

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


@dataclass
class AHCResult(ClusterResult):
    """Backward-compatible AHC result, also an instance of ClusterResult.

    Preserve the original class name, constructor fields, constructor default,
    pickle import path, and dictionary layout. ``ahc()`` still explicitly
    selects ``nearest_centroid`` by default. Its optional ``legacy`` policy
    can repeat representatives or select outside their clusters, and orders
    clusters by the selected period.
    """

    selection: str = "legacy"


@dataclass
class DTWResult:
    """Absolute-cost alignment of two complete one-dimensional sequences.

    ``distance`` is the sum of absolute differences along ``path``; it is
    neither normalized nor squared. ``path`` has shape (steps, 2), containing
    zero-based source/target indices in chronological order, including both
    sequence endpoints. It is an alignment, not a set of clusters or weights.
    """

    distance: float
    path: NDArray[np.int64]

    def to_dict(self) -> dict:
        """Export a detached, JSON-compatible distance and alignment path."""
        return {"distance": float(self.distance), "path": self.path.tolist()}

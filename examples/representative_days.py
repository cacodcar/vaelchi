"""Cluster six synthetic days and print framework-independent JSON.

Each day contains four six-hour samples of demand and temperature. Keeping the
features separate preserves their order and units in the output. Run this file
from an installed Vael environment.
"""

import json

import numpy as np

from vael import AHCResult, ahc


def representative_days() -> AHCResult:
    """Reduce two groups of three identical days to two observed profiles."""
    demand = np.concatenate(
        [np.tile([10, 12, 14, 10], 3), np.tile([20, 24, 28, 20], 3)],
    )
    temperature = np.concatenate(
        [np.tile([15, 18, 22, 16], 3), np.tile([25, 28, 32, 26], 3)],
    )
    return ahc(
        demand,
        temperature,
        periods=2,
        period_length=4,
        selection="nearest_centroid",
    )


if __name__ == "__main__":
    print(json.dumps(representative_days().to_dict(), indent=2))

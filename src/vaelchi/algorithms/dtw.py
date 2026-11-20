"""Exact, closed-endpoint dynamic time warping of scalar sequences.

Adapted from Energia v1.0.7, revision 0604a26e, aggregation/dtw.py
(module version 1.0.5). Original authors: Rahul Kakodkar and
Efstratios N. Pistikopoulos, Multi-parametric Optimization & Control Lab.
OpenAI Codex: correct boundary initialization and backtracking; add standalone
validation and result APIs. Preserve the original absolute-difference cost.
"""

# MIT License
# Copyright (c) 2023 Rahul Kakodkar, Efstratios N. Pistikopoulos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy as np
from numpy.typing import ArrayLike, NDArray

from vaelchi.result import DTWResult

_MATRIX_DIMENSIONS = 2
_MIN_PADDED_LENGTH = 2


def _sequence(values):
    """Require a nonempty finite scalar sequence; lengths may differ."""
    series = np.asarray(values, dtype=float)
    if series.ndim != 1 or not series.size or not np.isfinite(series).all():
        message = "DTW inputs must be nonempty finite one-dimensional series"
        raise ValueError(message)
    return series


def dtw_matrix(source: ArrayLike, target: ArrayLike) -> NDArray[np.float64]:
    """Return the padded accumulated absolute-cost matrix for full alignment.

    :param source: Nonempty finite one-dimensional source sequence.
    :param target: Nonempty finite one-dimensional target sequence; its length
        can differ from the source.
    :returns: Shape (len(source) + 1, len(target) + 1). The origin is zero;
        the remaining first row and column are positive infinity. Entry
        [i, j] is the minimum cost to align the first i and j observations.

    Both endpoints must participate. Each step advances the source, target,
    or both. Local cost is abs(source[i] - target[j]); there is no scaling,
    length normalization, window constraint, or approximation. Time and memory
    are O(len(source) * len(target)). Unrepresentable accumulated costs raise
    ValueError instead of returning an infinite distance.
    """
    left, right = _sequence(source), _sequence(target)
    matrix = np.full((len(left) + 1, len(right) + 1), np.inf)
    matrix[0, 0] = 0.0
    for i, value in enumerate(left, start=1):
        for j, other in enumerate(right, start=1):
            cost = abs(float(value) - float(other))
            previous = float(
                min(matrix[i - 1, j - 1], matrix[i - 1, j], matrix[i, j - 1]),
            )
            matrix[i, j] = cost + previous
    if not np.isfinite(matrix[1:, 1:]).all():
        message = "DTW accumulated costs exceed finite floating-point range"
        raise ValueError(message)
    return matrix


def _validated_matrix(values):
    """Check the shape and boundary contract of a DTW accumulated matrix."""
    matrix = np.asarray(values, dtype=float)
    if (
        matrix.ndim != _MATRIX_DIMENSIONS
        or min(matrix.shape) < _MIN_PADDED_LENGTH
    ):
        message = "DTW matrix must have two dimensions of at least size 2"
        raise ValueError(message)
    if (
        matrix[0, 0] != 0
        or not np.isposinf(matrix[0, 1:]).all()
        or not np.isposinf(matrix[1:, 0]).all()
    ):
        message = "DTW matrix requires a zero origin and infinite boundaries"
        raise ValueError(message)
    interior = matrix[1:, 1:]
    if not np.isfinite(interior).all() or np.any(interior < 0):
        message = "DTW matrix interior must be finite and nonnegative"
        raise ValueError(message)
    return matrix


def dtw_path(matrix: ArrayLike) -> NDArray[np.int64]:
    """Backtrack a matrix from dtw_matrix into chronological index pairs.

    The path begins at (0, 0) and ends at (n - 1, m - 1), using zero-based
    sequence indices, not the padded matrix coordinates. Ties prefer diagonal,
    then source-only, then target-only steps during backtracking. This returns
    one optimal alignment; the minimizing path need not be unique.

    Supply an accumulated matrix produced by ``dtw_matrix``. Shape, boundaries,
    and finite nonnegative interior values are checked. Local costs cannot be
    verified without the original sequences. The input matrix is not modified.
    """
    values = _validated_matrix(matrix)
    i, j = values.shape[0] - 1, values.shape[1] - 1
    path = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        step = int(
            np.argmin(
                [values[i - 1, j - 1], values[i - 1, j], values[i, j - 1]]
            ),
        )
        di, dj = ((1, 1), (1, 0), (0, 1))[step]
        i, j = i - di, j - dj
    return np.asarray(path[::-1], dtype=np.int64)


def dtw(source: ArrayLike, target: ArrayLike) -> DTWResult:
    """Align two complete scalar sequences and return distance and path.

    Uses exact absolute-cost DTW with O(n*m) time and memory. Inputs must be
    finite, nonempty scalar sequences; unequal lengths are supported. The
    distance is the unnormalized sum of absolute differences along the path.
    See ``dtw_matrix`` and ``dtw_path`` for costs, boundaries, and ties.

    Examples
    --------
    >>> alignment = dtw([0, 10], [10])
    >>> alignment.distance
    10.0
    >>> alignment.path.tolist()
    [[0, 0], [1, 0]]
    """
    matrix = dtw_matrix(source, target)
    return DTWResult(distance=float(matrix[-1, -1]), path=dtw_path(matrix))

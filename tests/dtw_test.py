"""OpenAI Codex: check DTW against exhaustive paths, not another recurrence."""

import json

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from vaelchi import DTWResult, dtw, dtw_matrix, dtw_path


def _paths(i, j):
    """Enumerate legal paths for a tiny independent oracle."""
    if i == j == 0:
        yield [(0, 0)]
        return
    for di, dj in ((1, 1), (1, 0), (0, 1)):
        if i >= di and j >= dj:
            for prefix in _paths(i - di, j - dj):
                yield [*prefix, (i, j)]


@given(
    st.lists(st.integers(-3, 3), min_size=1, max_size=4),
    st.lists(st.integers(-3, 3), min_size=1, max_size=4),
)
def test_global_optimum_and_path_invariants(source, target):
    """The returned path achieves the global minimum over every legal path."""
    expected = min(
        sum(abs(source[i] - target[j]) for i, j in path)
        for path in _paths(len(source) - 1, len(target) - 1)
    )
    result = dtw(source, target)
    np.testing.assert_equal(result.distance, expected)
    np.testing.assert_equal(dtw(target, source).distance, expected)
    np.testing.assert_array_equal(result.path[0], [0, 0])
    np.testing.assert_array_equal(
        result.path[-1],
        [len(source) - 1, len(target) - 1],
    )
    moves = np.diff(result.path, axis=0)
    np.testing.assert_equal(
        all(tuple(move) in {(1, 0), (0, 1), (1, 1)} for move in moves),
        True,
    )
    path_cost = sum(abs(source[i] - target[j]) for i, j in result.path)
    np.testing.assert_equal(path_cost, expected)


@pytest.mark.parametrize(
    "source, target, expected_path",
    [([0, 10], [10], [[0, 0], [1, 0]]), ([10], [0, 10], [[0, 0], [0, 1]])],
)
def test_legacy_free_prefix_regression(source, target, expected_path):
    """Neither sequence can skip leading values or produce negative indices."""
    result = dtw(source, target)
    np.testing.assert_equal(result.distance, 10)
    np.testing.assert_array_equal(result.path, expected_path)


def test_identical_constant_and_shifted_sequences():
    """Diagonal-first ties are stable; repeated samples can have zero cost."""
    identity = dtw([4, 4, 4], [4, 4, 4])
    np.testing.assert_array_equal(identity.path, [[0, 0], [1, 1], [2, 2]])
    np.testing.assert_equal(identity.distance, 0)
    shifted = dtw([0, 1, 0], [0, 0, 1, 0])
    np.testing.assert_equal(shifted.distance, 0)
    np.testing.assert_array_equal(
        shifted.path,
        [[0, 0], [0, 1], [1, 2], [2, 3]],
    )
    np.testing.assert_equal(dtw([-2], [3]).distance, 5)


def test_matrix_boundaries_and_no_input_mutation():
    """The padded matrix exposes accumulated costs with unreachable borders."""
    source = np.array([0.0, 2.0])
    target = np.array([1.0, 2.0])
    matrix = dtw_matrix(source, target)
    np.testing.assert_array_equal(
        matrix,
        [[0, np.inf, np.inf], [np.inf, 1, 3], [np.inf, 2, 1]],
    )
    original = matrix.copy()
    np.testing.assert_array_equal(dtw_path(matrix), [[0, 0], [1, 1]])
    np.testing.assert_array_equal(matrix, original)
    np.testing.assert_array_equal(source, [0, 2])
    np.testing.assert_array_equal(target, [1, 2])


@pytest.mark.parametrize("values", [[], [np.nan], [np.inf], [[1]], 1])
def test_invalid_sequences(values):
    """Validate either sequence without requiring equal lengths."""
    with pytest.raises(ValueError, match="one-dimensional"):
        dtw(values, [1])
    with pytest.raises(ValueError, match="one-dimensional"):
        dtw([1], values)


@pytest.mark.parametrize(
    "matrix",
    [
        [],
        [0, 1],
        [[0]],
        [[0, 0], [0, 1]],
        [[1, np.inf], [np.inf, 0]],
        [[0, -np.inf], [np.inf, 0]],
        [[0, np.inf], [np.inf, np.nan]],
        [[0, np.inf], [np.inf, np.inf]],
        [[0, np.inf], [np.inf, -1]],
    ],
)
def test_invalid_accumulated_matrices(matrix):
    """Reject unpadded, old zero-border, or nonfinite accumulated matrices."""
    with pytest.raises(ValueError):
        dtw_path(matrix)


def test_unrepresentable_costs_raise():
    """Finite input values must not silently produce infinite distances."""
    with pytest.raises(ValueError, match="floating-point range"):
        dtw([1e308], [-1e308])


def test_result_export_is_detached():
    """Alignment JSON excludes the matrix's unreachable infinity padding."""
    result = dtw([1, 2], [2])
    np.testing.assert_equal(isinstance(result, DTWResult), True)
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    np.testing.assert_equal(payload["distance"], 1)
    np.testing.assert_array_equal(payload["path"], [[0, 0], [1, 0]])
    payload["path"][0][0] = 99
    np.testing.assert_array_equal(result.path, [[0, 0], [1, 0]])

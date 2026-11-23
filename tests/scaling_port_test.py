"""Check shared scaling semantics at the public and compatibility imports."""

import numpy as np
import pandas as pd
import pytest

from vaelchi import normalize, scaling
from vaelchi.functions.other import normalize as historical_normalize


@pytest.mark.parametrize(
    "values, method, expected",
    [
        ([(5, 6), (1, 100)], "max", [(0.05, 0.06), (0.01, 1)]),
        ([(5, 6), (1, 100)], "min_max", [(4 / 99, 5 / 99), (0, 1)]),
        ([(5, 5), (5, 5)], "min_max", [(0, 0), (0, 0)]),
        ([-4, 0], "max", [-1, 0]),
        ([0, 0], "max", [0, 0]),
        ([5, 5], "min_max", [0, 0]),
        ([[2, 4], [0, 0]], "max", [[0.5, 1], [0, 0]]),
        ([[2, 4], [5, 7]], "min_max", [[0, 1], [0, 1]]),
        ([], "max", []),
    ],
)
def test_shared_normalization(values, method, expected):
    """Intervals share one scale while nested lists remain independent."""
    np.testing.assert_equal(normalize(values, method), expected)
    np.testing.assert_equal(historical_normalize is normalize, True)


def test_normalization_rejects_ambiguous_input():
    """Reversed endpoints and unknown methods are explicit errors."""
    with pytest.raises(ValueError, match="lower bound"):
        normalize([(5, 2)])
    with pytest.raises(ValueError, match="Unknown"):
        normalize([1, 2], "other")


@pytest.mark.parametrize(
    "method, expected",
    [
        ("max", [[0.5, 1.0], [1.0, 1.0]]),
        ("minmax", [[0.0, 0.0], [1.0, 0.0]]),
        ("standard", [[-1.0, 0.0], [1.0, 0.0]]),
    ],
)
def test_column_scaling_preserves_labels_and_input(method, expected):
    """Column scaling retains timezone-aware coordinates and column names."""
    index = pd.date_range("2024-02-28", periods=2, tz="UTC", name="date")
    columns = pd.Index(["power", "constant"], name="series")
    frame = pd.DataFrame([[2, 5], [4, 5]], index=index, columns=columns)
    original = frame.copy()
    pd.testing.assert_frame_equal(
        scaling(frame, method),
        pd.DataFrame(expected, index=index, columns=columns),
    )
    pd.testing.assert_frame_equal(frame, original)


def test_scaling_handles_zero_maxima_and_missing_values():
    """A zero maximum does not introduce division by zero."""
    frame = pd.DataFrame({"zero": [0, 0], "negative": [-4, 0]})
    expected = pd.DataFrame({"zero": [0.0, 0.0], "negative": [-1.0, 0.0]})
    pd.testing.assert_frame_equal(scaling(frame, "max"), expected)
    frame = pd.DataFrame(
        {1: pd.Series([2, pd.NA], dtype="Int64"), "b": [4, 6]}
    )
    expected = pd.DataFrame({1: [0.0, float("nan")], "b": [0.0, 1.0]})
    pd.testing.assert_frame_equal(scaling(frame, "minmax"), expected)


def test_scaling_retains_validation_errors():
    """The port preserves Energia's public ValueError contract."""
    with pytest.raises(ValueError, match="DataFrame"):
        scaling([1, 2], "max")
    with pytest.raises(ValueError, match="Unknown"):
        scaling(pd.DataFrame({"power": [1, 2]}), "other")

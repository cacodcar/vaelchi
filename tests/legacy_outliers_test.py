"""Preserve the historical outlier filter during its move from Energia."""

import numpy as np
import pandas as pd
import pytest

from vaelchi.functions.legacy import remove_outliers


@pytest.mark.parametrize("spike", [-100.0, 100.0])
def test_interior_outlier_replacement_preserves_axes_and_identity(spike):
    """A single interior spike is replaced in the supplied object."""
    dates = pd.date_range("2020-02-25", periods=10, name="date")
    values = [0.0, 0.0, spike, *([0.0] * 7)]
    frame = pd.DataFrame({"price": values}, index=dates)
    result = remove_outliers(frame)
    np.testing.assert_equal(result is frame, True)
    pd.testing.assert_frame_equal(
        result, pd.DataFrame({"price": [0.0] * 10}, index=dates)
    )


def test_adjacent_outliers_use_earlier_replacements():
    """Thresholds are fixed, but neighbour values change sequentially."""
    frame = pd.DataFrame({"price": [0.0, 0, 40, 60, 0, 0, 0, 0, 0, 0]})
    result = remove_outliers(frame, sd_cuttoff=1)
    np.testing.assert_array_equal(
        result["price"], [0, 0, 30, 15, 0, 0, 0, 0, 0, 0]
    )


def test_only_first_column_selects_rows_for_all_column_replacement():
    """The legacy decision rule does not detect each column independently."""
    frame = pd.DataFrame(
        {
            "price": [0.0, 0, 100, 0, 0, 0, 0, 0, 0, 0],
            "other": [0.0, 2, 8, 4, 0, 1000, 0, 0, 0, 0],
        }
    )
    result = remove_outliers(frame)
    np.testing.assert_array_equal(result.iloc[2], [0, 3])
    np.testing.assert_equal(result["other"].iloc[5], 1000)


@pytest.mark.parametrize("values", [[2.0] * 10, [0.0, 1, 2, 3]])
def test_series_without_outliers_is_unchanged(values):
    """The move preserves constant data and values within the cutoff."""
    frame = pd.DataFrame({"price": values})
    original = frame.copy()
    pd.testing.assert_frame_equal(remove_outliers(frame), original)


def test_larger_window_retains_historical_expression():
    """The compatibility port retains sum / 2 * range, not a window mean."""
    frame = pd.DataFrame({"price": [1.0, 1, 1, 100, 1, 1, 1, 1, 1, 1]})
    np.testing.assert_equal(remove_outliers(frame, mean_range=2).iloc[3, 0], 4)


def test_endpoint_behavior_is_preserved():
    """Negative positions wrap; a missing right neighbour raises."""
    start = pd.DataFrame({"price": [100.0, 2, 0, 0, 0, 0, 0, 0, 0, 4]})
    np.testing.assert_equal(remove_outliers(start).iloc[0, 0], 3)
    end = pd.DataFrame({"price": [0.0] * 9 + [100.0]})
    with pytest.raises(IndexError):
        remove_outliers(end)

"""Behavioral contracts for calendar completion and missing-value policies."""

import numpy as np
import pandas as pd
import pytest

from vael import fill_missing_values


def test_weekend_and_holiday_preserve_observations_and_input():
    """Fill each column independently across a long weekend."""
    index = pd.DatetimeIndex(["2024-05-28", "2024-05-24"], name="date")
    data = pd.DataFrame(
        {"price": [12.0, 10.0], "flow": [4.0, np.nan]},
        index=index,
    )
    original = data.copy(deep=True)
    result = fill_missing_values(data)
    expected = pd.DataFrame(
        {
            "price": [10.0, 10.0, 10.0, 10.0, 12.0],
            "flow": [np.nan] * 4 + [4.0],
        },
        index=pd.date_range("2024-05-24", "2024-05-28", name="date"),
    )
    pd.testing.assert_frame_equal(result, expected)
    pd.testing.assert_frame_equal(data, original)


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("ffill", [np.nan, 2.0, 2.0, 6.0, 6.0]),
        ("bfill", [2.0, 2.0, 6.0, 6.0, np.nan]),
        ("time", [np.nan, 2.0, 4.0, 6.0, np.nan]),
    ],
)
def test_fill_policies_and_calendar_edges(method, expected):
    """Interior NaNs and absent boundary rows obey the selected policy."""
    data = pd.Series(
        [2.0, np.nan, 6.0],
        index=pd.date_range("2024-02-28", periods=3),
        name="x",
    )
    result = fill_missing_values(
        data,
        start="2024-02-27",
        end="2024-03-02",
        method=method,
    )
    pd.testing.assert_series_equal(
        result,
        pd.Series(
            expected,
            index=pd.date_range("2024-02-27", periods=5),
            name="x",
        ),
    )


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("ffill", [0.0, 0.0, np.nan, np.nan, 8.0]),
        ("bfill", [0.0, np.nan, np.nan, 8.0, 8.0]),
        ("time", [0.0, 2.0, np.nan, np.nan, 8.0]),
    ],
)
def test_fill_limits(method, expected):
    """Bound filled calendar rows when several timestamps are absent."""
    data = pd.Series(
        [0.0, 8.0],
        index=pd.to_datetime(["2024-01-01", "2024-01-05"]),
    )
    result = fill_missing_values(data, method=method, limit=np.int64(1))
    np.testing.assert_allclose(result.to_numpy(), expected, equal_nan=True)


def test_timezone_and_elapsed_time_interpolation():
    """DST changes elapsed-time weights but preserves local daily dates."""
    index = pd.date_range(
        "2024-03-09",
        periods=3,
        tz="America/New_York",
        name="local",
    )
    data = pd.Series([0.0, 47.0], index=index[[0, 2]], name="x")
    result = fill_missing_values(
        data,
        method="time",
        start="2024-03-09",
        end="2024-03-11T04:00:00Z",
    )
    pd.testing.assert_series_equal(
        result,
        pd.Series([0.0, 24.0, 47.0], index=index, name="x"),
    )
    hourly = fill_missing_values(data, freq="h")
    np.testing.assert_equal(len(hourly), 48)


@pytest.mark.parametrize("method", ["ffill", "bfill", "time"])
def test_no_borrowing_from_outside_window(method):
    """Isolate the window and leave unobserved windows missing."""
    data = pd.Series(
        [1.0, 9.0],
        index=pd.to_datetime(["2023-12-31", "2024-01-05"]),
    )
    result = fill_missing_values(
        data,
        start="2024-01-01",
        end="2024-01-04",
        method=method,
    )
    pd.testing.assert_series_equal(
        result,
        pd.Series(np.nan, index=pd.date_range("2024-01-01", periods=4)),
    )


def test_all_missing_column_and_existing_nan():
    """Existing missing cells are filled without inventing all-missing data."""
    data = pd.DataFrame(
        {"x": [3.0, np.nan, 7.0], "absent": [np.nan] * 3},
        index=pd.date_range("2024-01-01", periods=3),
    )
    expected = data.copy()
    expected.loc["2024-01-02", "x"] = 3.0
    pd.testing.assert_frame_equal(fill_missing_values(data), expected)


@pytest.mark.parametrize(
    ("data", "error", "match"),
    [
        ([1, 2], TypeError, "Series or DataFrame"),
        (pd.Series([1]), TypeError, "DatetimeIndex"),
        (
            pd.Series([], index=pd.DatetimeIndex([])),
            ValueError,
            "at least one",
        ),
        (
            pd.Series([1, 2], index=pd.to_datetime(["2024-01-01"] * 2)),
            ValueError,
            "unique",
        ),
        (pd.Series([1], index=pd.DatetimeIndex([pd.NaT])), ValueError, "NaT"),
    ],
)
def test_invalid_input(data, error, match):
    """Ambiguous timestamps and non-time-series input fail explicitly."""
    with pytest.raises(error, match=match):
        fill_missing_values(data)


@pytest.mark.parametrize(
    ("options", "match"),
    [
        ({"method": "nearest"}, "method"),
        ({"limit": 0}, "limit"),
        ({"limit": -1}, "limit"),
        ({"limit": True}, "limit"),
        ({"limit": 1.5}, "limit"),
        ({"start": "NaT"}, "NaT"),
        ({"start": "2024-01-03"}, "start"),
        ({"start": "2024-01-01T00:00:00Z"}, "timezone-aware"),
        ({"freq": "-1D"}, "advance"),
        ({"freq": "0D"}, "advance"),
        ({"freq": "not_a_frequency"}, "Invalid frequency"),
        ({"freq": "2D"}, "align"),
    ],
)
def test_invalid_options(options, match):
    """Invalid policies and grids cannot silently discard observations."""
    data = pd.Series([1.0, 2.0], index=pd.date_range("2024-01-01", periods=2))
    with pytest.raises(ValueError, match=match):
        fill_missing_values(data, **options)

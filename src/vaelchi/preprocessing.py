"""Calendar-aware preparation of general timestamped time series."""

from numbers import Integral
from typing import Literal, TypeVar

import pandas as pd

TimeData = TypeVar("TimeData", pd.Series, pd.DataFrame)
FillMethod = Literal["ffill", "bfill", "time"]


def _validate_data(data: TimeData) -> TimeData:
    """Validate timestamps and return a sorted independent object."""
    if not isinstance(data, (pd.Series, pd.DataFrame)):
        message = "data must be a pandas Series or DataFrame"
        raise TypeError(message)
    if not isinstance(data.index, pd.DatetimeIndex):
        message = "data must have a DatetimeIndex"
        raise TypeError(message)
    if data.empty:
        message = "data must contain at least one observation"
        raise ValueError(message)
    if data.index.hasnans or not data.index.is_unique:
        message = "timestamps must be unique and must not contain NaT"
        raise ValueError(message)
    return data.sort_index().copy()


def _validate_options(method: FillMethod, limit: int | None) -> None:
    """Reject unknown policies and invalid consecutive-missing-row limits."""
    if method not in ("ffill", "bfill", "time"):
        message = "method must be 'ffill', 'bfill', or 'time'"
        raise ValueError(message)
    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, Integral) or limit < 1
    ):
        message = "limit must be a positive integer or None"
        raise ValueError(message)


def _boundary(
    value: str | pd.Timestamp | None,
    default: pd.Timestamp,
) -> pd.Timestamp:
    """Interpret naive bounds in the data's timezone; retain aware times."""
    if value is None:
        return default
    stamp = pd.Timestamp(value)
    if pd.isna(stamp):
        message = "calendar bounds must not be NaT"
        raise ValueError(message)
    if default.tz is None:
        if stamp.tz is not None:
            message = "timezone-aware bounds require timezone-aware data"
            raise ValueError(message)
        return stamp
    if stamp.tz is None:
        return stamp.tz_localize(default.tz)
    return stamp.tz_convert(default.tz)


def _calendar_window(
    data: TimeData,
    freq: str,
    start: str | pd.Timestamp | None,
    end: str | pd.Timestamp | None,
) -> TimeData:
    """Complete the requested grid without silently dropping off-grid rows."""
    lower = _boundary(start, data.index[0])
    upper = _boundary(end, data.index[-1])
    if lower > upper:
        message = "start must not be after end"
        raise ValueError(message)
    offset = pd.tseries.frequencies.to_offset(freq)
    if offset.n <= 0:
        message = "freq must advance time"
        raise ValueError(message)
    calendar = pd.date_range(lower, upper, freq=offset, name=data.index.name)
    window = data.loc[(data.index >= lower) & (data.index <= upper)]
    if not window.index.isin(calendar).all():
        message = "observations do not align with the requested calendar"
        raise ValueError(message)
    return window.reindex(calendar)


def fill_missing_values(
    data: TimeData,
    *,
    freq: str = "D",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    method: FillMethod = "ffill",
    limit: int | None = None,
) -> TimeData:
    """Complete a calendar and fill absent rows and existing missing values.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame
        Observations with a unique DatetimeIndex. Values and column names
        have no domain-specific meaning; no unit conversion is performed.
    freq : str, default "D"
        Positive pandas calendar frequency. Use "D" to include weekends and
        holidays, or "h" for an hourly grid. This is not an aggregation tool:
        off-grid observations within the requested window are rejected.
    start, end : str or pandas.Timestamp, optional
        Inclusive calendar bounds, defaulting to the first and last input
        timestamps. Only observations within these bounds can supply values.
        Naive bounds use the data's timezone. Leap days follow the calendar.
    method : {"ffill", "bfill", "time"}, default "ffill"
        Carry the previous observation forward, use the next observation,
        or interpolate numeric values by elapsed time between observations.
        Forward fill leaves leading gaps missing; backward fill leaves
        trailing gaps missing. Time interpolation fills interior gaps only.
        Backward fill and interpolation explicitly use future observations.
    limit : int, optional
        Maximum consecutive missing calendar rows filled per column. For
        interpolation, pandas applies this limit in the forward direction.

    Returns
    -------
    pandas.Series or pandas.DataFrame
        A new object with the same container type, names and timezone, sorted
        onto the requested grid. Observed nonmissing values are preserved.
        Dtypes may change when missing values are introduced. The input is
        unchanged; unresolved gaps remain missing, including all-missing
        columns and windows containing no observations.

    Notes
    -----
    No holiday database is needed: the policy applies to all missing grid
    values, regardless of whether the cause was a weekend, holiday or outage.
    It does not infer whether filling a particular gap is physically valid.
    """
    _validate_options(method, limit)
    ordered = _validate_data(data)
    aligned = _calendar_window(ordered, freq, start, end)
    count = None if limit is None else int(limit)
    if method == "ffill":
        return aligned.ffill(limit=count)
    if method == "bfill":
        return aligned.bfill(limit=count)
    return aligned.interpolate(method="time", limit=count, limit_area="inside")

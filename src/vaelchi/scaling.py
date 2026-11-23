"""Shared scaling of time-series values and DataFrame columns.

Ported from TAMUparametric/energiapy f288bd46 (MIT).
"""

from itertools import batched
from typing import Literal

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def scaling(
    data: DataFrame, how: Literal["max", "minmax", "standard"]
) -> DataFrame:
    """
    Scale each DataFrame column independently and retain both axes.

    Max scaling divides by the column maximum, using the largest magnitude
    when the maximum is zero. All-zero columns remain zero.

    :param data: Input DataFrame.
    :param how: Scaling method, one of ``max``, ``minmax``, or ``standard``.
    :return: Scaled DataFrame with the input index and column labels.
    :raises ValueError: For non-DataFrame input or an unknown method.

    .. admonition:: Example

        .. code-block:: python

            from pandas import DataFrame
            from vaelchi import scaling

            demand = DataFrame({"heat": [0, 8], "power": [2, 4]})
            scaled = scaling(demand, how="max")
            assert scaled["heat"].tolist() == [0.0, 1.0]
            assert scaled["power"].tolist() == [0.5, 1.0]
    """
    if not isinstance(data, DataFrame):
        message = "please provide DataFrame"
        raise ValueError(message)  # noqa: TRY004 -- preserve Energia's API

    if how == "max":
        maxima = data.max()
        divisors = maxima.mask(maxima == 0, data.min().abs()).replace(0, 1)
        return data / divisors

    scaler: MinMaxScaler | StandardScaler
    if how == "minmax":
        scaler = MinMaxScaler()
    elif how == "standard":
        scaler = StandardScaler()
    else:
        message = f"Unknown scaling method {how!r}"
        raise ValueError(message)
    values = scaler.fit_transform(data.to_numpy(na_value=float("nan")))
    return DataFrame(values, index=data.index, columns=data.columns)


def normalize(data: list, how: str = "max") -> list:
    """
    Normalize a series of values or (lower, upper) intervals.

    The ``max`` method divides by the series maximum. If the maximum is
    zero, it uses the largest magnitude, leaving an all-zero series at zero.
    The ``min_max`` method maps the extrema to 0 and 1, or a constant to 0.
    Interval endpoints share one scale. Nested lists are independent series.

    :param data: Time-series values or (lower, upper) pairs.
    :param how: Normalization method, either ``max`` or ``min_max``.
    :return: Normalized values in the same grouping as the input.
    :raises ValueError: For an unknown method or reversed interval bounds.

    .. admonition:: Example

        .. code-block:: python

            from vaelchi import normalize

            prices = [(2, 4), (6, 8)]
            assert normalize(prices, how="max") == [(0.25, 0.5), (0.75, 1.0)]
    """
    if how not in ("max", "min_max"):
        message = f"Unknown normalization method {how!r}"
        raise ValueError(message)
    if len(data) == 0:
        return []
    first = next(iter(data))
    if isinstance(first, list):
        return [normalize(series, how) for series in data]
    if isinstance(first, tuple):
        return _normalize_intervals(data, how)

    offset = min(data) if how == "min_max" else 0
    divisor = max(data) - offset
    if divisor == 0:
        divisor = abs(min(data) - offset) or 1
    return [(value - offset) / divisor for value in data]


def _normalize_intervals(data: list, how: str) -> list:
    """Use one scale for all lower and upper interval endpoints."""
    if any(lower > upper for lower, upper in data):
        message = "The lower bound must not exceed the upper bound"
        raise ValueError(message)
    endpoints = [value for interval in data for value in interval]
    scaled = normalize(endpoints, how)
    return [(min(pair), max(pair)) for pair in batched(scaled, 2)]

"""NSRDB site selection and temporal averaging.

Ported from TAMUparametric/energiapy f288bd46 (MIT).
"""

import logging
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

logger = logging.getLogger("vaelchi")


def _county_site(meta: pd.DataFrame, state: str, county: str, get: str):
    """Select the first site matching the county's requested extreme."""
    sites = meta.loc[
        (meta["state"] == state.encode()) & (meta["county"] == county.encode())
    ]
    direction, metric = get.split("-", maxsplit=1)
    if direction not in ("min", "max"):
        message = "get must begin with 'min-' or 'max-'"
        raise ValueError(message)
    values = sites[metric]
    extreme = values.min() if direction == "min" else values.max()
    chosen = sites.loc[values == extreme].iloc[0]
    latitude, longitude = float(chosen["latitude"]), float(chosen["longitude"])
    matching = sites.loc[
        (sites["latitude"] == latitude) & (sites["longitude"] == longitude)
    ]
    return matching.index[0], (latitude, longitude)


def _average_attributes(source, attrs: list[str], idx, resolution: str):
    """Average consecutive half-hourly records and apply source scales."""
    step = {"halfhourly": 1, "hourly": 2, "daily": 48}[resolution]
    times = pd.to_datetime(source["time_index"][...].astype(str))
    result = pd.DataFrame()
    for attr in attrs:
        dataset = source[attr]
        values = dataset[:, idx]
        result[attr] = np.average(values.reshape(-1, step), axis=1)
    result = result.set_index(times[::step])
    for attr in attrs:
        result[attr] = result[attr] / source[attr].attrs["psm_scale_factor"]
    return result


def fetch_nsrdb_data(  # noqa: PLR0917 -- preserve Energia's positional API
    attrs: list[str],
    year: int,
    lat_lon: tuple[float, float] | None = None,
    state: str = "",
    county: str = "",
    resolution: str = "",
    get: str = "max-population",
    save: str | None = None,
) -> tuple[tuple[float, float], pd.DataFrame] | None:
    """Fetch and average NSRDB observations for one site.

    Install ``vaelchi[nsrdb]`` and configure h5pyd access to NREL's HSDS
    service before fetching. The optional dependency is loaded only on call;
    if it is absent, log a warning and return None, as in Energia.

    ``attrs`` names NSRDB datasets and ``year`` selects the source year.
    ``lat_lon`` selects the nearest site using Euclidean coordinate distance.
    Otherwise, capitalized ``state`` and ``county`` select a county and
    ``get`` chooses its first site at a min/max population, elevation or
    landcover value, for example ``max-population``.

    Supply ``resolution="halfhourly"``, ``"hourly"`` or ``"daily"``.
    Consecutive groups of 1, 2 or 48 source rows are averaged, then divided
    by each dataset's ``psm_scale_factor``. The first timestamp labels each
    group. The legacy empty default is retained and is not a valid resolution.

    Return ``(coordinates, data)``. Coordinates are the requested pair for
    nearest-site selection and the selected site's pair for county selection.
    If ``save`` is supplied, write the DataFrame to ``save + ".csv"``.
    Remote access and malformed source-data errors propagate to the caller.
    """
    try:
        h5pyd = import_module("h5pyd")
    except ModuleNotFoundError as error:
        if error.name != "h5pyd":
            raise
        logger.warning("Install h5pyd or vaelchi[nsrdb] to fetch NSRDB data.")
        return None

    with h5pyd.File(f"/nrel/nsrdb/v3/nsrdb_{year}.h5", "r") as source:
        if lat_lon is None:
            idx, lat_lon = _county_site(
                pd.DataFrame(source["meta"][...]), state, county, get
            )
        else:
            tree = cKDTree(source["coordinates"][...])
            idx = tree.query(np.array(lat_lon))[1]
        result = _average_attributes(source, attrs, idx, resolution)
    if save is not None:
        result.to_csv(save + ".csv")
    return lat_lon, result

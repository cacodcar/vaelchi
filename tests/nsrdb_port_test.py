"""Verify NSRDB selection, averaging and optional access without a network."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from vaelchi import fetch_nsrdb_data, nsrdb


class Dataset:
    """Supply the dataset interface used by the NSRDB adapter."""

    def __init__(self, values, scale=1):
        self.values = values
        self.attrs = {"psm_scale_factor": scale}

    def __getitem__(self, key):
        return self.values[key]


class Source(dict):
    """Record closure of an in-memory NSRDB file."""

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, *args):
        self.closed = True


@pytest.fixture
def source(monkeypatch):
    """Two Texas sites and one out-of-state site over a leap day."""
    times = pd.date_range("2024-02-28", periods=96, freq="30min", tz="UTC")
    values = np.arange(288, dtype=float).reshape(96, 3)
    meta = np.array(
        [
            (b"Texas", b"Harris", 30.0, -95.0, 10, 50, 1),
            (b"Texas", b"Harris", 31.0, -96.0, 20, 40, 2),
            (b"Ohio", b"Harris", 40.0, -80.0, 100, 100, 3),
        ],
        dtype=[
            ("state", "S10"),
            ("county", "S10"),
            ("latitude", float),
            ("longitude", float),
            ("population", int),
            ("elevation", int),
            ("landcover", int),
        ],
    )
    data = Source(
        time_index=Dataset(np.array(times.astype(str), dtype="S40")),
        coordinates=Dataset(np.array([[30, -95], [31, -96], [40, -80]])),
        meta=Dataset(meta),
        dni=Dataset(values, scale=10),
        temperature=Dataset(values + 100, scale=100),
    )

    def open_file(path, mode):
        np.testing.assert_equal(path, "/nrel/nsrdb/v3/nsrdb_2024.h5")
        np.testing.assert_equal(mode, "r")
        return data

    monkeypatch.setattr(
        nsrdb, "import_module", lambda _name: SimpleNamespace(File=open_file)
    )
    return data


@pytest.mark.parametrize(
    "resolution, step", [("halfhourly", 1), ("hourly", 2), ("daily", 48)]
)
def test_nearest_site_scaling_and_time_labels(source, resolution, step):
    """Use source scale factors after averaging each attribute's rows."""
    requested = (30.9, -96.1)
    coordinates, result = fetch_nsrdb_data(
        ["dni", "temperature"], 2024, lat_lon=requested, resolution=resolution
    )
    expected = pd.DataFrame(
        {
            name: source[name][:, 1].reshape(-1, step).mean(axis=1) / scale
            for name, scale in [("dni", 10), ("temperature", 100)]
        },
        index=pd.to_datetime(source["time_index"][...].astype(str))[::step],
    )
    np.testing.assert_equal(coordinates, requested)
    pd.testing.assert_frame_equal(result, expected)
    np.testing.assert_equal(source.closed, True)


@pytest.mark.parametrize(
    "selection, idx",
    [
        ("min-population", 0),
        ("max-population", 1),
        ("min-elevation", 1),
        ("max-elevation", 0),
        ("min-landcover", 0),
        ("max-landcover", 1),
    ],
)
def test_county_selection_and_csv_export(source, tmp_path, selection, idx):
    """County filtering excludes larger values from a different state."""
    destination = str(tmp_path / "weather")
    coordinates, result = fetch_nsrdb_data(
        ["dni"],
        2024,
        state="Texas",
        county="Harris",
        resolution="hourly",
        get=selection,
        save=destination,
    )
    np.testing.assert_equal(coordinates, tuple(source["coordinates"][idx]))
    np.testing.assert_array_equal(
        result["dni"], source["dni"][:, idx].reshape(-1, 2).mean(axis=1) / 10
    )
    restored = pd.read_csv(destination + ".csv", index_col=0, parse_dates=True)
    pd.testing.assert_frame_equal(result, restored)


def test_source_closes_on_invalid_resolution_and_selection(source):
    """The inherited empty resolution still fails; the file is closed."""
    with pytest.raises(KeyError):
        fetch_nsrdb_data(["dni"], 2024, lat_lon=(30, -95))
    np.testing.assert_equal(source.closed, True)
    with pytest.raises(ValueError, match="get must begin"):
        fetch_nsrdb_data(
            ["dni"],
            2024,
            state="Texas",
            county="Harris",
            get="mean-population",
        )


def test_optional_dependency_is_loaded_only_when_fetching(monkeypatch, caplog):
    """Missing h5pyd is optional; a broken installed dependency propagates."""

    def missing(name):
        raise ModuleNotFoundError(name=name)

    monkeypatch.setattr(nsrdb, "import_module", missing)
    np.testing.assert_equal(fetch_nsrdb_data(["dni"], 2024), None)
    np.testing.assert_equal("vaelchi[nsrdb]" in caplog.text, True)

    def broken(name):
        raise ModuleNotFoundError(name="dependency_of_h5pyd")

    monkeypatch.setattr(nsrdb, "import_module", broken)
    with pytest.raises(ModuleNotFoundError):
        fetch_nsrdb_data(["dni"], 2024)

from pathlib import Path
import numpy as np
import pytest
from PyStemmusScope import forcing_io
from PyStemmusScope.global_data import utils
from . import data_folder


GLOBAL_DATA_FOLDER = Path(data_folder / "directories" / "global")
TEST_LAT = 37.933804  # Same as XX-Xxx
TEST_LON = -107.807526
START_TIME = np.datetime64("1996-01-01T00:00")
END_TIME = np.datetime64("1996-01-01T12:00")
TIMESTEP = "1800S"


def test_get_filename_canopy_height():
    fname = utils.get_filename_canopy_height(lat=52, lon=4)
    assert fname == "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif"

    fname = utils.get_filename_canopy_height(lat=-33.45, lon=-70.66)
    assert fname == "ETH_GlobalCanopyHeight_10m_2020_S36W072_Map.tif"


def test_get_filename_dem():
    fname = utils.get_filename_dem(lat=52, lon=4)
    assert fname == "Copernicus_DSM_30_N52_00_E004_00_DEM.tif"

    fname = utils.get_filename_dem(lat=-33.45, lon=-70.66)
    assert fname == "Copernicus_DSM_30_S34_00_W071_00_DEM.tif"


@pytest.fixture(scope="module")
def get_forcing_data():
    return forcing_io.read_forcing_data_global(
        global_data_dir=GLOBAL_DATA_FOLDER,
        lat=TEST_LAT,
        lon=TEST_LON,
        start_time=START_TIME,
        end_time=END_TIME,
        timestep=TIMESTEP,
    )


expected_keys_values = [
    ("wind_speed", (1**2 + 2**2) ** 0.5),
    ("t_air_celcius", 10),
    ("precip_conv", 3 / 10),
    ("psurf_hpa", 1e3),
    ("sw_down", 5 / 3600),
    ("lw_down", 6 / 3600),
    ("ea", 8.7227139),
    ("vpd", 3.5562065),
    ("rh", 71.0381175),
    ("Qair", 0.0054255),
    ("co2_conv", 15504000.0),
    ("lai", 4.0),
    ("elevation", 111.0),
    ("canopy_height", 1.0),
    ("reference_height", 10.0),
    ("doy_float", 0.0),
]


@pytest.mark.parametrize("key, val", expected_keys_values)
def test_extract_forcing_data(get_forcing_data, key, val):
    ds = get_forcing_data
    assert key in ds.keys()
    np.testing.assert_almost_equal(
        np.array([val]), ds[key][0] if hasattr(ds[key], "__iter__") else ds[key]
    )

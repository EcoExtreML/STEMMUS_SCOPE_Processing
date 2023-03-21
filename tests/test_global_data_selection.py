from pathlib import Path
from unittest import mock
import numpy as np
import PyStemmusScope.global_data as gd
import pytest
from PyStemmusScope import forcing_io
from . import data_folder


GLOBAL_DATA_FOLDER = Path(data_folder / "directories" / "global")
TEST_LAT = 37.933804  # Same as XX-Xxx
TEST_LON = -107.807526
START_TIME = np.datetime64("1996-01-01T00:00")
END_TIME = np.datetime64("1996-01-01T12:00")
TIMESTEP = "1800S"


def test_get_filename_canopy_height():
    fname = gd.eth_canopy_height.get_filename_canopy_height(lat=52, lon=4)
    assert fname == "ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif"

    fname = gd.eth_canopy_height.get_filename_canopy_height(lat=-33.45, lon=-70.66)
    assert fname == "ETH_GlobalCanopyHeight_10m_2020_S36W072_Map.tif"


def test_get_filename_dem():
    fname = gd.prism_dem.get_filename_dem(lat=52, lon=4)
    assert fname == "Copernicus_DSM_30_N52_00_E004_00_DEM.tif"

    fname = gd.prism_dem.get_filename_dem(lat=-33.45, lon=-70.66)
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


class TestEra5:
    def test_era5_missing_data(self):
        with pytest.raises(
            FileNotFoundError, match="No netCDF files found in the folder"
        ):
            gd.era5.retrieve_era5_data(
                global_data_dir=GLOBAL_DATA_FOLDER / "false",
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @mock.patch("PyStemmusScope.global_data.era5.RESOLUTION_ERA5", 0.0)
    def test_era5_no_nearby_datapoint(self):
        with pytest.raises(
            gd.utils.MissingDataError, match="No data point was found within"
        ):
            gd.era5.retrieve_era5_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @pytest.mark.parametrize("latlon", [(0, TEST_LON), (TEST_LAT, 0)])
    def test_era5_out_of_bounds_loc(self, latlon):
        with pytest.raises(
            gd.utils.MissingDataError, match="data does not cover the given location"
        ):
            gd.era5.retrieve_era5_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=latlon,
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    dummy_timeranges = [
        (np.datetime64("1980-01-01"), END_TIME),
        (START_TIME, np.datetime64("2020-01-01")),
    ]

    @pytest.mark.parametrize("time_range", dummy_timeranges)
    def test_era5_out_of_bounds_time(self, time_range):
        with pytest.raises(
            gd.utils.MissingDataError,
            match="data does not cover the given start and end time",
        ):
            gd.era5.retrieve_era5_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=time_range,
                timestep=TIMESTEP,
            )


class TestCams:
    def test_missing_data(self):
        with pytest.raises(
            FileNotFoundError, match="No netCDF files found in the folder"
        ):
            gd.cams_co2.retrieve_co2_data(
                global_data_dir=GLOBAL_DATA_FOLDER / "false",
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @mock.patch("PyStemmusScope.global_data.cams_co2.RESOLUTION_CAMS", 0.0)
    def test_no_nearby_datapoint(self):
        with pytest.raises(
            gd.utils.MissingDataError, match="No data point was found within"
        ):
            gd.cams_co2.retrieve_co2_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @pytest.mark.parametrize("latlon", [(0, TEST_LON), (TEST_LAT, 0)])
    def test_out_of_bounds_loc(self, latlon):
        with pytest.raises(
            gd.utils.MissingDataError,
            match="The CO2 data does not cover the given location.",
        ):
            gd.cams_co2.retrieve_co2_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=latlon,
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    dummy_timeranges = [
        (np.datetime64("1980-01-01"), END_TIME),
        (START_TIME, np.datetime64("2020-01-01")),
    ]

    @pytest.mark.parametrize("time_range", dummy_timeranges)
    def test_out_of_bounds_time(self, time_range):
        with pytest.raises(
            gd.utils.MissingDataError,
            match="The CO2 data does not cover the given start and end time",
        ):
            gd.cams_co2.retrieve_co2_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=time_range,
                timestep=TIMESTEP,
            )


class TestLAI:
    def test_missing_data(self):
        with pytest.raises(
            FileNotFoundError, match="No netCDF files found in the folder"
        ):
            gd.copernicus_lai.retrieve_lai_data(
                global_data_dir=GLOBAL_DATA_FOLDER / "false",
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @mock.patch("PyStemmusScope.global_data.copernicus_lai.RESOLUTION_LAI", 0.0)
    def test_no_nearby_datapoint(self):
        with pytest.raises(
            gd.utils.MissingDataError, match="No data point was found within"
        ):
            gd.copernicus_lai.retrieve_lai_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    @pytest.mark.parametrize("latlon", [(0, TEST_LON), (TEST_LAT, 0)])
    def test_out_of_bounds_loc(self, latlon):
        with pytest.raises(
            gd.utils.MissingDataError,
            match="The LAI data does not cover the given location.",
        ):
            gd.copernicus_lai.retrieve_lai_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=latlon,
                time_range=(START_TIME, END_TIME),
                timestep=TIMESTEP,
            )

    dummy_timeranges = [
        (np.datetime64("1980-01-01"), END_TIME),
        (START_TIME, np.datetime64("2020-01-01")),
    ]

    @pytest.mark.parametrize("time_range", dummy_timeranges)
    def test_out_of_bounds_time(self, time_range):
        with pytest.raises(
            gd.utils.MissingDataError,
            match="The LAI data does not cover the given start and end time",
        ):
            gd.copernicus_lai.retrieve_lai_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                latlon=(TEST_LAT, TEST_LON),
                time_range=time_range,
                timestep=TIMESTEP,
            )


class TestCanopyHeight:
    def test_missing_tile(self):
        with pytest.raises(
            gd.utils.InvalidLocationError, match="No canopy height data tile exists"
        ):
            gd.eth_canopy_height.retrieve_canopy_height_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=0,
                lon=0,  # "null" island: is ocean.
            )

    def test_missing_file(self):
        with pytest.raises(
            FileNotFoundError, match="Could not find a file with the name"
        ):
            gd.eth_canopy_height.retrieve_canopy_height_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=52,
                lon=4,
            )

    @mock.patch("PyStemmusScope.global_data.eth_canopy_height.MAX_DISTANCE", 0.0)
    def test_no_nearby_data(self):
        with pytest.raises(
            gd.utils.MissingDataError, match="No valid canopy height data found within"
        ):
            gd.eth_canopy_height.retrieve_canopy_height_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=TEST_LAT,
                lon=TEST_LON,
            )


class TestDEM:
    def test_missing_tile(self):
        with pytest.raises(
            gd.utils.InvalidLocationError, match="No DEM data tile exists"
        ):
            gd.prism_dem.retrieve_dem_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=0,
                lon=0,  # "null" island: is ocean.
            )

    def test_missing_file(self):
        with pytest.raises(
            FileNotFoundError, match="Could not find a file with the name"
        ):
            gd.prism_dem.retrieve_dem_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=52,
                lon=4,
            )

    @mock.patch("PyStemmusScope.global_data.prism_dem.MAX_DISTANCE", 0.0)
    def test_no_nearby_data(self):
        with pytest.raises(
            gd.utils.MissingDataError, match="No valid DEM data found within"
        ):
            gd.prism_dem.retrieve_dem_data(
                global_data_dir=GLOBAL_DATA_FOLDER,
                lat=TEST_LAT,
                lon=TEST_LON,
            )

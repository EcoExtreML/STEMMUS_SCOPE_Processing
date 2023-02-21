"""Generates test data for the 'global' model.

To generate the test data, run this script from the main repo folder. I.e.:
    STEMMUS_SCOPE_Processing > python ./tests/test_data/generate_test_data_global.py

The required folders will automatically be generated, and subsequently filled with the
test data. All the files are designed to mimic the real input data, except the values
are all nonsense (to avoid any copyright or licensing issues).
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import rioxarray  # noqa
import xarray as xr


TEST_DATA_DIR = Path("./tests/test_data/directories/global")
TEST_LAT = 37.933804  # Same as XX-Xxx
TEST_LON = -107.807526
START_TIME = np.datetime64("1996-01-01T00:00")
END_TIME = np.datetime64("1996-01-03T00:00")


# Generate directories
dirs = ["era5", "era5-land", "co2", "canopy_height", "dem", "soil_initial"]
for _dir in dirs:
    dir_path = Path(TEST_DATA_DIR) / _dir
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def generate_era5_file(
    varname: str, test_value: float, resolution: float, time_res="1H"
) -> xr.Dataset:
    time_coords = pd.date_range(
        start=START_TIME, end=END_TIME, freq=time_res, inclusive="left"
    )
    lat_coords = np.arange(
        start=np.round(TEST_LAT - 1),
        stop=np.round(TEST_LAT + 1),
        step=resolution,
    )
    lon_coords = np.arange(
        start=np.round(TEST_LON - 1),
        stop=np.round(TEST_LON + 1),
        step=resolution,
    )
    data = np.zeros((len(lon_coords), len(lat_coords), len(time_coords))) + test_value

    return xr.Dataset(
        data_vars={varname: (("longitude", "latitude", "time"), data)},
        coords={
            "longitude": lon_coords,
            "latitude": lat_coords,
            "time": time_coords,
        },
    )


# ERA5 data:
vars_names_era5 = [
    ("u10", 1, "era5_10m_u_component_of_wind"),
    ("v10", 2, "era5_10m_v_component_of_wind"),
    ("mtpr", 3, "era5_mean_total_precipitation_rate"),
    ("sp", 1e5, "era5_surface_pressure"),
    ("ssrd", 5, "era5_surface_solar_radiation_downwards"),
    ("strd", 6, "era5_surface_thermal_radiation_downwards"),
]

for var, test_value, var_fname in vars_names_era5:
    ds = generate_era5_file(var, test_value, resolution=0.25)
    ds.to_netcdf(path=TEST_DATA_DIR / "era5" / f"{var_fname}_2014_hourly.nc")


# ERA5-land data
vars_names_era5 = [
    ("d2m", 278.15, "era5-land_2m_dewpoint_temperature"),
    ("t2m", 283.15, "era5-land_2m_temperature"),
]

for var, test_value, var_fname in vars_names_era5:
    ds = generate_era5_file(var, test_value, resolution=0.1)
    ds.to_netcdf(path=TEST_DATA_DIR / "era5-land" / f"{var_fname}_2014_hourly.nc")


# CAMS CO2 data. Similar to era5 format
ds = generate_era5_file(
    varname="co2", test_value=12, resolution=0.25, time_res="3H"
).transpose("time", "latitude", "longitude")
ds.to_netcdf(TEST_DATA_DIR / "co2" / "CAMS_CO2_2003-2020_test.nc")


# Soil initial vars
vars_names_soil_init = [
    ("skt", 1, "era5-land_skin_temperature"),
    ("stl1", 2, "era5-land_soil_temperature_level_1"),
    ("stl2", 3, "era5-land_soil_temperature_level_2"),
    ("stl3", 4, "era5-land_soil_temperature_level_3"),
    ("stl4", 5, "era5-land_soil_temperature_level_4"),
    ("swvl1", 6, "era5-land_volumetric_soil_water_layer_1"),
    ("swvl2", 7, "era5-land_volumetric_soil_water_layer_2"),
    ("swvl3", 8, "era5-land_volumetric_soil_water_layer_3"),
    ("swvl4", 9, "era5-land_volumetric_soil_water_layer_4"),
]

for var, test_value, var_fname in vars_names_soil_init:
    ds = generate_era5_file(var, test_value, resolution=0.1, time_res="24H")
    ds.to_netcdf(path=TEST_DATA_DIR / "soil_initial" / f"{var_fname}_2014_hourly.nc")


def generate_tiff_data(test_value: float, resolution: float) -> xr.Dataset:
    band_coords = np.array([1], dtype="int32")
    y_coords = np.arange(
        start=TEST_LAT - 25 * resolution,
        stop=TEST_LAT + 25 * resolution,
        step=resolution,
    )
    x_coords = np.arange(
        start=TEST_LON + 25 * resolution,
        stop=TEST_LON - 25 * resolution,
        step=-resolution,
    )
    data = np.zeros((len(band_coords), len(y_coords), len(x_coords))) + test_value

    return xr.Dataset(
        data_vars={"band_data": (("band", "y", "x"), data)},
        coords={
            "band": band_coords,
            "y": y_coords,
            "x": x_coords,
        },
    )


# Canopy height
da = generate_tiff_data(test_value=1.0, resolution=0.000083)["band_data"]
da = da.rio.write_crs("epsg:4326")
da.rio.to_raster(
    TEST_DATA_DIR / "canopy_height" / "ETH_GlobalCanopyHeight_10m_2020_N36W108_Map.tif"
)

# DEM
da = generate_tiff_data(test_value=111.0, resolution=0.001667)["band_data"]
da = da.rio.write_crs("epsg:4326")
da.rio.to_raster(TEST_DATA_DIR / "dem" / "Copernicus_DSM_30_N37_00_W108_00_DEM.tif")

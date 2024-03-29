"""Generates test data for the 'global' model.

To generate the test data, run this script from the main repo folder. I.e.:
    STEMMUS_SCOPE_Processing > python ./tests/test_data/generate_test_data_global.py

The required folders will automatically be generated, and subsequently filled with the
test data. All the files are designed to mimic the real input data, except the values
are all nonsense (to avoid any copyright or licensing issues).
"""
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
dirs = [
    "era5",
    "era5-land",
    "co2",
    "canopy_height",
    "dem",
    "soil_initial",
    "lai",
    "landcover",
]
for _dir in dirs:
    dir_path = Path(TEST_DATA_DIR) / _dir
    dir_path.mkdir(parents=True, exist_ok=True)


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


# LAI
def generate_lai_data(test_value, resolution):
    time_coords = pd.date_range(
        start=START_TIME, end=END_TIME, freq="1d", inclusive="left"
    )
    lat_coords = np.arange(
        start=TEST_LAT - 10 * resolution,
        stop=TEST_LAT + 10 * resolution,
        step=resolution,
    )
    lon_coords = np.arange(
        start=TEST_LON - 10 * resolution,
        stop=TEST_LON + 10 * resolution,
        step=resolution,
    )
    data = np.zeros((len(lon_coords), len(lat_coords), len(time_coords))) + test_value

    return xr.Dataset(
        data_vars={
            "LAI": (("lon", "lat", "time"), data),
            "LAI_ERR": (("lon", "lat", "time"), data / 2),
            "retrieval_flag": (("lon", "lat", "time"), data),
            "crs": (("time"), np.zeros(len(time_coords))),
        },
        coords={
            "lon": lon_coords,
            "lat": lat_coords,
            "time": time_coords,
        },
    )


lai_data = generate_lai_data(test_value=4.0, resolution=1 / 112)

for i in range(lai_data["time"].size):
    ftime = pd.to_datetime(lai_data.isel(time=i)["time"].values)
    fname = f"c3s_LAI_{ftime:%Y%m%d}000000_GLOBE_PROBAV_V3.0.1.nc"
    # Note: isel with a list (incl. comma) to keep the 'time' dimension (!)
    lai_data.isel(
        time=[
            i,
        ]
    ).to_netcdf(TEST_DATA_DIR / "lai" / fname)


# Land cover
def generate_landcover_data(test_value: int, resolution: float) -> xr.Dataset:
    time_coords = pd.date_range(
        start=np.datetime64(f"{pd.to_datetime(START_TIME).year}-01-01T00:00"),
        freq="AS",  # year start
        periods=pd.to_datetime(END_TIME).year - pd.to_datetime(START_TIME).year + 1,
        inclusive="both",
    )
    lat_coords = np.arange(
        start=TEST_LAT + 10 * resolution,
        stop=TEST_LAT - 10 * resolution,
        step=-resolution,
    )
    lon_coords = np.arange(
        start=TEST_LON - 10 * resolution,
        stop=TEST_LON + 10 * resolution,
        step=resolution,
    )

    # Add the bounds
    lat_bounds = np.hstack(
        (lat_coords[0] - 0.5 * resolution, lat_coords + 0.5 * resolution)
    )
    lat_bounds = np.vstack((lat_bounds[:-1], lat_bounds[1:])).T
    # has time as dim, so the lat bounds need to be repeated for every time dim.
    lat_bounds = np.repeat(lat_bounds[np.newaxis, :, :], len(time_coords), axis=0)

    lon_bounds = np.hstack(
        (
            lon_coords - 0.5 * resolution,
            lon_coords[-1] + 0.5 * resolution,
        )
    )
    lon_bounds = np.vstack((lon_bounds[:-1], lon_bounds[1:])).T
    lon_bounds = np.repeat(lon_bounds[np.newaxis, :, :], len(time_coords), axis=0)

    data = (
        np.zeros((len(time_coords), len(lat_coords), len(lon_coords)), dtype=np.uint8)
        + test_value
    )

    ds = xr.Dataset(
        data_vars={
            "lccs_class": (("time", "lat", "lon"), data),
            "lat_bounds": (("time", "lat", "bounds"), lat_bounds),
            "lon_bounds": (("time", "lon", "bounds"), lon_bounds),
        },
        coords={
            "lon": lon_coords,
            "lat": lat_coords,
            "time": time_coords,
        },
    )
    ds["lccs_class"].attrs = {
        "flag_values": np.array([0, 70], dtype=np.uint8),
        "flag_meanings": "no_data tree_needleleaved_evergreen_closed_to_open",
    }

    return ds


landcover_data = generate_landcover_data(test_value=70, resolution=1 / 360)


for i in range(landcover_data["time"].size):
    ftime = pd.to_datetime(landcover_data.isel(time=i)["time"].values)
    fname = f"ESACCI-LC-L4-LCCS-Map-300m-P1Y-{ftime:%Y}-v2.0.7cds.nc"
    # Note: isel with a list (incl. comma) to keep the 'time' dimension (!)
    landcover_data.isel(
        time=[
            i,
        ]
    ).to_netcdf(TEST_DATA_DIR / "landcover" / fname)

"""Generate dummy soil initial condition data for testing."""
from pathlib import Path
import numpy as np
import xarray as xr


TEST_DATA_DIR = Path(
    "./tests/test_data/directories/model_parameters/soil_initialcondition/"
)
FILE_TIME = np.datetime64("1996-01-01T00:00",)
LOCATION = "XX-Xxx"
LAT = 37.933804  # from XX-Xxx dummy file.
LON = -107.807526

timestr = np.datetime_as_string(FILE_TIME)[:-6].replace("-","")
filenames_varnames = [
    (f"{LOCATION}_{timestr}_00-land_skin_temperature.nc", "skt"),
    (f"{LOCATION}_{timestr}_00-land_soil_temperature_level_1.nc", "stl1"),
    (f"{LOCATION}_{timestr}_00-land_soil_temperature_level_2.nc", "stl2"),
    (f"{LOCATION}_{timestr}_00-land_soil_temperature_level_3.nc", "stl3"),
    (f"{LOCATION}_{timestr}_00-land_soil_temperature_level_4.nc", "stl4"),
    (f"{LOCATION}_{timestr}_00-land_volumetric_soil_water_layer_1.nc", "swvl1"),
    (f"{LOCATION}_{timestr}_00-land_volumetric_soil_water_layer_2.nc", "swvl2"),
    (f"{LOCATION}_{timestr}_00-land_volumetric_soil_water_layer_3.nc", "swvl3"),
    (f"{LOCATION}_{timestr}_00-land_volumetric_soil_water_layer_4.nc", "swvl4"),
]

data = np.zeros((1, 1, 1))

for filename, varname in filenames_varnames:
    ds = xr.Dataset(
        data_vars={varname: (("time", "latitude", "longitude"), data)},
        coords={
            "time": np.array([FILE_TIME]),
            "latitude": np.array([LAT]),
            "longitude": np.array([LON]),
        }
    )
    ds.to_netcdf(TEST_DATA_DIR / filename)

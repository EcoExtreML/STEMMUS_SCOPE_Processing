"""Module for the 'global' data IO of PyStemmusScope."""
from pathlib import Path
from typing import List
from typing import Union
import numpy as np
import xarray as xr
from PyStemmusScope.global_data import utils


def extract_cams_data(  # noqa:PLR0913 (too many arguments)
    files_cams: List[Path],
    lat: Union[int, float],
    lon: Union[int, float],
    start_time: np.datetime64,
    end_time: np.datetime64,
    timestep: str,
) -> xr.DataArray:
    """Extract and convert the required variables from the CAMS CO2 dataset.

    Args:
        files_cams: List of CAMS files.
        lat: Latitude of the site.
        lon: Longitude of the site.
        start_time: Start time of the model run.
        end_time: End time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        DataArray containing the CO2 concentration.
    """
    ds = xr.open_mfdataset(files_cams)
    ds = ds.sel(latitude=lat, longitude=lon, method="nearest")
    ds = ds.drop_vars(["latitude", "longitude"])
    ds = ds.resample(time=timestep).interpolate("linear")
    ds = ds.sel(time=slice(start_time, end_time))
    return ds.co2

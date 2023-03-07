from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
import numpy as np
import xarray as xr
from PyStemmusScope.global_data import utils


def retrieve_lai_data(
    global_data_dir: Path,
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Check for availability and retrieve the Copernicus LAI data.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        DataArray containing the LAI of the specified site for the given time range.
    """
    files = list((global_data_dir / "lai").glob("*.nc"))

    if len(files) == 0:
        raise FileNotFoundError(
            f"No netCDF files found in the folder '{global_data_dir / 'lai':str}'"
        )

    return extract_lai_data(
        files_lai=files,
        latlon=latlon,
        time_range=time_range,
        timestep=timestep,
    )


def extract_lai_data(
    files_lai: List[Path],
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Generate LAI values, until a dataset is chosen.

    Args:
        files_lai: List of paths to the *.nc files.
        lat: Latitude of the site.
        lon: Longitude of the site.
        start_time: Start time of the model run.
        end_time: End time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        DataArray containing the LAI of the specified site for the given time range.
    """

    def preproc(ds):
        ds = ds.drop_vars(["crs", "LAI_ERR", "retrieval_flag"])
        ds = ds.sel(lat=latlon[0], lon=latlon[1], method="nearest")
        return ds.drop_vars(["lat", "lon"])

    ds_lai = xr.open_mfdataset(files_lai, preprocess=preproc)
    ds_lai = ds_lai.resample(time=timestep).interpolate("linear")
    ds_lai = ds_lai.sel(time=slice(time_range[0], time_range[1]))

    check_lai_dataset(ds_lai)

    return ds_lai["LAI"].values


def check_lai_dataset(
    laidata: xr.Dataset,
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
) -> None:
    """Validate the LAI dataset (variables, location & time range).

    Args:
        laidata: Dataset containing the LAI data.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
    """
    try:
        utils.assert_variables_present(laidata, ["LAI"])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "Could not find the variable 'LAI' in the LAI dataset. "
            "Please check the netCDF files or the path."
        ) from err

    try:
        utils.assert_location_within_bounds(
            laidata, x=latlon[1], y=latlon[0], xdim="lon", ydim="lat"
        )
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "The LAI data does not cover the given location. "
            "Please check the LAI netCDF files, or select a different location."
        ) from err

    try:
        utils.assert_time_within_bounds(laidata, time_range[0], time_range[1])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "The LAI data does not cover the given start end end time. "
            "Please check the LAI netCDF files, or modify the model start and end time."
        ) from err

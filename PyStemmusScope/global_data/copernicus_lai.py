"""Module for loading and validating the Copernicus LAI dataset."""
from pathlib import Path
from typing import Union
import numpy as np
import xarray as xr
from PyStemmusScope.global_data import utils


RESOLUTION_LAI = 1 / 112  # Resolution of the LAI dataset in degrees


def retrieve_lai_data(
    global_data_dir: Path,
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Check for availability and retrieve the Copernicus LAI data.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800s"

    Returns:
        DataArray containing the LAI of the specified site for the given time range.
    """
    files = list((global_data_dir / "lai").glob("*.nc"))

    if len(files) == 0:
        raise FileNotFoundError(
            f"No netCDF files found in the folder '{global_data_dir / 'lai'}'"
        )

    return extract_lai_data(
        files_lai=files,
        latlon=latlon,
        time_range=time_range,
        timestep=timestep,
    )


def extract_lai_data(
    files_lai: list[Path],
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Generate LAI values, until a dataset is chosen.

    Args:
        files_lai: List of paths to the *.nc files.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800s"

    Returns:
        DataArray containing the LAI of the specified site for the given time range.
    """
    ds = xr.open_mfdataset(files_lai, chunks="auto")

    check_lai_dataset(ds, latlon, time_range)

    ds = ds.drop_vars(["crs", "LAI_ERR", "retrieval_flag"])

    try:
        ds = ds.sel(
            lat=latlon[0],
            lon=latlon[1],
            method="nearest",
            tolerance=RESOLUTION_LAI,
        )
    except KeyError as err:
        if "not all values found" in str(err):
            raise utils.MissingDataError(
                f"\nNo data point was found within {RESOLUTION_LAI} degrees"
                f"\nof the specified location {latlon}."
                f"\nPlease check the netCDF files or select a different location"
            ) from err
        else:
            raise err

    ds = ds.drop_vars(["lat", "lon"])
    ds = ds.compute()  # Load into memory before resampling
    ds = ds.resample(time=timestep).interpolate("linear")
    ds = ds.sel(time=slice(time_range[0], time_range[1]))

    return ds["LAI"].values


def check_lai_dataset(
    lai_data: xr.Dataset,
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
) -> None:
    """Validate the LAI dataset (variables name, location & time range).

    Args:
        lai_data: Dataset containing the LAI data.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
    """
    try:
        utils.assert_variables_present(lai_data, ["LAI"])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nCould not find the variable 'LAI' in the LAI dataset. "
            "\nPlease check the netCDF files or the path."
        ) from err

    try:
        utils.assert_location_within_bounds(
            lai_data, x=latlon[1], y=latlon[0], xdim="lon", ydim="lat"
        )
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nThe LAI data does not cover the given location."
            "\nPlease check the LAI netCDF files, or select a different location."
        ) from err

    try:
        utils.assert_time_within_bounds(lai_data, time_range[0], time_range[1])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nThe LAI data does not cover the given start and end time. "
            "\nPlease check the LAI netCDF files, or modify the model"
            "\nstart and end time."
        ) from err

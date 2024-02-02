"""Module for loading and validating the CAMS CO2 dataset."""
from pathlib import Path
from typing import Union
import numpy as np
import xarray as xr
from PyStemmusScope.global_data import utils


RESOLUTION_CAMS = 0.75  # Resolution of the dataset in degrees


def retrieve_co2_data(
    global_data_dir: Path,
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Check for availability and retrieve the CAMS CO2 data.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800s"

    Returns:
        DataArray containing the CO2 at the specified site for the given time range.
    """
    files = list((global_data_dir / "co2").glob("*.nc"))

    if len(files) == 0:
        raise FileNotFoundError(
            f"No netCDF files found in the folder '{global_data_dir / 'co2'}'"
        )

    return extract_cams_data(
        files_cams=files,
        latlon=latlon,
        time_range=time_range,
        timestep=timestep,
    )


def extract_cams_data(
    files_cams: list[Path],
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> np.ndarray:
    """Extract and convert the required variables from the CAMS CO2 dataset.

    Args:
        files_cams: List of CAMS files.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800s"

    Returns:
        DataArray containing the CO2 concentration.
    """
    ds = xr.open_mfdataset(files_cams, chunks="auto")

    check_cams_dataset(cams_data=ds, latlon=latlon, time_range=time_range)

    try:
        ds = ds.sel(
            latitude=latlon[0],
            longitude=latlon[1],
            method="nearest",
            tolerance=RESOLUTION_CAMS,
        )
    except KeyError as err:
        if "not all values found" in str(err):
            raise utils.MissingDataError(
                f"\nNo data point was found within {RESOLUTION_CAMS} degrees"
                f"\nof the specified location {latlon}."
                f"\nPlease check the netCDF files or select a different location"
            ) from err
        else:
            raise err

    ds = ds.drop_vars(["latitude", "longitude"])
    ds = ds.compute()
    ds = ds.resample(time=timestep).interpolate("linear")
    ds = ds.sel(time=slice(time_range[0], time_range[1]))

    return ds["co2"].values


def check_cams_dataset(
    cams_data: xr.Dataset,
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
) -> None:
    """Validate the CAMS CO2 dataset (variable name, location & time range).

    Args:
        cams_data: Dataset containing the CAMS CO2 data.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
    """
    try:
        utils.assert_variables_present(cams_data, ["co2"])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nCould not find the variable 'co2' in the CAMS dataset."
            "\nPlease check the netCDF files or the path."
        ) from err

    try:
        utils.assert_location_within_bounds(
            cams_data, x=latlon[1], y=latlon[0], xdim="longitude", ydim="latitude"
        )
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nThe CO2 data does not cover the given location."
            "\nPlease check the CAMS CO2 netCDF files, or select"
            "\na different location."
        ) from err

    try:
        utils.assert_time_within_bounds(cams_data, time_range[0], time_range[1])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "\nThe CO2 data does not cover the given start and end time. "
            "\nPlease check the CAMS CO2 netCDF files, or modify the model"
            "\nstart and end time."
        ) from err

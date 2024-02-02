"""Utility funtions for the global data IO."""
from typing import Union
import numpy as np
import xarray as xr


class MissingDataError(Exception):
    """Error to be raised when requested data is missing."""


class InvalidLocationError(Exception):
    """Error to be raised when a location is given where no data will ever exist."""


def assert_variables_present(
    dataset: xr.Dataset,
    variables: list[str],
):
    """Check if the required variables are in the specified dataset."""
    dataset_variables = [str(var) for var in dataset.data_vars]
    missing_variables = set(variables) - set(dataset_variables)
    if len(missing_variables) > 0:
        raise MissingDataError(
            "Some required variables are missing from the data:"
            "".join(f"\n    {var}" for var in missing_variables)
        )


def assert_location_within_bounds(
    data: Union[xr.DataArray, xr.Dataset],
    x: float,
    y: float,
    xdim: str = "x",
    ydim: str = "y",
) -> None:
    """Compare a locations x/y (lon/lat) values to the range of the available data."""
    if (
        x > data[xdim].max()
        or x < data[xdim].min()
        or y > data[ydim].max()
        or y < data[ydim].min()
    ):
        raise MissingDataError(
            f"\nThe specified location {xdim}={x}, {ydim}={y} is not covered by the \n"
            f" range of the available data:\n"
            f"    {xdim}=[{data[xdim].min()}-{data[xdim].max()}],\n"
            f"    {ydim}=[{data[ydim].min()}-{data[ydim].max()}].\n"
        )


def assert_time_within_bounds(
    data: Union[xr.DataArray, xr.Dataset],
    start_time: np.datetime64,
    end_time: np.datetime64,
    time_dim: str = "time",
) -> None:
    """Assert that the start and end time are within the data's time bounds.

    Args:
        data: Dataset or DataArray that requires validation
        start_time: Start time of the model run.
        end_time: End time of the model run.
        time_dim: Name of the time dimension. Defaults to "time".
    """
    if (
        datetime_to_unix(start_time) < datetime_to_unix(data[time_dim].min().values)
    ) or (datetime_to_unix(end_time) > datetime_to_unix(data[time_dim].max().values)):
        raise MissingDataError(
            "\nThe available data cannot cover the specified start and end time.\n"
            f"    Specified model time range:\n"
            f"        {np.datetime_as_string(start_time, unit='m')}"  # type: ignore
            f" - {np.datetime_as_string(end_time, unit='m')}\n"  # type: ignore
            f"    Data start: {np.datetime_as_string(data[time_dim].min(), unit='m')}\n"  # type: ignore
            f"    Data end: {np.datetime_as_string(data[time_dim].max(), unit='m')}"  # type: ignore
        )


def find_nearest_non_nan(  # noqa:PLR0913 (too many arguments)
    da: xr.DataArray,
    x: float,
    y: float,
    xdim: str = "x",
    ydim: str = "y",
    max_distance: Union[float, None] = None,
) -> xr.DataArray:
    """Extract the (Cartesian) nearest non-nan value from a DataArray.

    Args:
        da: DataArray containing the data, and the xdim and ydim as dimensions
        x: x-coordinate of interest
        y: y-coordinate of interest
        xdim: optional, to be used if the x-dimension is named "lon" or "longitude".
        ydim: optional, to be used if the y-dimension is named "lat" or "latitude".
        max_distance: Maximum distance between the specified location and the nearest
            non-nan location (same units as x and y coordinates).

    Returns:
        The input dataarray reduced to only one location
    """
    distance = ((da[xdim] - x) ** 2 + (da[ydim] - y) ** 2) ** 0.5
    distance = distance.where(~np.isnan(da), np.nan)
    if max_distance is None or distance.min() < max_distance:
        return da.isel(distance.argmin(dim=[xdim, ydim]))  # type: ignore
    raise MissingDataError(
        "No non-nan data could be found within specified the maximum distance."
    )


def make_lat_lon_strings(
    lat: Union[int, float],
    lon: Union[int, float],
    step: int = 1,
) -> tuple[str, str]:
    """Turn numeric lat and lon values into strings.

    Args:
        lat: Latitude between -90 and 90.
        lon: Longitude between -180 and 180.
        step: The size of the step in values. E.g. if step is 5, valid latitude strings
            are "N00", "N05", "N10", etc.

    Returns:
        Two strings, in the form ("N50", "E005")
    """
    if lat > 90 or lat < -90:
        raise ValueError("Latitude out of bounds (-90, 90)")
    if lon > 180 or lon < -180:
        raise ValueError("Longitude out of bounds (-180, 180)")

    lat = int(lat // step * step)
    lon = int(lon // step * step)

    latstr = str(abs(lat)).rjust(2, "0")
    lonstr = str(abs(lon)).rjust(3, "0")
    latstr = f"N{latstr}" if lat >= 0 else f"S{latstr}"
    lonstr = f"E{lonstr}" if lon >= 0 else f"W{lonstr}"

    return latstr, lonstr


def datetime_to_unix(dt):
    """Convert a numpy datetime object to unix time (seconds since 1970-01-01)."""
    return dt.astype("datetime64[s]").astype(float)

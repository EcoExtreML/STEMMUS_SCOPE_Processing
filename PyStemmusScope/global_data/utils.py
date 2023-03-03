"""Utility funtions for the global data IO."""
from typing import Tuple
from typing import Union
import numpy as np


def find_nearest_non_nan(da, x, y, xdim="x", ydim="y"):
    """Extract the (Cartesian) nearest non-nan value from a DataArray.

    Args:
        da: DataArray containing the data, and the xdim and ydim as dimensions
        x: x-coordinate of interest
        y: y-coordinate of interest
        xdim: optional, to be used if the x-dimension is named "lon" or "longitude".
        ydim: optional, to be used if the y-dimension is named "lat" or "latitude".

    Returns:
        The input dataarray reduced to only one location/
    """
    distance = ((da[xdim] - x) ** 2 + (da[ydim] - y) ** 2) ** 0.5
    distance = distance.where(~np.isnan(da), np.nan)
    return da.isel(distance.argmin(dim=[xdim, ydim]))


def make_lat_lon_strings(
    lat: Union[int, float],
    lon: Union[int, float],
    step: int = 1,
) -> Tuple[str, str]:
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

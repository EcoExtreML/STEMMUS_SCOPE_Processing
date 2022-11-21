import ast
import os
import re
from datetime import datetime
from itertools import product
from pathlib import Path
import numpy as np


def convert_to_lsm_coordinates(lat, lon):
    """Converts latitude in degrees North to NCAR's LSM coordinate system: Grid with lat
    values ranging from 0 -- 360, where 0 is the South Pole, and lon values ranging
    from 0 -- 720, where 0 is the prime meridian. Both representing a 0.5 degree
    resolution.

    Args:
        lat (float): Latitude in degrees North
        lon (float): longitude in degrees East

    Returns:
        (int, int): (nearest) latitude grid coordinates
    """
    lat += 90
    lat *= 2

    lon *= 2
    if lon < 0:
        lon += 720

    return np.round(lat).astype(int), np.round(lon).astype(int)


def os_name():
    return os.name


def to_absolute_path(
    input_path: str,
    parent: Path = None,
    must_be_in_parent=True,
) -> Path:
    """Parse input string as :py:class:`pathlib.Path` object.

    Args:
        input_path: Input string path that can be a relative or absolute path.
        parent: Optional parent path of the input path
        must_exist: Optional argument to check if the input path exists.
        must_be_in_parent: Optional argument to check if the input path is
            subpath of parent path

    Returns:
        The input path that is an absolute path and a :py:class:`pathlib.Path` object.
    """

    must_exist = False
    pathlike = Path(input_path)
    if parent:
        if not parent.is_absolute():
            # care for windows, see issue 22
            must_exist = os_name() == 'nt'
        pathlike = parent.joinpath(pathlike)
        if must_be_in_parent:
            try:
                pathlike.relative_to(parent)
            except ValueError as exc:
                raise ValueError(
                    f"Input path {input_path} is not a subpath of parent {parent}"
                ) from exc
    else:
        # care for windows, see issue 22
        must_exist = os_name() == 'nt'

    return pathlike.expanduser().resolve(strict=must_exist)


def get_forcing_file(config):
    """Get forcing file from the location.
    """
    location, fmt = check_location_fmt(config["Location"])
    # check if the forcing file exists for the given locaiton(s)
    if fmt == "site":
        # get forcing file list
        forcing_filenames_list = [file.name for file in Path(config["ForcingPath"]).iterdir()]
        forcing_file = [filename for filename in forcing_filenames_list if location in filename]
        #pylint: disable=no-else-raise
        if not forcing_file:
            raise ValueError(f"Forcing file does not exist for the given site {location}.")
        elif len(forcing_file) > 1:
            raise ValueError(f"Multiple forcing files exist for the given site {location}." +
                "Please check your focing files and remove the redundant files.")
        else:
            forcing_file = forcing_file[0]

    elif fmt == "latlon":
        raise NotImplementedError
    elif fmt == "bbox":
        raise NotImplementedError

    return forcing_file


def check_location_fmt(loc):
    """Check the format of location.

    Three types of format are supported:
    - Site name (e.g. "DE-Kli")
    - Latitude and longitude (e.g. "(56.4, 112.0)")
    - Bounding box (lat_min, lat_max), (lon_min, lon_max) (e.g. "[19.5,20.5], [125.5,130.0]")

    Args:
        loc: String of location extracted from config file.

    Returns:
        Location name (string) or location (tuple) lat,lon pair and its format
    """
    # remove all blanks
    loc = loc.replace(" ","")
    if re.fullmatch("[A-Z]{2}-[A-Z][a-z]{2}", loc):
        location = loc
        fmt = "site"
    elif re.fullmatch(r"\(\d*[.,]?\d*,\d*[.,]?\d*\)", loc):
        # turn string into tuples
        location = ast.literal_eval(loc)
        # check if the coordinate is valid
        #_check_lat_lon(location)
        fmt = "latlon"
    elif re.fullmatch(r"(\[\d*[.,]?\d*,\d*[.,]?\d*\][,]?){2}", loc):
        # find items between brackets
        bbox = re.findall(r"\[.*?\]", loc)
        # turn string into list
        bbox = [ast.literal_eval(i) for i in bbox]
        location = [list(coordinate) for coordinate in product(bbox[0], bbox[1])]
        #for coordinates in location:
        #    _check_lat_lon(coordinates)
        fmt = "bbox"
    else:
        raise ValueError(
            f"Location '{loc}' in the config file does not match expected format."
        )

    return location, fmt


def _check_lat_lon(coordinates):
    """Check if the coordinates exists."""
    raise NotImplementedError


def check_time_fmt(config):
    """Check the format of time."""
    # check if start/end time can be converted to the iso format
    start_time = datetime.strptime(config["StartTime"],'%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(config["EndTime"],'%Y-%m-%dT%H:%M')

    if start_time > end_time:
        raise ValueError("Invalid time range. StartTime must be earlier than EndTime.")


def remove_dates_from_header(filename):
    """Removes the datetime string from the .mat file header.

    MATLAB raises an error when some characters are non-UTF-8 (?), e.g. Chinese month
    names. This function removes this part of the file header to avoid this problem.

    Args:
        filename (Path): Valid path to the .mat file
    """
    with open(filename, "rb") as f:
        data = f.read()

    # Get locations of date string in header
    start_datestring = data[:128].find(b"Created on:") + 12
    end_datestring = data[:128].find(b"HDF5") - 1

    # Rebuild the data, with the dates in the header removed
    sanitized_data = (
        data[:start_datestring] +
        b' '*len(data[start_datestring:end_datestring]) +
        data[end_datestring:]
        )

    # Overwrite the old file
    with open(filename, 'wb') as file:
        file.write(sanitized_data)

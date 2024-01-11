"""Assorted utils to be shared across multiple other modules."""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from typing import Union
import numpy as np


def convert_to_lsm_coordinates(lat: float, lon: float) -> tuple[int, int]:
    """Convert latitude in degrees North to NCAR's LSM coordinate system.

    NCAR's LSM coordinates consist of a grid with lat values ranging from 0 -- 360,
    where 0 is the South Pole, and lon values ranging from 0 -- 720, where 0 is the
    prime meridian. Both representing a 0.5 degree resolution.

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
    """Alias for os.name."""
    return os.name


def to_absolute_path(
    input_path: Union[str, Path],
    parent: Optional[Path] = None,
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
            must_exist = os_name() == "nt"
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
        must_exist = os_name() == "nt"

    return pathlike.expanduser().resolve(strict=must_exist)


def get_forcing_file(config):
    """Get forcing file from the location."""
    location, fmt = check_location_fmt(config["Location"])
    # check if the forcing file exists for the given location(s)
    if fmt == "site":
        # get forcing file list
        forcing_filenames_list = [
            file.name for file in Path(config["ForcingPath"]).iterdir()
        ]
        forcing_file = [
            filename for filename in forcing_filenames_list if location in filename
        ]
        if not forcing_file:
            raise ValueError(
                f"Forcing file does not exist for the given site {location}."
            )
        if len(forcing_file) > 1:
            raise ValueError(
                f"Multiple forcing files exist for the given site {location}."
                + "Please check your forcing files and remove the redundant files."
            )
        forcing_file = Path(config["ForcingPath"]) / forcing_file[0]

    elif fmt == "latlon":
        raise NotImplementedError
    elif fmt == "bbox":
        raise NotImplementedError
    else:
        raise ValueError("Unknown value for site format")

    return forcing_file


# Location format aliases
LatLonFmt = tuple[float, float]
BBoxFmt = tuple[LatLonFmt, LatLonFmt]


def check_location_fmt(loc: str) -> tuple[Union[str, LatLonFmt, BBoxFmt], str]:
    """Check the format of the model location.

    Three types of format are supported:
    - Site name, e.g., "DE-Kli"
    - Latitude and longitude, e.g. "(56.4, 112.0)"
    - A rectangular bounding box, described with two opposing corners:
        ((lat1, lon1), (lat2, lon2)), e.g., "((19.5, 125.5), (20.5, 130.0))".

    Args:
        loc: Location extracted from the config file.

    Returns:
        Site name (string), location (tuple), or bounding box (tuple of tuples),
        Location format (string)
    """
    # Matches a floating-point like number. I.e., 5.23 or -2.0
    flstr = r"[+-]?\d*[\.]?\d*"

    site_pattern = r"[A-Z]{2}-([A-z]|\d){3}"
    latlon_pattern = rf"\(({flstr}),\s?({flstr})\)"
    bbox_pattern = rf"\(\(({flstr}),\s?({flstr})\),\s?\(({flstr}),\s?({flstr})\)\)"

    if re.fullmatch(site_pattern, loc):
        return loc, "site"

    re_match = re.findall(latlon_pattern, loc)
    if len(re_match) == 1:
        # TODO: add check if lat/lon are valid
        return (float(re_match[0][0]), float(re_match[0][1])), "latlon"

    re_match = re.findall(bbox_pattern, loc)
    if len(re_match) == 1:
        bbox = [float(x) for x in re_match[0]]
        # TODO: add check if bbox values are valid
        return ((bbox[0], bbox[1]), (bbox[2], bbox[3])), "bbox"

    raise ValueError(
        f"Location '{loc}' in the config file does not match expected format."
    )


def _check_lat_lon(coordinates):
    """Check if the coordinates exists."""
    raise NotImplementedError


def _check_bbox(coordinates):
    """Check if the bounding box input is valid."""
    raise NotImplementedError


def check_time_fmt(start, end):
    """Check the format of time."""
    # check if start/end time can be converted to the iso format
    if start == "NA":
        start_time = None
    else:
        start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M")
    if end == "NA":
        end_time = None
    else:
        end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M")

    for time in [start_time, end_time]:
        if time is not None and time.minute not in [0, 30]:
            raise ValueError(
                "Invalid time values. Due to the resolution of forcing file,"
                + " the input time should be either 0 or 30 minutes."
            )

    if (start_time and end_time) and start_time > end_time:
        raise ValueError("Invalid time range. StartTime must be earlier than EndTime.")


def remove_dates_from_header(file: Path):
    """Remove the datetime string from the .mat file header.

    MATLAB raises an error when some characters are non-UTF-8 (?), e.g. Chinese month
    names. This function removes this part of the file header to avoid this problem.

    Args:
        file (Path): Valid path to the .mat file
    """
    with file.open("rb") as f:
        data = f.read()

    # Get locations of date string in header
    start_datestring = data[:128].find(b"Created on:") + 12
    end_datestring = data[:128].find(b"HDF5") - 1

    # Rebuild the data, with the dates in the header removed
    sanitized_data = (
        data[:start_datestring]
        + b" " * len(data[start_datestring:end_datestring])
        + data[end_datestring:]
    )

    # Overwrite the old file
    with file.open(mode="wb") as f:
        f.write(sanitized_data)

import os
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

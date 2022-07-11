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

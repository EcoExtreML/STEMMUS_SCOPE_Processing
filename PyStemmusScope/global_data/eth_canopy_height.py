"""Module to load and check the ETH Canopy Height (2020) dataset."""
import gzip
from pathlib import Path
from typing import Union
import xarray as xr
from PyStemmusScope.global_data import utils


MAX_DISTANCE = 0.01  # Maximum lat/lon distance to be considered nearby.


def retrieve_canopy_height_data(
    global_data_dir: Path,
    lat: Union[int, float],
    lon: Union[int, float],
) -> float:
    """Verify if the expected canopy height file exists, and then load the data.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        lat: Latitude of the site.
        lon: Longitude of the site.

    Returns:
        Canopy height at the location.
    """
    filename = global_data_dir / "canopy_height" / get_filename_canopy_height(lat, lon)
    assert_tile_existance(filename.name)

    if not filename.exists():
        raise FileNotFoundError(
            f"\nCould not find a file with the name '{filename.name}'"
            f"\nin the directory:"
            f"\n    {filename.parent}."
            f"\nPlease download the file, or change the global data"
            f"\ndirectory to point to the right location."
        )
    return extract_canopy_height_data(filename, lat, lon)


def extract_canopy_height_data(
    file_canopy_height: Path,
    lat: Union[int, float],
    lon: Union[int, float],
) -> float:
    """Extract and validate the (ETH) canopy height data.

    Args:
        file_canopy_height: The canopy height .tiff file.
        lat: Latitude of the site.
        lon: Longitude of the site.

    Returns:
        Canopy height at the location.
    """
    da = xr.open_dataarray(file_canopy_height, engine="rasterio")
    da = da.sortby(["x", "y"])

    pad = 0.05  # Add padding around the data before trying to find nearest non-nan
    da = da.sel(y=slice(lat - pad, lat + pad), x=slice(lon - pad, lon + pad))

    try:
        canopy_height = utils.find_nearest_non_nan(
            da.compute(),
            x=lon,
            y=lat,
            max_distance=MAX_DISTANCE,
        )
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            f"\nNo valid canopy height data found within {MAX_DISTANCE} degrees"
            f"\nof the selected location ({lat:.3f}, {lon:.3f})."
            "\nPlease select a different (nearby) location."
        ) from err

    return canopy_height.values[0]


def get_filename_canopy_height(lat: Union[int, float], lon: Union[int, float]) -> str:
    """Get the right filename for the ETH canopy height dataset.

    The dataset is split up in 3 degree ^2 files. This makes the output filename, for
    example with the coordinates (52N, 4E):
        ETH_GlobalCanopyHeight_10m_2020_N51E003_Map.tif

    Note: There are no files when there is only oceans/seas in the gridcell. This
        function does not take that into account.

    Args:
        lat: Latitude of the location for which the filename should be retrieved.
        lon: Longitude of the location for which the filename should be retrieved.

    Returns:
        str: Properly formatted filename for a valid ETH GlobalCanopyHeight file.
    """
    latstr, lonstr = utils.make_lat_lon_strings(lat, lon, step=3)
    return f"ETH_GlobalCanopyHeight_10m_2020_{latstr}{lonstr}_Map.tif"


def assert_tile_existance(filename: str) -> None:
    """Assert that a canopy height tile exists with the specified filename."""
    valid_name_file = (
        Path(__file__).parent / "assets" / "h_canopy_filenames_compressed.txt.gz"
    )

    with gzip.open(valid_name_file, "rb") as f:
        valid_filenames = f.read().decode("utf-8")

    if filename not in valid_filenames:
        raise utils.InvalidLocationError(
            "\nNo canopy height data tile exists for the specified location."
            "\nPlease select a different location."
        )

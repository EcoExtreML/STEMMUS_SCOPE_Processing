"""Module load and check the Prism DEM (Digital Elevation Model) dataset."""
from pathlib import Path
from typing import Union
import xarray as xr
from PyStemmusScope.global_data import utils


def retrieve_dem_data(
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
        Surface elevation at the location.
    """
    filename = global_data_dir / "dem" / get_filename_dem(lat, lon)

    if not filename.exists():
        raise FileNotFoundError(
            f"Could not find a file with the name '{filename.name}' in the directory "
            f"{filename.parent}. Please download the file, or change the global data "
            "dir to point to the right location."
        )
    return extract_prism_dem_data(filename, lat, lon)


def extract_prism_dem_data(
    file_dem: Path,
    lat: Union[int, float],
    lon: Union[int, float],
) -> float:
    """Extract the elevation from the PRISM DEM dataset.

    Args:
        file_dem: The DEM .tiff file.
        lat: Latitude of the site.
        lon: Longitude of the site.

    Returns:
        Elevation of the location.
    """
    ds = xr.open_dataarray(file_dem, engine="rasterio")
    elevation = ds.sel(x=lon, y=lat, method="nearest")
    return elevation.values[0]


def get_filename_dem(lat: Union[int, float], lon: Union[int, float]) -> str:
    """Get the right filename for the Copernicus prism DEM dataset.

    The dataset is split up in 1 degree ^2 files. This makes the output filename, for
    example with the coordinates (52N, 4E):
        Copernicus_DSM_30_N52_00_E004_00_DEM.tif

    Note: There are no files when there is only oceans/seas in the gridcell. This
        function does not take that into account.

    Args:
        lat: Latitude of the location for which the filename should be retrieved.
        lon: Longitude of the location for which the filename should be retrieved.

    Returns:
        str: Properly formatted filename for a valid DEM file.
    """
    latstr, lonstr = utils.make_lat_lon_strings(lat, lon, step=1)
    return f"Copernicus_DSM_30_{latstr}_00_{lonstr}_00_DEM.tif"

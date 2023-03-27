"""Module for loading and validating the ESA CCI land cover dataset."""
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
import numpy as np
import pandas as pd
import xarray as xr
from PyStemmusScope.global_data import utils


RESOLUTION_CCI = 1 / 360  # Resolution of the dataset in degrees
FILEPATH_LANDCOVER_TABLE = Path(__file__).parent / "assets" / "lccs_to_igbp_table.csv"


def retrieve_landcover_data(
    global_data_dir: Path,
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> Dict[str, str]:
    """Get the land cover data from the CCI netCDF files.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        Dictionary containing IGBP and LCCS land cover classes.
    """

    files_cci = list((global_data_dir / "landcover").glob("*.nc"))

    return extract_landcover_data(
        files_cci=files_cci,
        latlon=latlon,
        time_range=time_range,
        timestep=timestep,
    )


def extract_landcover_data(
    files_cci: List[Path],
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> Dict[str, str]:
    """Extract the land cover data from the CCI netCDF files.

    Args:
        files_cci: List of CCI land cover files.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        Dictionary containing IGBP and LCCS land cover classes.
    """
    cci_dataset = xr.open_mfdataset(files_cci)
    cci_dataset = cci_dataset.compute()

    lat_bounds = cci_dataset["lat_bounds"].load()  # Load so that they are not
    lon_bounds = cci_dataset["lon_bounds"].load()  #  dask arrays
    lat_idx = np.logical_and(
        lat_bounds.isel(bounds=0) >= latlon[0], lat_bounds.isel(bounds=1) < latlon[0]
    ).argmax()
    lon_idx = np.logical_and(
        lon_bounds.isel(bounds=0) <= latlon[1], lon_bounds.isel(bounds=1) > latlon[1]
    ).argmax()

    lccs_id = cci_dataset.isel(lat=lat_idx, lon=lon_idx)["lccs_class"]

    # If time is size 1, interp fails. Adding an extra datapoint prevents this.
    if lccs_id["time"].size == 1:
        data_copy = lccs_id.copy()
        data_copy["time"] = lccs_id["time"] + np.timedelta64(1, "D")
        lccs_id = xr.concat((lccs_id, data_copy), dim='time')

    lccs_id = lccs_id.interp(
        time=pd.date_range(time_range[0], time_range[1], freq=timestep),
        method="nearest",
        kwargs={"fill_value": "extrapolate", "bounds_error": False},
    )

    landcover_lookup_table = get_landcover_table(cci_dataset)
    igbp_lookup_table = get_lccs_to_igbp_table()

    return {
        "LCCS_landcover": np.array(
            [landcover_lookup_table[_id] for _id in lccs_id.to_numpy()]
        ),
        "IGBP_veg_long": np.array(
            [igbp_lookup_table[_id] for _id in lccs_id.to_numpy()]
        ),
    }


def get_lccs_to_igbp_table() -> Dict[int, str]:
    """Read the land cover translation table, and turn it into a lookup dictionary."""
    df = pd.read_csv(FILEPATH_LANDCOVER_TABLE, index_col="lccs_class")
    return df.to_dict()["IGBP_STEMMUS_SCOPE"]


def get_landcover_table(cci_dataset: xr.Dataset) -> Dict[int, str]:
    """Get the lookup table to convert the flag values to a land cover name.

    The lookup table for the land cover classes is contained in the netCDF file, under
    the lcc_class attributes. This function extracts it and turns it into a (dict)
    lookup table.

    Args:
        cci_dataset: The CCI dataset netCDF file.

    Returns:
        The landcover class lookup table
    """
    flag_meanings = cci_dataset["lccs_class"].attrs["flag_meanings"].split(" ")
    flag_values = cci_dataset["lccs_class"].attrs["flag_values"]
    return {key: flag for key, flag in zip(flag_values, flag_meanings)}

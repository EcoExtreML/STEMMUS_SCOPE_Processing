"""Module containing the full global dataset collection."""
from pathlib import Path
from typing import Any
from typing import Union
import numpy as np
import pandas as pd
import xarray as xr
from PyStemmusScope import global_data as gd
from PyStemmusScope import variable_conversion as vc


def collect_datasets(
    global_data_dir: Path,
    latlon: Union[tuple[int, int], tuple[float, float]],
    time_range: tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> dict:
    """Collect and merge all the global datasets into one.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800s"

    Returns:
        Dictionary containing the variables extracted from the global datasets.
    """
    data: dict[str, Any] = {
        "time": xr.DataArray(
            pd.date_range(str(time_range[0]), str(time_range[1]), freq=timestep).rename(
                "time"
            )
        )
    }
    era5_data = gd.era5.retrieve_era5_data(
        global_data_dir,
        latlon,
        time_range,
        timestep,
    )

    data = {**data, **era5_data}

    data["wind_speed"] = vc.mask_data(data["wind_speed"], min_value=0.05)

    data["co2_conv"] = (
        vc.co2_mass_fraction_to_kg_per_m3(
            gd.cams_co2.retrieve_co2_data(
                global_data_dir,
                latlon,
                time_range,
                timestep,
            )
        )
        * 1e6
    )  # kg/m3 -> mg/m3

    data["lai"] = vc.mask_data(
        gd.copernicus_lai.retrieve_lai_data(
            global_data_dir,
            latlon,
            time_range,
            timestep,
        ),
        min_value=0.01,
    )

    data["elevation"] = gd.prism_dem.retrieve_dem_data(
        global_data_dir, latlon[0], latlon[1]
    )

    data["canopy_height"] = gd.eth_canopy_height.retrieve_canopy_height_data(
        global_data_dir,
        latlon[0],
        latlon[1],
    )

    # Height of measurement. Data has no actual equivalent. Set to a temporary value.
    # See issue #145.
    data["reference_height"] = 10.0

    data["sitename"] = "global"

    # Expected time format is days (as floating point) since Jan 1st 00:00.
    data["doy_float"] = (
        data["time"].dt.dayofyear
        - 1
        + data["time"].dt.hour / 24
        + data["time"].dt.minute / 60 / 24
    )
    data["year"] = data["time"].dt.year.astype(float)

    data["DELT"] = (
        (data["time"].values[1] - data["time"].values[0]) / np.timedelta64(1, "s")
    ).astype(float)
    data["total_timesteps"] = data["time"].size

    data["latitude"] = latlon[0]
    data["longitude"] = latlon[1]

    landcover_data = gd.cci_landcover.retrieve_landcover_data(
        global_data_dir,
        latlon,
        time_range,
        timestep,
    )
    data["IGBP_veg_long"] = landcover_data["IGBP_veg_long"]
    data["LCCS_landcover"] = landcover_data["LCCS_landcover"]

    return data

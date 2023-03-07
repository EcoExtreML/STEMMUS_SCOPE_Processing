"""ERA5 data module, for data validation and data loading."""
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
import numpy as np
import PyStemmusScope.variable_conversion as vc
import xarray as xr
from PyStemmusScope.global_data import utils


ERA5_VARIABLES = ["u10", "v10", "t2m", "mtpr", "sp", "ssrd", "strd", "d2m"]
RESOLUTION_ERA5 = 0.25  # Resolution in degrees, to find nearest gridpoint.
RESOLUTION_ERA5LAND = 0.10


def retrieve_era5_data(
    global_data_dir: Path,
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> Dict:
    """Check for availability and retrieve the ERA5 and ERA5-land data.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        Dictionary containing the variables extracted from ERA5.
    """
    files_era5 = list((global_data_dir / "era5").glob("*.nc"))
    files_era5_land = list((global_data_dir / "era5-land").glob("*.nc"))

    if len(files_era5) == 0:
        raise FileNotFoundError(
            f"No netCDF files found in the folder '{global_data_dir / 'era5':str}'"
        )
    if len(files_era5_land) == 0:
        raise FileNotFoundError(
            f"No netCDF files found in the folder '{global_data_dir / 'era5-land':str}'"
        )

    return load_era5_data(
        files_era5,
        files_era5_land,
        latlon,
        time_range,
        timestep,
    )


def load_era5_data(
    files_era5: List[Path],
    files_era5_land: List[Path],
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> Dict:
    """Extract and convert the required variables from the ERA5 data.

    Args:
        files_era5: List of ERA5 files.
        files_era5_land: List of ERA5-land files.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        Dictionary containing the variables extracted from ERA5.
    """
    ds = xr.merge(
        [
            get_era5_dataset(
                files=files,
                latlon=latlon,
                tolerance=resolution,
                time_range=time_range,
                timestep=timestep,
            )
            for (files, resolution) in zip(
                [files_era5, files_era5_land], [RESOLUTION_ERA5, RESOLUTION_ERA5LAND]
            )
        ]
    )

    check_era5_dataset(ds, latlon, time_range)

    data = {}
    data["wind_speed"] = (ds["u10"] ** 2 + ds["v10"] ** 2) ** 0.5
    data["t_air_celcius"] = ds["t2m"] - 273.15  # K -> degC
    data["precip_conv"] = ds["mtpr"] / 10  # mm/s -> cm/s
    data["psurf_hpa"] = ds["sp"] / 100  # Pa -> hPa
    data["sw_down"] = ds["ssrd"] / 3600  # J * hr / m2 ->  W / m2
    data["lw_down"] = ds["strd"] / 3600  # J * hr / m2 ->  W / m2

    data["ea"] = vc.calculate_es(ds["d2m"] - 273.15) * 10  # hPa
    data["vpd"] = vc.calculate_es(data["t_air_celcius"]) * 10 - data["ea"]  # hPa
    data["rh"] = data["ea"] / vc.calculate_es(data["t_air_celcius"]) * 10
    data["Qair"] = vc.specific_humidity(data["ea"], data["psurf_hpa"])

    return data


def get_era5_dataset(
    files: List[Path],
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    tolerance: float,
    time_range: Tuple[np.datetime64, np.datetime64],
    timestep: str,
) -> xr.Dataset:
    """Load the ERA5/ERA5-land multifile dataset, and select the location before merge.

    Args:
        files: The ERA5 or ERA5-land files.
        latlon: Latitude and longitude of the site.
        tolerance: Tolerance for finding the nearest gridpoint.
        time_range: Start and end time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. For example: "1800S"

    Returns:
        The ERA5 or ERA5-land dataset.
    """

    def preproc(ds):
        ds = ds.sel(
            latitude=latlon[0],
            longitude=latlon[1],
            method="nearest",
            tolerance=tolerance,
        )
        return ds.drop_vars(["latitude", "longitude"])

    ds = xr.open_mfdataset(files, preprocess=preproc)
    ds = ds.compute()
    ds = ds.resample(time=timestep).interpolate("linear")
    return ds.sel(time=slice(time_range[0], time_range[1]))


def check_era5_dataset(
    era5data: xr.Dataset,
    latlon: Union[Tuple[int, int], Tuple[float, float]],
    time_range: Tuple[np.datetime64, np.datetime64],
) -> None:
    """Validate the ERA5 and ERA5-land dataset (variables, location & time range).

    Args:
        era5data: Dataset containing the ERA5 and ERA5-land data.
        latlon: Latitude and longitude of the site.
        time_range: Start and end time of the model run.
    """
    try:
        utils.assert_variables_present(era5data, ERA5_VARIABLES)
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "(Some) ERA5 or ERA5-land variables are missing. "
            "Please check the ERA5 and ERA5-land folders and netCDF files."
        ) from err

    try:
        utils.assert_location_within_bounds(
            era5data, x=latlon[1], y=latlon[0], xdim="longitude", ydim="latitude"
        )
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "The ERA5 or ERA5-land data does not cover the given location. Please "
            "check the ERA5 and ERA5-land netCDF files, or select a different location."
        ) from err

    try:
        utils.assert_time_within_bounds(era5data, time_range[0], time_range[1])
    except utils.MissingDataError as err:
        raise utils.MissingDataError(
            "The ERA5 or ERA5-land data does not cover the given start end end time. "
            "Please check the ERA5 and ERA5-land netCDF files, or modify the model "
            "start and end time."
        ) from err

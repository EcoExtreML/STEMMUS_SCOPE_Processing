from pathlib import Path
import numpy as np
import xarray as xr
from . import utils
from . import variable_conversion as vc
from typing import Union
from typing import Tuple
from typing import Dict
from typing import List


TIMESTEP = "1800S"


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

    lat = int(lat//step * step)
    lon = int(lon//step * step)

    latstr = str(lat).rjust(2, "0")
    lonstr = str(lon).rjust(3, "0")
    latstr = f"N{latstr}" if lat >= 0 else f"S{abs(latstr)}"
    lonstr = f"E{lonstr}" if lon >= 0 else f"W{abs(lonstr)}"

    return latstr, lonstr


def get_filename_canopy_height(
    lat: Union[int, float],
    lon: Union[int, float]
    ) -> str:
    """Get the right filename for the ETH canopy height dataset.

    The dataset is split up in 3 degree ^2 files. This makes the output filename, for
    example with the coordinates (52N, 4E):
        ETH_GlobalCanopyHeight_10m_2020_51N003E_Map.tif"

    Note: There are no files when there is only oceans/seas in the gridcell. This
        function does not take that into account.

    Args:
        lat: Latitude of the location for which the filename should be retrieved.
        lon: Longitude of the location for which the filename should be retrieved.

    Returns:
        str: Properly formatted filename for a valid ETH GlobalCanopyHeight file.
    """
    latstr, lonstr = make_lat_lon_strings(lat, lon, step=3)
    return f"ETH_GlobalCanopyHeight_10m_2020_{latstr}{lonstr}_Map.tif"


def get_filename_dem(
    lat: Union[int, float],
    lon: Union[int, float]
    ) -> str:
    """Get the right filename for the Copernicus prism DEM dataset.

    The dataset is split up in 1 degree ^2 files. This makes the output filename, for
    example with the coordinates (52N, 4E):
        Copernicus_DSM_30_N52_00_E004_00_DEM.tif"

    Note: There are no files when there is only oceans/seas in the gridcell. This
        function does not take that into account.

    Args:
        lat: Latitude of the location for which the filename should be retrieved.
        lon: Longitude of the location for which the filename should be retrieved.

    Returns:
        str: Properly formatted filename for a valid ETH GlobalCanopyHeight file.
    """
    latstr, lonstr = make_lat_lon_strings(lat, lon, step=1)
    return f"Copernicus_DSM_30_{latstr}_00_{lonstr}_00_DEM.tif"


def extract_era5_data(  # pylint: disable=too-many-arguments
    files_era5: List,
    files_era5_land: List,
    lat: Union[int, float],
    lon: Union[int, float],
    start_time: np.datetime64,
    end_time: np.datetime64,
    ) -> Dict:
    """Extracts and converts the required variables from the era5 data.

    Args:
        files_era5: List of era5 files.
        lat: Latitude of the site
        lon: Longitude of the site
        start_time: Start time of the model run
        end_time: End time of the model run

    Returns:
        Dictionary containing the variables extracted from era5.
    """
    datasets = []
    for files in (files_era5, files_era5_land):
        ds = xr.open_mfdataset(files)
        ds = ds.sel(latitude=lat, longitude=lon, method='nearest').compute()
        ds = ds.resample(time=TIMESTEP).interpolate('linear')
        ds = ds.sel(time=slice(start_time, end_time))
        ds = ds.drop(['latitude', 'longitude'])
        datasets.append(ds)
    ds = xr.merge(datasets)

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


def extract_cams_data(
    files_cams: List,
    lat: Union[int, float],
    lon: Union[int, float],
    start_time: np.datetime64,
    end_time: np.datetime64,
    ) -> xr.DataArray:
    """Extracts and converts the required variables from the CAMS CO2 dataset.

    Args:
        files_cams: List of era5 files.
        lat: Latitude of the site.
        lon: Longitude of the site.
        start_time: Start time of the model run.
        end_time: End time of the model run.

    Returns:
        DataArray containing the CO2 concentration.
    """
    ds = xr.open_mfdataset(files_cams)
    ds = ds.sel(latitude=lat, longitude=lon, method='nearest')
    ds = ds.drop(['latitude', 'longitude'])
    ds = ds.resample(time=TIMESTEP).interpolate('linear')
    ds = ds.sel(time=slice(start_time, end_time))
    return ds.co2


def extract_prism_dem_data(
    file_dem: Path,
    lat: Union[int, float],
    lon: Union[int, float],
    ) -> float:
    """Extracts the elevation from the PRISM DEM dataset.

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


def extract_canopy_height_data(
    file_canopy_height: Path,
    lat: Union[int, float],
    lon: Union[int, float],
    ) -> float:
    """Extracts the canopy height from the ETH global canopy height dataset.

    Args:
        file_canopy_height: The canopy height .tiff file.
        lat: Latitude of the site.
        lon: Longitude of the site.

    Returns:
        Canopy height at the location.
    """
    da = xr.open_dataarray(file_canopy_height, engine="rasterio")

    pad = 0.05  # Add padding around the data before trying to find nearest non-nan
    da = da.sel(y=slice(lat + pad, lat - pad), x=slice(lon - pad, lon + pad))
    canopy_height = utils.find_nearest_non_nan(da.compute(), x=lon, y=lat)
    return canopy_height.values[0]


def extract_lai_data(
    files_lai: List,
    lat: Union[int, float],
    lon: Union[int, float],
    start_time: np.datetime64,
    end_time: np.datetime64,
    ) -> xr.DataArray:
    """Extracts the LAI from the FAPAR dataset.

    Args:
        files_lai: List of paths to the *.nc files.
        lat: Latitude of the site.
        lon: Longitude of the site.
        start_time: Start time of the model run.
        end_time: End time of the model run.

    Returns:
        DataArray containing the LAI of the specified site for the given timeframe.
    """
    ds = xr.open_mfdataset(files_lai)

    pad = 0.2  # Add padding around the data before trying to find nearest non-nan
    ds = ds.sel(lat=slice(lat + pad, lat - pad), lon=slice(lon - pad, lon + pad))
    ds = ds.resample(time=TIMESTEP).interpolate('linear')
    ds = ds.sel(time=slice(start_time, end_time)).compute()
    return utils.find_nearest_non_nan(ds["LAI"], x=lon, y=lat, xdim="lon", ydim="lat")

from pathlib import Path
import hdf5storage
import numpy as np
import xarray as xr
from . import utils
from . import variable_conversion as vc
from typing import Union
from typing import Tuple
from typing import Dict
from glob import glob
from typing import List


def _write_matlab_ascii(fname, data, ncols):
    """Internal function to handle writing data in the Matlab ascii format. Equivalent
    to `save([-], '-ascii')` in Matlab.

    Args:
        fname (path or str): Path to the file that should be written
        data (np.array): Array with data to write to file
        ncols (int, optional): The number of data columns, required to correctly format
            the ascii file when writing multiple variables.
    """
    matlab_fmt = ' %14.7e'
    multi_fmt = [matlab_fmt]*ncols
    multi_fmt[0] = f' {multi_fmt[0]}'
    np.savetxt(fname, data, multi_fmt)


def read_forcing_data_plumber2(forcing_file):
    """Reads the forcing data from the provided netCDF file, and applies the required
    unit conversions before returning the read data.

    Args:
        forcing_file (Path): Path to the netCDF file containing the forcing data

    Returns:
        dict: Dictionary containing the different variables required by STEMMUS_SCOPE
            for the different forcing files.
    """
    ds_forcing = xr.open_dataset(forcing_file)

    # remove the x and y coordinates from the data variables to make the numpy arrays 1D
    ds_forcing = ds_forcing.squeeze(['x', 'y'])

    data = {}

    # Expected time format is days (as floating point) since Jan 1st 00:00.
    data['doy_float'] = (
        ds_forcing['time'].dt.dayofyear - 1 +
        ds_forcing['time'].dt.hour/24 +
        ds_forcing['time'].dt.minute/60/24
    )
    data['year'] = ds_forcing['time'].dt.year.astype(float)

    data['t_air_celcius'] = ds_forcing['Tair'] - 273.15 # conversion from K to degC.
    data['psurf_hpa'] = ds_forcing['Psurf'] / 100 # conversion from Pa to hPa
    data['co2_conv'] = vc.co2_molar_fraction_to_kg_per_m3(ds_forcing['CO2air'])
    data['precip_conv'] = ds_forcing['Precip'] / 10 # conversion from mm/s to cm/s
    data['lw_down'] = ds_forcing['LWdown']
    data['sw_down'] = ds_forcing['SWdown']
    data['wind_speed'] = ds_forcing['Wind']
    data['rh'] = ds_forcing['RH']
    data['vpd'] = ds_forcing['VPD']
    data['lai'] = vc.mask_data(ds_forcing['LAI'], min_value=0.01)

    # calculate ea, conversion from kPa to hPa:
    data['ea'] = vc.calculate_ea(data['t_air_celcius'], data['rh']) * 10

    # Load in non-timedependent variables
    data['sitename'] = forcing_file.name.split('_')[0]

    # Forcing data timestep size in seconds
    time_delta = (ds_forcing.time.values[1] -
                  ds_forcing.time.values[0]) / np.timedelta64(1, 's')
    data['DELT'] = time_delta.astype(float)
    data['total_timesteps'] = ds_forcing.time.size

    data['latitude'] = ds_forcing['latitude'].values
    data['longitude'] = ds_forcing['longitude'].values
    data['elevation'] = ds_forcing['elevation'].values
    data['IGBP_veg_long'] = ds_forcing['IGBP_veg_long'].values
    data['reference_height'] = ds_forcing['reference_height'].values
    data['canopy_height'] = ds_forcing['canopy_height'].values

    # these are needed by save.py
    data['time'] = ds_forcing["time"]
    data['Qair'] = ds_forcing['Qair']

    return data


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

    latstr = f"{lat}N" if lat >= 0 else f"{abs(lat)}S"
    lonstr = f"{lon}E" if lon >= 0 else f"{abs(lon)}W"

    latstr = latstr.rjust(3, "0")
    lonstr = lonstr.rjust(4, "0")

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


def extract_era5_data(
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
        ds = ds.resample(time="1800S").interpolate('linear')
        ds = ds.sel(time=slice(start_time, end_time))
        ds = ds.drop(['latitude', 'longitude'])
        datasets.append(ds)
    ds = xr.merge(datasets)

    data = {}
    data["wind_speed"] = (ds["u10"] ** 2 + ds["v10"] ** 2) ** 0.5
    data["t_air_celcius"] = ds["t2m"] - 273.15  # K -> degC
    data["precip"] = ds["mtpr"] / 10  # mm/s -> cm/s
    data["p_surf"] = ds["sp"] / 1000  # Pa -> kPa
    data["sw_down"] = ds["ssrd"] / 3600  # J * hr / m2 ->  W / m2
    data["lw_down"] = ds["strd"] / 3600  # J * hr / m2 ->  W / m2

    data["ea"] = vc.calculate_es(ds["d2m"] - 273.15)
    data["vpd"] = vc.calculate_es(data["t_air_celcius"]) - data["ea"]
    data["rh"] = data["ea"] / vc.calculate_es(data["t_air_celcius"])
    data["qair"] = vc.specific_humidity(data["ea"], data["p_surf"])

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
        lat: Latitude of the site
        lon: Longitude of the site
        start_time: Start time of the model run
        end_time: End time of the model run

    Returns:
        DataArray containing the CO2 concentration.
    """
    ds = xr.open_mfdataset(files_cams)
    ds = ds.sel(latitude=lat, longitude=lon, method='nearest')
    ds = ds.drop(['latitude', 'longitude'])
    ds = ds.resample(time="1800S").interpolate('linear')
    ds = ds.sel(time=slice(start_time, end_time))
    return ds.co2  # TODO: Unit conversion from kg/kg


def extract_prism_dem_data(
    file_dem: Path,
    lat: Union[int, float],
    lon: Union[int, float],
    ) -> float:
    ds = xr.open_dataarray(file_dem, engine="rasterio")
    elevation = ds.sel(x=lon, y=lat, method="nearest")
    return elevation.values[0]


def extract_canopy_height_data(
    file_canopy_height: Path,
    lat: Union[int, float],
    lon: Union[int, float],
    ) -> float:
    da = xr.open_dataarray(file_canopy_height, engine="rasterio")
    canopy_height = utils.find_nearest_non_nan(da, x=lon, y=lat)
    return canopy_height.values[0]


def extract_lai_data(files_lai, lat, lon, start_time, end_time):
    ds = xr.open_mfdataset(files_lai)

    pad = 0.2  # Add padding around the data before trying to find nearest non-nan
    ds = ds.sel(lat=slice(lat + pad, lat - pad), lon=slice(lon - pad, lon + pad))
    ds = ds.resample(time="1800S").interpolate('linear')
    ds = ds.sel(time=slice(start_time, end_time))
    return utils.find_nearest_non_nan(ds["LAI"], x=lon, y=lat, xdim="lon", ydim="lat")


def read_forcing_data_global(
    global_data_dir: Path,
    lat: float,
    lon: float,
    start_time: np.datetime64,
    end_time: np.datetime64,
    ) -> Dict:

    files_cams = glob(global_data_dir / "co2" / "*.nc")
    file_canopy_height = (global_data_dir / "canopy_height" /
        get_filename_canopy_height(lat, lon))
    file_dem = (global_data_dir / "canopy_height" / get_filename_dem(lat, lon))
    files_era5 = glob(global_data_dir / "era5" / "*.nc")
    files_era5land = glob(global_data_dir / "era5-land" / "*.nc")
    files_lai = glob(global_data_dir / "lai" / "*.nc")

    data = {}

    era5_data = extract_era5_data(
        files_era5, files_era5land, lat, lon, start_time, end_time
    )
    data = {**data, **era5_data}

    data["co2"] = extract_cams_data(files_cams, lat, lon, start_time, end_time)

    data["LAI"] = vc.mask_data(
        extract_lai_data(files_lai, lat, lon, start_time, end_time),
        min_value=0.01
    )

    data["elevation"] = extract_prism_dem_data(file_dem, lat, lon)

    data["canopy_height"] = extract_canopy_height_data(file_canopy_height, lat, lon)
    data["reference_height"] = 0.7 * data["canopy_height"]

    data["sitename"] = "StemmusScope_Global"

    data["doy_float"] = ...  # days (as floating point) since Jan 1st 00:00.
    data["year"] = ...  # ds_forcing['time'].dt.year.astype(float)

    # data['t_air_celcius'] = ds_forcing['Tair'] - 273.15 # conversion from K to degC.
    # data['psurf_hpa'] = ds_forcing['Psurf'] / 100 # conversion from Pa to hPa
    # data['co2_conv'] = vc.co2_molar_fraction_to_kg_per_m3(ds_forcing['CO2air'])
    # data['precip_conv'] = ds_forcing['Precip'] / 10 # conversion from mm/s to cm/s
    # data['lw_down'] = ds_forcing['LWdown']
    # data['sw_down'] = ds_forcing['SWdown']
    # data['wind_speed'] = ds_forcing['Wind']
    # data['rh'] = ds_forcing['RH']
    # data['vpd'] = ds_forcing['VPD']
    # data['lai'] = vc.mask_data(ds_forcing['LAI'], min_value=0.01)

    # # calculate ea, conversion from kPa to hPa:
    # data['ea'] = vc.calculate_ea(data['t_air_celcius'], data['rh']) * 10

    # # Forcing data timestep size in seconds
    # time_delta = (ds_forcing.time.values[1] -
    #               ds_forcing.time.values[0]) / np.timedelta64(1, 's')
    # data['DELT'] = time_delta.astype(float)
    # data['total_timesteps'] = ds_forcing.time.size

    # data['latitude'] = ds_forcing['latitude'].values
    # data['longitude'] = ds_forcing['longitude'].values
    # data['IGBP_veg_long'] = ds_forcing['IGBP_veg_long'].values

    # # these are needed by save.py
    # data['time'] = ds_forcing["time"]
    # data['Qair'] = ds_forcing['Qair']

    # return data



def write_dat_files(data, input_dir):
    """Fuction to write the single-data .dat files for the STEMMUS_SCOPE matlab model.

    Args:
        data (dict): Data dictionary generated by read_forcing
        input_dir (path or str): Directory to which the different single-column .dat
            files should be written to.
    """
    write_info = {
        'doy_float': 't_.dat',
        't_air_celcius': 'Ta_.dat',
        'sw_down': 'Rin_.dat',
        'lw_down': 'Rli_.dat',
        'psurf_hpa': 'p_.dat',
        'wind_speed': 'u_.dat',
        'co2_conv': 'CO2_.dat',
        'ea': 'ea_.dat',
        'year': 'year_.dat'
    }
    for var, fname in write_info.items():
        fpath = Path(input_dir) / fname
        _write_matlab_ascii(fpath, data[var], ncols=1)


def write_lai_file(data, fname):
    """Function to write the ascii LAI_.dat file for STEMMUS_SCOPE.

    Args:
        data (dict): Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        fname (Path): Full path, including filename, to which the file should be
            written to.
    """
    lai_file_data = np.vstack([data['doy_float'], data['lai']]).T
    _write_matlab_ascii(fname, lai_file_data, ncols=2)


def write_meteo_file(data, fname):
    """Function to write the ascii Mdata.txt meteo file for STEMMUS_SCOPE.

    Args:
        data (dict): Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        fname (Path): Full path, including filename, to which the file should be
            written to.
    """
    meteo_data_vars = ['doy_float', 't_air_celcius', 'rh',
        'wind_speed', 'psurf_hpa', 'precip_conv', 'sw_down',
        'lw_down', 'vpd', 'lai']
    meteo_file_data = np.vstack([data[var] for var in meteo_data_vars]).T
    _write_matlab_ascii(fname, meteo_file_data, ncols=len(meteo_data_vars))


def prepare_global_variables(data, input_path, config):
    """Function to read and calculate global variables for STEMMUS_SCOPE from the
    forcing data. Data will be written to a Matlab binary file (v7.3), under the name
    'forcing_globals.mat' in the specified input directory.

    Args:
        data (dict): Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        input_path (Path): Path to which the file should be written to.
        config (dict): The PyStemmusScope configuration dictionary.
    """
    if config['NumberOfTimeSteps'] != 'NA':
        total_duration = min(int(config['NumberOfTimeSteps']), data['total_timesteps'])
    else:
        total_duration = data['total_timesteps']

    matfile_vars = ['latitude', 'longitude', 'elevation', 'IGBP_veg_long',
                    'reference_height', 'canopy_height', 'DELT', 'sitename']
    matfiledata = {key: data[key] for key in matfile_vars}

    matfiledata['Dur_tot'] = float(total_duration) # Matlab expects a 'double'

    hdf5storage.savemat(input_path / "forcing_globals.mat", matfiledata, appendmat=False)
    utils.remove_dates_from_header(input_path / "forcing_globals.mat")


def prepare_forcing(config):
    """Function to prepare the forcing files required by STEMMUS_SCOPE. The input
        directory should be taken from the model configuration file.

    Args:
        config (dict): The PyStemmusScope configuration dictionary.
    """

    input_path = Path(config["InputPath"])

    # Read the required data from the forcing file into a dictionary
    forcing_file = Path(config["ForcingPath"]) / config["ForcingFileName"]
    data = read_forcing_data_plumber2(forcing_file)

    # Write the single-column ascii '.dat' files to the input directory
    write_dat_files(data, input_path)

    # Write the two-column LAI_.dat file to the input directory.
    write_lai_file(data, input_path / 'LAI_.dat')

    # Write the multi-column Mdata.txt ascii file to the input directory
    write_meteo_file(data, input_path / 'Mdata.txt')

    # Write the remaining variables (without time dependency) to the matlab v7.3
    #  file 'forcing_globals.mat'
    prepare_global_variables(data, input_path, config)

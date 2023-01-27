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
import pandas as pd
from . import global_data_selection as gds

TIMESTEP = "1800S"


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


def read_forcing_data_plumber2(forcing_file, start_time, end_time):
    """Reads the forcing data from the provided netCDF file, and applies the required
    unit conversions before returning the read data.

    Args:
        forcing_file (Path): Path to the netCDF file containing the forcing data
        start_time (str): Start of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.
        end_time (str): End of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.

    Returns:
        dict: Dictionary containing the different variables required by STEMMUS_SCOPE
            for the different forcing files.
    """
    ds_forcing = xr.open_dataset(forcing_file)
    ds_forcing = ds_forcing.sel(time=slice(start_time, end_time))

    # remove the x and y coordinates from the data variables to make the numpy arrays 1D
    ds_forcing = ds_forcing.squeeze(['x', 'y'])

    # check if time range is covered by forcing
    # if so, return a subset of forcing matching the given time range
    ds_forcing = _slice_forcing_file(
        ds_forcing,
        start_time,
        end_time,
        )

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


def read_forcing_data_global(
    global_data_dir: Path,
    lat: float,
    lon: float,
    start_time: np.datetime64,
    end_time: np.datetime64,
    ) -> Dict:
    """Read forcing data for a certain location, based on global datasets.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        lat: Latitude of the site of interest.
        lon: Longitude of the site of interest.
        start_time: Start time of the model run.
        end_time: End time of the model run.

    Returns:
        Dictionary containing the forcing data.
    """

    files_cams = list((global_data_dir / "co2").glob("*.nc"))
    file_canopy_height = (global_data_dir / "canopy_height" /
        gds.get_filename_canopy_height(lat, lon))
    file_dem = (global_data_dir / "dem" / gds.get_filename_dem(lat, lon))
    files_era5 = list((global_data_dir / "era5").glob("*.nc"))
    files_era5land = list((global_data_dir / "era5-land").glob("*.nc"))
    files_lai = list((global_data_dir / "lai").glob("*.nc"))

    data = {
        "time": xr.DataArray(
            pd.date_range(str(start_time), str(end_time), freq=TIMESTEP).rename("time")
        )
    }
    era5_data = gds.extract_era5_data(
        files_era5, files_era5land, lat, lon, start_time, end_time
    )
    data = {**data, **era5_data}

    data["co2_conv"] = vc.co2_mass_fraction_to_kg_per_m3(
        gds.extract_cams_data(files_cams, lat, lon, start_time, end_time)
    )

    # data["lai"] = vc.mask_data(
    #     gds.extract_lai_data(files_lai, lat, lon, start_time, end_time),
    #     min_value=0.01
    # )

    data["elevation"] = gds.extract_prism_dem_data(file_dem, lat, lon)

    data["canopy_height"] = gds.extract_canopy_height_data(file_canopy_height, lat, lon)
    data["reference_height"] = 0.7 * data["canopy_height"]

    data["sitename"] = "StemmusScope_Global"

    # Expected time format is days (as floating point) since Jan 1st 00:00.
    data['doy_float'] = (
        data['time'].dt.dayofyear - 1 +
        data['time'].dt.hour/24 +
        data['time'].dt.minute/60/24
    )
    data['year'] = data['time'].dt.year.astype(float)

    data['DELT'] = (
        (
            data['time'].values[1] -
            data['time'].values[0]
        ) / np.timedelta64(1, 's')
        ).astype(float)
    data['total_timesteps'] = data['time'].size

    data['latitude'] = lat
    data['longitude'] = lon

    # TODO: Add land cover data retrieval.
    data['IGBP_veg_long'] = "Evergreen Needleleaf Forests"

    return data


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


def prepare_global_variables(data, input_path):
    """Function to read and calculate global variables for STEMMUS_SCOPE from the
    forcing data. Data will be written to a Matlab binary file (v7.3), under the name
    'forcing_globals.mat' in the specified input directory.

    Args:
        data (dict): Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        input_path (Path): Path to which the file should be written to.
        config (dict): The PyStemmusScope configuration dictionary.
    """
    total_duration = data['total_timesteps']

    matfile_vars = ['latitude', 'longitude', 'elevation', 'IGBP_veg_long',
                    'reference_height', 'canopy_height', 'DELT', 'sitename']
    matfiledata = {key: data[key] for key in matfile_vars}

    matfiledata['Dur_tot'] = float(total_duration) # Matlab expects a 'double'

    hdf5storage.savemat(input_path / "forcing_globals.mat", matfiledata, appendmat=False)
    utils.remove_dates_from_header(input_path / "forcing_globals.mat")


def prepare_forcing(config):
    """Function to prepare the forcing files required by STEMMUS_SCOPE.

    The input directory should be taken from the model configuration file.
    A subset of forcing file will be generated if the time range is covered
    by the time of existing forcing file.

    Args:
        config (dict): The PyStemmusScope configuration dictionary.
    """

    input_path = Path(config["InputPath"])

    # Read the required data from the forcing file into a dictionary
    forcing_file = utils.get_forcing_file(config)
    data = read_forcing_data_plumber2(
        forcing_file,
        config["StartTime"],
        config["EndTime"]
    )

    # Write the single-column ascii '.dat' files to the input directory
    write_dat_files(data, input_path)

    # Write the two-column LAI_.dat file to the input directory.
    write_lai_file(data, input_path / 'LAI_.dat')

    # Write the multi-column Mdata.txt ascii file to the input directory
    write_meteo_file(data, input_path / 'Mdata.txt')

    # Write the remaining variables (without time dependency) to the matlab v7.3
    #  file 'forcing_globals.mat'
    prepare_global_variables(data, input_path)


def _slice_forcing_file(ds_forcing, start_time, end_time):
    """Get the subset of forcing file based on time range in config

    Also check if the desired time range is covered by forcing file.

    Args:
        ds_forcing (xr.Dataset): Dataset of forcing file.
        start_time (str): Start of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.
            If "NA", start time will be the first timestamp of the forcing input data.
        end_time (str): End of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.
            If "NA", end time will be the last timestamp of the forcing input data.

    Returns:
        Forcing dataset, sliced with the start and end time.
    """
    start_time = None if start_time == "NA" else np.datetime64(start_time)
    end_time = None if end_time == "NA" else np.datetime64(end_time)

    start_time_forcing = ds_forcing.coords["time"].values[0]
    end_time_forcing = ds_forcing.coords["time"].values[-1]

    start_time_valid = start_time >= start_time_forcing if start_time else True
    end_time_valid = end_time <= end_time_forcing if end_time else True
    if not (start_time_valid and end_time_valid):
        raise ValueError(
            f"Given time range (from {start_time} to {end_time}) cannot be covered by"
            f"the time range of forcing file (from {start_time_forcing} to "
            f"{end_time_forcing}).")

    return ds_forcing.sel(time=slice(start_time, end_time))

import os
import numpy as np
import xarray as xr


def _calculate_ea(t_air_celcius, rh):
    """Internal function that calculates the actual vapour pressure (kPa) from the
    air temperature (degree Celcius) and relative humidity (%)

    Args:
        t_air_celcius: numpy array containing the air temperature in degrees C.

        rh: numpy array of same shape as t_air_celcius, containing the relative humidity
            as a percentage (e.g. ranging from 0 - 100).

    Returns:
        numpy array with the calculated actual vapor pressure
    """
    es = 6.107 * 10**(t_air_celcius*7.5 / (237.3+t_air_celcius))
    return es * rh/100


def read_forcing_data(forcing_file):
    """Reads the forcing data from the provided netCDF file, and applies the required
    unit conversions before returning the read data.

    Args:
        forcing_file (str or path): _description_

    Returns:
        _type_: _description_
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

    data['t_air_celcius'] = ds_forcing['Tair'] - 273.15
    # convert air pressure from Pa to hPa
    data['psurf_hpa'] = ds_forcing['Psurf'] / 100

    # convert CO2 concentration from 'mole fraction' to ?
    data['co2_conv'] = ds_forcing['CO2air'] * 44 / 22.4

    # convert precipitation from [kg/m2/s] to ?
    data['precip_conv'] = ds_forcing['Precip'] / 10

    data['lw_down'] = ds_forcing['LWdown']
    data['sw_down'] = ds_forcing['SWdown']
    data['wind_speed'] = ds_forcing['Wind']
    data['rh'] = ds_forcing['RH']
    data['vpd'] = ds_forcing['VPD']

    data['lai'] = ds_forcing['LAI']
    data['lai'][data['lai']<0.01] = 0.01

    data['ea'] = _calculate_ea(data['t_air_celcius'], data['rh'])

    return data


def write_dat_files(data, input_dir, fmt='  %14.7e'):
    """Fuction to write the single-data .dat files for the STEMMUS_SCOPE matlab model.

    Args:
        data (dict): _description_
        input_dir (path): _description_
        fmt (str, optional): Formatting to use in . Defaults to '  %14.7e'.
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
        fpath = os.path.join(input_dir, fname)
        np.savetxt(fpath, data[var], fmt)


def write_lai_file(data, fname, fmt='  %14.7e'):
    lai_file_data = np.vstack([data['doy_float'], data['lai']]).T
    np.savetxt(fname, lai_file_data, fmt)


def write_meteo_file(data, fname, fmt='  %14.7e'):
    meteo_data_vars = ['doy_float', 't_air_celcius', 'rh',
        'wind_speed', 'psurf_hpa', 'precip_conv', 'sw_down',
        'lw_down', 'vpd', 'lai']
    meteo_file_data = np.vstack([data[var] for var in meteo_data_vars]).T
    np.savetxt(fname, meteo_file_data, fmt)
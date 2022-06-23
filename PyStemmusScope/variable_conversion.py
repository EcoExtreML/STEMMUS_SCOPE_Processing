import numpy as np


def calculate_ea(t_air_celcius, rh):
    """Function that calculates the actual vapour pressure (kPa) from the
    air temperature (degree Celcius) and relative humidity (%)

    Args:
        t_air_celcius: numpy array containing the air temperature in degrees C.

        rh: numpy array of same shape as t_air_celcius, containing the relative humidity
            as a percentage (e.g. ranging from 0 - 100).

    Returns:
        numpy array with the calculated actual vapor pressure
    """
    # Teten O. Über einige meteorologische Begriffe. Z. Geophys., 1930; 6. 297-309.
    # Murray FW. On the computation of saturation vapor pressure,
    #   J. Appl. Meteorol., 1967; 6, 203-204
    es = 6.1078 * 10**(t_air_celcius*7.5 / (237.3+t_air_celcius))
    return es * rh/100


def kpa_to_hpa(pressure):
    """Function to convert pressure data in kPa to hPa.

    Args:
        pressure (xr.DataArray): DataArray with pressure values in [kPa].

    Returns:
        xr.DataArray: Pressure data [hPa].

    Raises:
        ValueError if the input pressure is not in [kPa]
    """
    if pressure.units == 'kPa':
        return pressure * 10
    raise ValueError('Input pressure is not in [kPa]')


def pa_to_hpa(pressure):
    """Function to convert pressure data in Pa to hPa.

    Args:
        pressure (xr.DataArray): DataArray with pressure values in Pascal.

    Returns:
        xr.DataArray: Pressure data [hPa].

    Raises:
        ValueError if the input pressure is not in Pascal
    """
    if pressure.units == 'Pa':
        return pressure / 100
    raise ValueError('Input pressure is not in [Pa]')


def kelvin_to_celcius(temperature):
    """Function to convert temperature data in Kelvin to deg Celcius

    Args:
        temperature (xr.DataArray): DataArray with temperature values in Kelvin.

    Returns:
        xr.DataArray: Temperature in degrees Celcius.

    Raises:
        ValueError if the input temperature is not in Kelvin
    """
    if temperature.units=='K':
        return temperature - 273.15
    raise ValueError('Input temperature is not in [K]')


def co2_molar_fraction_to_kg_per_m3(molar_fraction):
    """Function to convert CO2 molar fraction [mol cO2/mol air] to CO2
    concentration in [kg CO2 / m3 air]

    Note: the density of air [kg/m3] used for the calculation is assumed to be constant
    here, but will vary depending on the air pressure and air temperature.

    Args:
        molar_fraction (float, np.array): CO2 concentration as molar fraction

    Returns:
        Same as input: CO2 concentration in [kg CO2 / m3 air]
    """
    molecular_weight_co2 = 44.01 # [kg/mol]
    avg_density_air = 1.292 # [kg/m3]
    avg_molar_mass_air = 28.9647 # [kg/mol]
    molar_density_air = avg_molar_mass_air / avg_density_air # [m3/mol]
    return molar_fraction * molecular_weight_co2 / molar_density_air


def precipitation_mm_s_to_cm_s(precipitation_rate):
    """Function to convert precipitation rate in [kg/m2/s] or [mm/s] to [cm/s]

    Args:
        precipitation_rate (float, np.array): Precipitation rate in [kg/m2/s] or [mm/s].

    Returns:
        Same as input: Precipitation rate in [cm/s]
    """
    return precipitation_rate/10


def mask_data(data, min_value=None, max_value=None):
    """Function to apply a mask to data.

    Args:
        data (np.array): Array containing the original data.
        condition (np.array): Boolean array to mask the data with.
        value (float): Value to replaced the masked data with.

    Returns:
        np.array: Array where the values under the mask have been replaced with the
            given value.
    """
    return np.clip(data, min_value, max_value)

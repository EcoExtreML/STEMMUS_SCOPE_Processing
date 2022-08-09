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

    # check rh values
    if rh.min() < 0.0 or rh.max() > 100.0:
        raise ValueError("relative humidity should be in percentage ranging from 0 - 100")

    # check lengths
    if rh.shape != t_air_celcius.shape:
        raise ValueError("input arrays should have the same shape (size).")

    es = 0.61078 * 10 ** (t_air_celcius * 7.5 / (237.3 + t_air_celcius))
    return es * rh / 100


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


def field_moisture_content(theta_r, theta_s, alpha, coef_n):
    """Calculates the field moisture content at the field capacity, based on the Van
    Genuchten equation.

    See:
        Genuchten, V. , & Th., M. . (1980). A closed-form equation for predicting the
        hydraulic conductivity of unsaturated soils. Soil Science Society of America
        Journal, 44(5), 892-898.

    Args:
        theta_r (float or np.array): Residual water content of the soil
        theta_s (float or np.array): Saturated water content of the soil
        alpha (float or np.array): Parameter related to the inverse of the air entry suction
        coef_n (float or np.array): Pore-size distribution coefficient

    Returns:
        float or np.array: Field moisture content
    """
    phi_fc = 341.9 # soil water potential at field capacity (cm)

    field_moisture_content = theta_r + (theta_s - theta_r)/(
        1 + (alpha * phi_fc)**coef_n
        )**(1 -1/coef_n)

    return field_moisture_content


def soil_moisture(volumetric_water_content:np.array, thickness:np.array) -> np.array:
    """Calculates the soil moisture (kg/m2) from volumetric water content(m3/m3), based on SM =
        VolumetricWaterContent * Density * Thickness.

    Args:
        volumetric_water_content(np.array): volumetric water content in m3/m3
        thickness(np.array): soil layer thickness in m

    Returns:
        np.array: soil moisture in kg/m2
    """
    # check lengths
    if volumetric_water_content.shape != thickness.shape:
        raise ValueError("input arrays should have the same shape (size).")

    # Density: constant (water_density = 1000 kg per m3)
    return  (1000.0 * volumetric_water_content * thickness)

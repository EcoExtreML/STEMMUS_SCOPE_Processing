"""PyStemmusScope save module.

Module designed to create a netcdf file (following ALMA cf convention) from csv
files (following SCOPE format) in the output directory.

https://scope-model.readthedocs.io/en/latest/outfiles.html
https://web.lmd.jussieu.fr/~polcher/ALMA/convention_output_3.html
"""

import logging
from pathlib import Path
from typing import Dict
from typing import List
import numpy as np
import pandas as pd
import xarray as xr
from PyStemmusScope import forcing_io
from . import variable_conversion as vc


logger = logging.getLogger(__name__)


def _select_forcing_variables(forcing_dict: Dict, forcing_var: str, alma_var: str) -> xr.DataArray:
    """Select the variable needed by ALMA convention.

    Args:
        forcing_dict(dict): a dictionary returned by `PyStemmusScope.forcing_io.read_forcing_data()`.
        forcing_var(str): variable name in forcing dataset.
        alma_var(str): variable name in ALMA convention.

    Returns:
        xr.DataArray: a data array which its variable name is alma_name.
    """

    # select the forcing variable
    data_array = forcing_dict[forcing_var]

    # rename the variable name to alma_name
    data_array = data_array.rename(alma_var)
    return data_array


def _resize_data_array(data: xr.DataArray, time_steps: str)-> xr.DataArray:
    """Resize data based on time_steps.

    Args:
        data(xr.DataArray): data to be resized.
        time_steps(str): number of time steps to resize.

    Returns:
        xr.DataArray: subset of data with the lenght of time equal to time_steps.
    """

    if time_steps != "NA":
        time_length = int(time_steps)
        data = data.isel(time=np.arange(0, time_length))

    return data


def _prepare_4d_data(file_name: str, var_name: str, time: List) -> xr.DataArray:
    """Reshape a `pandas.DataFrame` to include z dimension.

    Args:
        file_name(str): csv file name generated by Stemmus_Scope model.
        var_name(str): variable name by ALMA convention.
        time(list): time values to be used for the time coordinates.

    Returns:
        xr.DataArray: a dataarray with two dimensions of time and z.
    """
    # the first two rows are depth and thickness
    data = pd.read_csv(file_name, delimiter=",", header=[0, 1])

    # skip first row that is unit
    data = data.iloc[1:]

    # make sure it is float and not str
    data = data.astype('float32')

    # get depth, thickness info
    depths = []
    thicknesses = []
    for depth, thickness in data.columns:
        depths.append(np.float32(depth))
        thicknesses.append(np.float32(thickness))

    # soil layer metadata
    soil_metadata = _create_soil_layer_metadata(thicknesses, depths)

    # drop thickness
    data = data.droplevel(level=1, axis=1)

    if var_name == "SoilTemp":
        # Celsius to Kelvin : K = 273.15 + C
        data = data + 273.15

    elif var_name == "SoilMoist":
        # cm to m
        thicknesses = np.array(thicknesses) / 100.0

        for index in data.index:
            # m3/m3 to kg/m2
            volumetric_water_content = np.array(data.loc[index])
            data.loc[index] = vc.soil_moisture(volumetric_water_content, thicknesses)

    # reshape the data frame
    data = data.stack()

    # set values
    layers = range(1, data.index.levshape[1] + 1)
    data.index.names = ["time", "z"]
    data.index = data.index.set_levels([time, layers], level=["time", "z"])
    data.name = var_name

    # convert dataframe to xarray data array
    data_array = data.to_xarray()

    # add z attributes
    data_array["z"].attrs = {
        "long_name": "Soil layer",
        "standard_name": "Soil layer",
        "definition": soil_metadata,
        "units": "-",
    }

    return data_array


def _prepare_3d_data(file_name: str, model_name: str, alma_name: str, time: List) ->  xr.DataArray:
    """Reshape a `pandas.DataFrame` to include z dimension.

    Args:
        file_name(str): csv file name generated by Stemmus_Scope model.
        model_name(str): variable name by Stemmus_Scope model.
        alma_name(str): variable name by ALMA conventions.
        time(list): time values to be used for the time coordinates.

    Returns:
        xr.DataArray: a dataarray with one dimension of time.
    """
    # the first three rows are names and units
    data = pd.read_csv(file_name, delimiter=",")

    # select variable and skip first row that is unit
    data = data[model_name].iloc[1:]

    # set time values
    data.index = time
    data.index.names = ["time"]

    # rename it to alma name
    data.name = alma_name

    # make sure it is float and not str
    data = data.astype('float32')

    # convert dataframe to xarray data array
    return data.to_xarray()


def _create_soil_layer_metadata(thicknesses: List, depths: List) -> List:
    """
    layer_1: 0.0 - 1.0 cm
    layer_2: 1.0 - 2.0 cm
    layer_3: 2.0 - 3.0 cm
    """

    metadata = []
    for index, (thickness, depth) in enumerate(zip(thicknesses, depths)):
        metadata.append(f"layer_{index + 1}: {(depth - thickness)} - {depth} cm")

    return metadata


def _update_dataset_attrs_dims(dataset: xr.Dataset, forcing_dict: Dict) -> xr.Dataset:
    """Update dimentions of a dataset according to ALMA conventions.

    Args:
        dataset(xr.Dataset): a dataset with varaibles in ALMA conventions.

    Returns:
        xr.Dataset: the dataset with dimensions ("time", "x", "y").
    """

    # add x/y dims to the dataset
    dataset_expanded = dataset.expand_dims(["x", "y"])

    # change the order of dims
    try:
        dataset_reordered = dataset_expanded.transpose("time", "y", "x", "z")
    except ValueError:
        try:
            dataset_reordered = dataset_expanded.transpose("time", "y", "x")
        except ValueError as err:
            raise ValueError("Data should have time dimension.") from err

    # additional metadata
    lat = forcing_dict["latitude"]
    lon = forcing_dict["longitude"]
    dataset_reordered.attrs = {
        'model': 'STEMMUS_SCOPE',
        'institution': 'University of Twente; Northwest A&F University',
        'contact': (
            'Zhongbo Su, z.su@utwente.nl; '
            'Yijian Zeng, y.zeng@utwente.nl; '
            'Yunfei Wang, y.wang-3@utwente.nl'
            ),
        'license_type': 'CC BY 4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'latitude': lat,
        'longitude': lon,
        }

    # update values of x and y coords
    dataset = dataset_reordered.assign_coords(
        {
            "x": [lon],
            "y": [lat],
            }
        )

    # update x, y attributes
    dataset["x"].attrs = {
            "long_name": "Gridbox longitude",
            "standard_name": "longitude",
            "units": "degrees",
            }

    dataset["y"].attrs = {
            "long_name": "Gridbox latitude",
            "standard_name": "latitude",
            "units": "degrees",
            }

    return dataset


def to_netcdf(config: Dict, cf_filename: str) -> str:
    """Save csv files generated by Stemmus_Scope model to a netcdf file using
        information provided by ALMA conventions.

    Args:
        config(Dict): PyStemmusScope configuration dictionary.
        cf_filename(str): Path to a csv file for ALMA conventions.

    Returns:
        str: path to a csv file under the output directory.
    """

    # list of required forcing variables, Alma_short_name: forcing_io_name, # model_name
    # they called ECdata
    var_names = {
        "RH": "rh", # RH
        "SWdown_ec": "sw_down", # Rin
        "LWdown_ec": "lw_down", # Rli
        "Qair": "Qair",
        "Tair": "t_air_celcius", # Ta
        "Psurf": "psurf_hpa", # P
        "Wind": "wind_speed", # u
        "Precip": "precip_conv", # Pre
    }

    # Number of time steps from configuration file
    time_steps = config["NumberOfTimeSteps"]

    # read forcing file into a dict
    forcing_dict = forcing_io.read_forcing_data(
        Path(config["ForcingPath"]) / config["ForcingFileName"]
    )

    # get time info
    time = _resize_data_array(forcing_dict["time"], time_steps)

    # read convention file
    conventions = pd.read_csv(cf_filename)

    alma_short_names = conventions["short_name_alma"]
    data_list = []
    for alma_name in alma_short_names:
        df = conventions.loc[alma_short_names == alma_name].iloc[0]
        file_name = Path(config["OutputPath"]) / df["File name"]

        if alma_name in var_names:
            # select data
            data_array = _select_forcing_variables(forcing_dict, var_names[alma_name], alma_name)
            data_array = _resize_data_array(data_array, time_steps)

        # create data array
        elif alma_name in {"SoilTemp", "SoilMoist"}:
            data_array = _prepare_4d_data(file_name, alma_name, time.values)
        else:
            data_array = _prepare_3d_data(
                file_name, df["Variable name in STEMMUS-SCOPE"], alma_name, time.values
                )

        # update attributes of array
        data_array.attrs = {
            "units": df["unit"],
            "long_name": df["long_name"],
            "standard_name": df["standard_name"],
            "STEMMUS-SCOPE_name": df["Variable name in STEMMUS-SCOPE"],
            "definition": df["definition"],
        }

        # add to list
        data_list.append(data_array)

    # merge to a dataset
    dataset = xr.merge(data_list)

    # update dimensions
    dataset = _update_dataset_attrs_dims(dataset, forcing_dict)

    # # save to nc file
    nc_filename = Path(config["OutputPath"]) / f"{Path(config['OutputPath']).stem}_STEMMUS_SCOPE.nc"

    dataset.to_netcdf(path= nc_filename, mode='w')
    return str(nc_filename)

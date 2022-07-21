"""PyStemmusScope save module.

Module designed to create csv files (following SCOPE format) and a netcdf
file (following ALMA cf convention) in the output directory.

https://scope-model.readthedocs.io/en/latest/outfiles.html
https://web.lmd.jussieu.fr/~polcher/ALMA/convention_output_3.html
"""

import logging
import pandas as pd
import xarray as xr
import numpy as np

from pathlib import Path
from typing import Dict
from PyStemmusScope import forcing_io

logger = logging.getLogger(__name__)



def select_forcing_variables(config: Dict) -> xr.Dataset:
    """Reads forcing data, and select the variables needed by ALMA convention.

    Args:
        config(dict): The PyStemmusScope configuration dictionary.

    Returns:
        dict: Dictionary containing the different variables required by ALMA convention.
    """

    forcing_file = Path(config['ForcingPath']) / config['ForcingFileName']

    # read forcing file into a dict
    forcing_dict = forcing_io.read_forcing_data(forcing_file)

    # list of required variables
    var_names = [
        't_air_celcius',
        'sw_down',
        'lw_down',
        'wind_speed',
        'psurf_hpa',
        'rh',
        'year',
        'precip_conv',
        'co2_conv',
        'Qair',
        ]

    data_list = [forcing_dict[var_name] for var_name in var_names]

    # add lat/lon to the list
    data_list.extend(
        [{'latitude': forcing_dict['latitude']},
        {'longitude': forcing_dict['longitude']}]
    )

    # merge into one dataset
    dataset = xr.merge(data_list)

    # add time attributes
    dataset['time'].attrs.update(
        {
            'calendar': forcing_dict['calendar'],
            'time_units': forcing_dict['time_units'],
            }
            )
    # add x/y dims to the dataset
    dataset_expanded = dataset.expand_dims(["x", "y"])

    # change the order of dims
    dataset_reordered = dataset_expanded.transpose("time", "x", "y")

    # update values of x and y coords
    dataset_reordered.assign_coords(
        {
            "x":forcing_dict['longitude'],
            "y":forcing_dict['latitude'],
            }
        )
    return dataset_reordered


def resize_data_frame(config: Dict, data: xr.Dataset)-> xr.Dataset:
    """Resize data based on `NumberOfTimeSteps` in configuration file.

    Args:
        config(dict): The PyStemmusScope configuration dictionary.
        data(xr.Dataset): data to be resized.

    Returns:
        xr.Dataset: subset of data with the lenght of time equal to `NumberOfTimeSteps`.
    """
    # subset data, if needed
    time_steps_lenght = config['NumberOfTimeSteps']
    if time_steps_lenght != 'NA':
        time_length = int(time_steps_lenght) - 1
        data_subset = data.isel(time=np.arange(0, time_length))

    return data_subset


def read_convetion(filename: str) -> pd.DataFrame:
    """Read convention file and return it as a data frame.

    example file: Variables_will_be_in_NetCDF_file.csv

    Args:

    Returns:

    """
    return pd.read_csv(filename)


def create_dataarray(dataset, filename, var_name, metadat):
    data = pd.read_csv(filename)
    variable = data[var_name]

    if metadat['dimension'] == 'XYT':
        dims=["x", "y", "time"]
    else:
        dims=["x", "y", "z", "time"]

    if var_name in dataset:
        # update attrs
    else:
        # add it to dataset
        # update attrs




def save(config, cf_filename):
    dataset = select_forcing_variables(config)
    dataset = resize_data_frame(config, dataset)

    conventions = read_convetion(cf_filename)






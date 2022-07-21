"""PyStemmusScope save module.

Module designed to create csv files (following SCOPE format) and a netcdf
file (following ALMA cf convention) in the output directory.

https://scope-model.readthedocs.io/en/latest/outfiles.html
https://web.lmd.jussieu.fr/~polcher/ALMA/convention_output_3.html
"""

import logging
import pandas as pd
from rdflib import Dataset
import xarray as xr
import numpy as np

from pathlib import Path
from typing import Dict
from PyStemmusScope import forcing_io

logger = logging.getLogger(__name__)



def _select_forcing_variables(config, forcing_dict, forcing_name, alma_name) -> xr.DataArray:
    """Reads forcing data, and select the variables needed by ALMA convention.

    Args:
        config(dict): The PyStemmusScope configuration dictionary.

    Returns:
        dict: Dictionary containing the different variables required by ALMA convention.
    """

    data_array = forcing_dict[forcing_name]
    data_array.rename({forcing_name:alma_name})
    data_array = resize_data_array(data_array, config)
    return data_array

def _update_dims(dataset, forcing_dict):
    # merge into one dataset


    # add time attributes
    time_units = forcing_dict["time"].encoding["units"]
    calendar = forcing_dict["time"].encoding["calendar"]

    dataset['time'].attrs.update(
        {
            'calendar': calendar,
            'time_units': time_units,
            }
            )
    # add x/y dims to the dataset
    dataset_expanded = dataset.expand_dims(["x", "y"])

    # change the order of dims
    dataset_reordered = dataset_expanded.transpose("time", "x", "y")

    # update values of x and y coords
    dataset_reordered.assign_coords(
        {
            "x":dataset_reordered['longitude'].values.flatten(),
            "y":dataset_reordered['latitude'].values.flatten(),
            }
        )
    return dataset_reordered


def resize_data_array(data: xr.DataArray, config)-> xr.Dataset:
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
        time_length = int(time_steps_lenght)
        data = data.isel(time=np.arange(0, time_length))

    return data


def _create_3d_dataarray(csv_file_name: str, model_name: str, time: List) -> xr.DataArray:

    data = pd.read_csv(csv_file_name)
    data_frame = data[model_name].loc[1:]

    data_array = data_frame.to_xarray()
    data_array["index"] = time
    return data_array.rename({"index":"time"})


def _create_4d_dataarray(csv_file_name: str, model_name: str, time: List) -> xr.DataArray:

    data_frame = pd.read_csv(csv_file_name, skiprows=1)

    data_array = data_frame.to_xarray()
    data_array["index"] = time
    return data_array.rename({"index":"time"})


def _add_attrs(data: xr.DataArray, metadata: Dict) -> xr.DataArray:
    data.attrs = {
        "units": metadata['unit'],
        "long_name": metadata['long_name'],
        "standard_name": metadata['standard_name'],
        "STEMMUS-SCOPE_name": metadata['Variable name in STEMMUS-SCOPE'],
        "definition": metadata['definition'],
    }
    return data


def save(config, cf_filename):
    # list of required variables, Alma_short_name: forcing_io_name
    var_names = {
        'Ta': 't_air_celcius',
        'Rin': 'sw_down',
        'Rli': 'lw_down',
        'u': 'wind_speed',
        'p': 'psurf_hpa',
        'RH': 'rh',
        'year': 'year',
        'Pre': 'precip_conv',
        'CO2air': 'co2_conv',
        'Qair': 'Qair',
    }

    forcing_file = Path(config['ForcingPath']) / config['ForcingFileName']

    # read forcing file into a dict
    forcing_dict = forcing_io.read_forcing_data(forcing_file)

    # get time info
    time = resize_data_array(forcing_dict["time"], config)

    # read convention file
    conventions = pd.read_csv(cf_filename)

    # variable metadat
    metadata_list = [
        "unit",
        "long_name",
        "standard_name",
        "Variable name in STEMMUS-SCOPE",
        "definition",
        ]

    alma_short_names = conventions["short_name_alma"]
    data_list = []
    for name in alma_short_names:
        file_name = conventions.loc[alma_short_names == name, ['File name']]
        file_name = file_name.values.flatten()[0]

        model_name = conventions.loc[alma_short_names == name, ['Variable name in STEMMUS-SCOPE']]
        model_name = model_name.values.flatten()[0]

        dimension = conventions.loc[alma_short_names == name, ['dimension']]
        dimension = dimension.values.flatten()[0]

        metadata = conventions.loc[conventions['short_name_alma']== name, metadata_list]

        if name in var_names:
            # select data
            forcing_name = var_names[name]
            dataarray = _select_forcing_variables(config, forcing_dict, forcing_name, name)
        else:
            # create data array
            if file_name == 'Sim_Temp.csv':
                #TODO check Sim_Temp.csv
                dataarray = _create_4d_dataarray(file_name, model_name, time)
            else:
                dataarray = _create_3d_dataarray(file_name, model_name, time)

        # update metadat
        dataarray = _add_attrs(dataarray, metadata)

        # add to list
        dara_list.append(dataarray)

    # add lat/lon to the list
    data_list.extend(
        [{'latitude': forcing_dict['latitude']},
        {'longitude': forcing_dict['longitude']}]
    )

    # merge to a dataset
    dataset = xr.merge(data_list)

    dataset = _update_dims(dataset, forcing_dict)











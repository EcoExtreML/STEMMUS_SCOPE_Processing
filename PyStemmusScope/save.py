"""PyStemmusScope save module.

Module designed to create a netcdf file following the
[ALMA convention](https://web.lmd.jussieu.fr/~polcher/ALMA/)
from csv files following the
[SCOPE format](https://scope-model.readthedocs.io/en/latest/outfiles.html)
in the output directory.

The file
[`required_netcf_variables.csv`](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/utils/csv_to_nc/required_netcf_variables.csv)
lists required variable names and their attributes based on the
[ALMA+CF convention table](https://docs.google.com/spreadsheets/d/1CA3aTvI9piXqRqO-3MGrsH1vW-Sd87D8iZXHGrqK42o/edit#gid=2085475627).

Note:
    See notebooks/run_model_in_notebook.ipynb in the
    [STEMMUS_SCOPE_Processing repository](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing).

"""
import logging
from pathlib import Path
from typing import Dict
from typing import List
import numpy as np
import pandas as pd
import xarray as xr
from PyStemmusScope import config_io
from PyStemmusScope import forcing_io
from PyStemmusScope import utils
from . import variable_conversion as vc


logger = logging.getLogger(__name__)

DATASET_ATTRS = {
    "model": "STEMMUS_SCOPE",
    "institution": "University of Twente; Northwest A&F University",
    "contact": (
        "Zhongbo Su, z.su@utwente.nl; "
        "Yijian Zeng, y.zeng@utwente.nl; "
        "Yunfei Wang, y.wang-3@utwente.nl"
    ),
    "license_type": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
}


def _select_forcing_variables(
    forcing_dict: Dict, forcing_var: str, alma_var: str
) -> xr.DataArray:
    """Select the variable needed by ALMA convention.

    Args:
        forcing_dict(dict): a dictionary returned by
            `PyStemmusScope.forcing_io.read_forcing_data_plumber2()` or
            `read_forcing_data_global()`
        forcing_var(str): variable name in forcing dataset.
        alma_var(str): variable name in ALMA convention.

    Returns:
        xr.DataArray: a data array which its variable name is alma_name.
    """
    # select the forcing variable
    data_array = forcing_dict[forcing_var]

    # rename the variable name to alma_name
    return data_array.rename(alma_var)


def _prepare_soil_data(csv_file: Path, var_name: str, time: List) -> xr.DataArray:
    """Return simulated soil temperature and soil moisture as `xr.DataArray`.

    Args:
        csv_file: csv file name generated by Stemmus_Scope model.
        var_name: variable name by ALMA convention.
        time: time values to be used for the time coordinates.

    Returns:
        xr.DataArray: a dataarray with two dimensions of time and z.
    """
    # the first two rows are depth and thickness
    data = pd.read_csv(csv_file, delimiter=",", header=[0, 1])

    # skip first row that is unit
    data = data.iloc[1:]

    # make sure it is float and not str
    data = data.astype(float)

    # get depth, thickness info
    depths = []
    thicknesses = []
    for depth, thickness in data.columns:
        depths.append(float(depth))
        thicknesses.append(float(thickness))

    # soil layer metadata
    soil_metadata = _create_soil_layer_metadata(thicknesses, depths)

    # drop thickness
    data = data.droplevel(level=1, axis=1)

    if var_name == "SoilTemp":
        # Celsius to Kelvin : K = 273.15 + C
        data = data + 273.15

    elif var_name == "SoilMoist":
        # cm to m
        thicknesses_m = np.array(thicknesses) / 100.0

        for index in data.index:
            # m3/m3 to kg/m2
            volumetric_water_content = np.array(data.loc[index])
            data.loc[index] = vc.soil_moisture(volumetric_water_content, thicknesses_m)

    # reshape the data frame, it returns Series
    data = data.stack()

    # set values
    layers = range(1, data.index.levshape[1] + 1)
    data.index.names = ["time", "z"]
    data.index = data.index.set_levels([time, layers], level=["time", "z"])
    data.name = var_name

    # convert data to xarray data array
    data_array = data.to_xarray()

    # add z attributes
    data_array["z"].attrs = {
        "long_name": "Soil layer",
        "standard_name": "Soil layer",
        "definition": soil_metadata,
        "units": "-",
    }

    return data_array


def _prepare_simulated_data(
    csv_file: Path, model_name: str, alma_name: str, time: List
) -> xr.DataArray:
    """Return model simulation as `xr.DataArray`.

    Args:
        csv_file: csv file name generated by Stemmus_Scope model.
        model_name: variable name by Stemmus_Scope model.
        alma_name: variable name by ALMA conventions.
        time: time values to be used for the time coordinates.

    Returns:
        xr.DataArray: a dataarray with one dimension of time.
    """
    # the first three rows are names and units
    data = pd.read_csv(csv_file, delimiter=",")

    # select variable and skip first row that is unit
    data = data[model_name].iloc[1:]

    # set time values
    data.index = time
    data.index.names = ["time"]  # type: ignore

    # rename it to alma name
    data.name = alma_name

    # make sure it is float and not str
    data = data.astype("float32")

    # convert dataframe to xarray data array
    return data.to_xarray()


def _create_soil_layer_metadata(
    thicknesses: List[float], depths: List[float]
) -> List[str]:
    """Create soil layer metadata for STEMMUS_SCOPE.

    Note:
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
        dataset: Dataset with varaibles in ALMA conventions.
        forcing_dict: a dictionary returned by
            `PyStemmusScope.forcing_io.read_forcing_data_plumber2()` or
            `read_forcing_data_global()`

    Returns:
        The dataset with dimensions ("time", "x", "y").
    """
    # add x/y dims to the dataset
    dataset_expanded = dataset.expand_dims(["x", "y"])

    # change the order of dims
    req_dims = ["time", "x", "y"]
    if any(dim not in dataset_expanded.dims for dim in req_dims):
        raise ValueError("Data should have dimensions time, y, x.")

    if "z" in dataset_expanded.dims:
        dataset_reordered = dataset_expanded.transpose("time", "z", "y", "x")
    else:
        dataset_reordered = dataset_expanded.transpose("time", "y", "x")

    # additional metadata
    lat = forcing_dict["latitude"]
    lon = forcing_dict["longitude"]
    dataset_reordered.attrs = DATASET_ATTRS
    dataset_reordered.attrs["latitude"] = lat
    dataset_reordered.attrs["longitude"] = lon

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


def to_netcdf(config_file: str, cf_filename: str) -> str:
    """Save csv files generated by STEMMUS_SCOPE to a ALMA compliant netCDF file.

    Args:
        config_file: Path to the config file.
        cf_filename: Path to a csv file for ALMA conventions.

    Returns:
        Path to a csv file under the output directory.
    """
    config = config_io.read_config(Path(config_file))
    loc, fmt = utils.check_location_fmt(config["Location"])

    # list of required forcing variables, Alma_short_name: forcing_io_name, # model_name
    var_names = {
        "RH": "rh",  # RH
        "SWdown_ec": "sw_down",  # Rin
        "LWdown_ec": "lw_down",  # Rli
        "Qair": "Qair",
        "Tair": "t_air_celcius",  # Ta
        "Psurf": "psurf_hpa",  # P
        "Wind": "wind_speed",  # u
        "Precip": "precip_conv",  # Pre
    }

    if fmt == "site":
        # read forcing file into a dict
        forcing_dict = forcing_io.read_forcing_data_plumber2(
            utils.get_forcing_file(config),
            config["StartTime"],
            config["EndTime"],
        )
    elif fmt == "latlon":
        forcing_dict = forcing_io.read_forcing_data_global(
            Path(config["ForcingPath"]),
            lat=loc[0],  # type: ignore
            lon=loc[1],  # type: ignore
            start_time=np.datetime64(config["StartTime"]),
            end_time=np.datetime64(config["EndTime"]),
        )

    # get time info
    time = forcing_dict["time"]

    # read convention file
    conventions = pd.read_csv(cf_filename)

    alma_short_names = conventions["short_name_alma"]
    data_list = []
    for alma_name in alma_short_names:
        df = conventions.loc[alma_short_names == alma_name].iloc[0]
        file_name = Path(config["OutputPath"]) / df["file_name_STEMMUS-SCOPE"]

        if alma_name in var_names:
            # select data
            data_array = _select_forcing_variables(
                forcing_dict, var_names[alma_name], alma_name
            )

        # create data array
        elif alma_name in {"SoilTemp", "SoilMoist"}:
            data_array = _prepare_soil_data(file_name, alma_name, time)
        else:
            data_array = _prepare_simulated_data(
                file_name, df["short_name_STEMMUS-SCOPE"], alma_name, time
            )

        # update attributes of array
        data_array.attrs = {
            "units": df["unit"],
            "long_name": df["long_name"],
            "standard_name": df["standard_name"],
            "STEMMUS-SCOPE_name": df["short_name_STEMMUS-SCOPE"],
            "definition": df["definition"],
        }

        # add to list
        data_list.append(data_array)

    # merge to a dataset
    dataset = xr.merge(data_list)

    # update dimensions
    dataset = _update_dataset_attrs_dims(dataset, forcing_dict)

    # for writing to netcdf, time attrs should be added
    # time attrs should be the same as plumber 2 forcing data
    # otherwise it cannot be uploaded to modelevaluation portal
    start_time = time.dt.strftime("%Y-%m-%d").values[0]
    time_encode = {
        "time": {
            "units": f"seconds since {start_time}",
            "calendar": "standard"
            }
        }
    # save to nc file
    nc_filename = (
        Path(config["OutputPath"])
        / f"{Path(config['OutputPath']).stem}_STEMMUS_SCOPE.nc"
    )
    dataset.to_netcdf(path=nc_filename, encoding=time_encode)

    return str(nc_filename)

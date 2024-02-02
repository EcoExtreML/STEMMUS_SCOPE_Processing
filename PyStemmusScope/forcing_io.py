"""Module for forcing data input and output operations."""
from pathlib import Path
import dask
import hdf5storage
import numpy as np
import xarray as xr
from PyStemmusScope import global_data
from PyStemmusScope import utils
from PyStemmusScope import variable_conversion as vc


def _write_matlab_ascii(fname, data, ncols):
    """Write data in the Matlab ascii format.

    Equivalent to `save([-], '-ascii')` in Matlab.

    Args:
        fname (path or str): Path to the file that should be written
        data (np.array): Array with data to write to file
        ncols (int, optional): The number of data columns, required to correctly format
            the ascii file when writing multiple variables.
    """
    matlab_fmt = " %14.7e"
    multi_fmt = [matlab_fmt] * ncols
    multi_fmt[0] = f" {multi_fmt[0]}"
    np.savetxt(fname, data, multi_fmt)


def read_forcing_data_plumber2(forcing_file: Path, start_time: str, end_time: str):
    """Read the forcing data from the provided netCDF file and apply unit conversion.

    Args:
        forcing_file: Path to the netCDF file containing the forcing data
        start_time: Start of time range in ISO format string, e.g. ,
            'YYYY-MM-DDTHH:MM:SS'.
        end_time: End of time range in ISO format string, e.g.,
            'YYYY-MM-DDTHH:MM:SS'.

    Returns:
        dict: Dictionary containing the different variables required by STEMMUS_SCOPE
            for the different forcing files.
    """
    ds_forcing = xr.open_dataset(forcing_file)

    # check if time range is covered by forcing
    # if so, return a subset of forcing matching the given time range
    ds_forcing = _slice_forcing_file(
        ds_forcing,
        start_time,
        end_time,
    )

    # remove the x and y coordinates from the data variables to make the numpy arrays 1D
    ds_forcing = ds_forcing.squeeze(["x", "y"])

    data = {}

    # Expected time format is days (as floating point) since Jan 1st 00:00.
    data["doy_float"] = (
        ds_forcing["time"].dt.dayofyear
        - 1
        + ds_forcing["time"].dt.hour / 24
        + ds_forcing["time"].dt.minute / 60 / 24
    )
    data["year"] = ds_forcing["time"].dt.year.astype(float)

    data["t_air_celcius"] = ds_forcing["Tair"] - 273.15  # conversion from K to degC.
    data["psurf_hpa"] = ds_forcing["Psurf"] / 100  # conversion from Pa to hPa
    data["co2_conv"] = (
        vc.co2_molar_fraction_to_kg_per_m3(
            ds_forcing["CO2air"] * 1e-6  # ppm -> molar fraction
        )
        * 1e6
    )  # kg/m3 -> mg/m3
    data["precip_conv"] = ds_forcing["Precip"] / 10  # conversion from mm/s to cm/s
    data["lw_down"] = ds_forcing["LWdown"]
    data["sw_down"] = ds_forcing["SWdown"]
    data["wind_speed"] = vc.mask_data(ds_forcing["Wind"], min_value=0.05)
    data["rh"] = ds_forcing["RH"]
    data["vpd"] = ds_forcing["VPD"]
    data["lai"] = vc.mask_data(ds_forcing["LAI"], min_value=0.01)

    # calculate ea, conversion from kPa to hPa:
    data["ea"] = vc.calculate_ea(data["t_air_celcius"], data["rh"]) * 10

    # Load in non-timedependent variables
    data["sitename"] = forcing_file.name.split("_")[0]

    # Forcing data timestep size in seconds
    time_delta = (
        ds_forcing.time.values[1] - ds_forcing.time.values[0]
    ) / np.timedelta64(1, "s")
    data["DELT"] = time_delta.astype(float)
    data["total_timesteps"] = ds_forcing.time.size

    data["latitude"] = ds_forcing["latitude"].values
    data["longitude"] = ds_forcing["longitude"].values
    data["elevation"] = ds_forcing["elevation"].values
    data["IGBP_veg_long"] = np.repeat(
        ds_forcing["IGBP_veg_long"].values, ds_forcing.time.size
    ).T
    data["reference_height"] = ds_forcing["reference_height"].values
    data["canopy_height"] = ds_forcing["canopy_height"].values

    # these are needed by save.py
    data["time"] = ds_forcing["time"]
    data["Qair"] = ds_forcing["Qair"]

    return data


def read_forcing_data_global(  # noqa:PLR0913 (too many arguments)
    global_data_dir: Path,
    lat: float,
    lon: float,
    start_time: np.datetime64,
    end_time: np.datetime64,
    timestep: str = "1800s",
) -> dict:
    """Read forcing data for a certain location, based on global datasets.

    Args:
        global_data_dir: Path to the directory containing the global datasets.
        lat: Latitude of the site of interest.
        lon: Longitude of the site of interest.
        start_time: Start time of the model run.
        end_time: End time of the model run.
        timestep: Desired timestep of the model, this is derived from the forcing data.
            In a pandas-timedelta compatible format. Defaults to "1800S" (half an hour).

    Returns:
        Dictionary containing the forcing data.
    """
    # see https://docs.dask.org/en/latest/array-slicing.html#efficiency
    with dask.config.set(**{"array.slicing.split_large_chunks": True}):  # type: ignore
        return global_data.collect_datasets(
            global_data_dir=global_data_dir,
            latlon=(lat, lon),
            time_range=(start_time, end_time),
            timestep=timestep,
        )


def write_dat_files(data: dict, input_dir: Path):
    """Fuction to write the single-data .dat files for the STEMMUS_SCOPE matlab model.

    Args:
        data: Data dictionary generated by read_forcing
        input_dir: Directory to which the different single-column .dat files should be
            written to.
    """
    write_info = {
        "doy_float": "t_.dat",
        "t_air_celcius": "Ta_.dat",
        "sw_down": "Rin_.dat",
        "lw_down": "Rli_.dat",
        "psurf_hpa": "p_.dat",
        "wind_speed": "u_.dat",
        "co2_conv": "CO2_.dat",
        "ea": "ea_.dat",
        "year": "year_.dat",
    }
    for var, fname in write_info.items():
        _write_matlab_ascii(input_dir / fname, data[var], ncols=1)


def write_lai_file(data: dict, fpath: Path):
    """Write the ascii LAI_.dat file for STEMMUS_SCOPE.

    Args:
        data: Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        fpath: Full path, including filename, to which the file should be
            written to.
    """
    lai_file_data = np.vstack([data["doy_float"], data["lai"]]).T
    _write_matlab_ascii(fpath, lai_file_data, ncols=2)


def write_meteo_file(data: dict, fpath: Path):
    """Write the ascii Mdata.txt meteo file for STEMMUS_SCOPE.

    Args:
        data: Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        fpath: Full path, including filename, to which the file should be
            written to.
    """
    meteo_data_vars = [
        "doy_float",
        "t_air_celcius",
        "rh",
        "wind_speed",
        "psurf_hpa",
        "precip_conv",
        "sw_down",
        "lw_down",
        "vpd",
        "lai",
    ]
    meteo_file_data = np.vstack([data[var] for var in meteo_data_vars]).T
    _write_matlab_ascii(fpath, meteo_file_data, ncols=len(meteo_data_vars))


def prepare_global_variables(data: dict, input_path: Path):
    """Read and calculate global variables for STEMMUS_SCOPE from forcing data.

    Data will be written to a Matlab binary file (v7.3), under the name
    'forcing_globals.mat' in the specified input directory.

    Args:
        data: Dictionary containing the required variables. Generated by the
            function `read_forcing_data`.
        input_path: Path to which the file should be written to.
    """
    matfile_vars = [
        "latitude",
        "longitude",
        "elevation",
        "IGBP_veg_long",
        "reference_height",
        "canopy_height",
        "DELT",
        "sitename",
    ]
    matfiledata = {key: data[key] for key in matfile_vars}

    matfiledata["Dur_tot"] = float(data["total_timesteps"])  # Matlab expects a 'double'

    hdf5storage.savemat(
        input_path / "forcing_globals.mat", matfiledata, appendmat=False
    )
    utils.remove_dates_from_header(input_path / "forcing_globals.mat")


def prepare_forcing(config: dict) -> None:
    """Prepare the forcing files required by STEMMUS_SCOPE.

    The input directory should be taken from the model configuration file.
    A subset of forcing file will be generated if the time range is covered
    by the time of existing forcing file.

    Args:
        config (dict): The PyStemmusScope configuration dictionary.
    """
    input_path = Path(config["InputPath"])

    loc, fmt = utils.check_location_fmt(config["Location"])

    if fmt == "site":
        forcing_file = utils.get_forcing_file(config)
        data = read_forcing_data_plumber2(
            forcing_file=forcing_file,
            start_time=config["StartTime"],
            end_time=config["EndTime"],
        )

    elif fmt == "latlon":
        if config["StartTime"] == "NA" or config["EndTime"] == "NA":
            raise ValueError(
                "'NA' as start or end time is not supported in 'global' mode. Please "
                "specify a start and end time."
            )

        data = read_forcing_data_global(
            global_data_dir=Path(config["ForcingPath"]),
            lat=loc[0],  # type: ignore
            lon=loc[1],  # type: ignore
            start_time=np.datetime64(config["StartTime"]),
            end_time=np.datetime64(config["EndTime"]),
        )
    else:
        raise NotImplementedError

    # Write the single-column ascii '.dat' files to the input directory
    write_dat_files(data, input_path)

    # Write the two-column LAI_.dat file to the input directory.
    write_lai_file(data, input_path / "LAI_.dat")

    # Write the multi-column Mdata.txt ascii file to the input directory
    write_meteo_file(data, input_path / "Mdata.txt")

    # Write the remaining variables (without time dependency) to the matlab v7.3
    #  file 'forcing_globals.mat'
    prepare_global_variables(data, input_path)


def _slice_forcing_file(
    ds_forcing: xr.Dataset, start_time: str, end_time: str
) -> xr.Dataset:
    """Get the subset of forcing file based on time range in config.

    Also check if the desired time range is covered by forcing file.

    Args:
        ds_forcing: Dataset of forcing file.
        start_time: Start of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.
            If "NA", start time will be the first timestamp of the forcing input data.
        end_time: End of time range in ISO format string e.g. 'YYYY-MM-DDTHH:MM:SS'.
            If "NA", end time will be the last timestamp of the forcing input data.

    Returns:
        Forcing dataset, sliced with the start and end time.
    """
    start_dtime = None if start_time == "NA" else np.datetime64(start_time)
    end_dtime = None if end_time == "NA" else np.datetime64(end_time)

    start_time_forcing = ds_forcing.coords["time"].values[0]
    end_time_forcing = ds_forcing.coords["time"].values[-1]

    start_time_valid = start_dtime >= start_time_forcing if start_dtime else True
    end_time_valid = end_dtime <= end_time_forcing if end_dtime else True
    if not (start_time_valid and end_time_valid):
        raise ValueError(
            f"Given time range (from {start_dtime} to {end_dtime}) cannot be covered by"
            f"the time range of forcing file (from {start_time_forcing} to "
            f"{end_time_forcing})."
        )

    return ds_forcing.sel(time=slice(start_dtime, end_dtime))

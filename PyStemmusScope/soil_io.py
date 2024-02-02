"""Module for the soil data IO of PyStemmusScope."""
from collections.abc import Iterable
from pathlib import Path
import hdf5storage
import numpy as np
import xarray as xr
from . import utils
from . import variable_conversion as vc


def _open_multifile_datasets(
    paths: Iterable[Path],
    lat: float,
    lon: float,
    lat_key: str = "lat",
    lon_key: str = "lon",
) -> xr.Dataset:
    """Open mfdatasets, and select location before merging.

    Open multifile netCDF files, and selects the lat & lon
    before merging them by coordinates. xarray's open_mfdataset does not support this
    type of functionality.

    Args:
        paths: Iterable containing the paths to the netCDF files
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)
        lat_key: Variable name corresponding to the latitude.
        lon_key: Variable name corresponding to the longitude.

    Returns:
        Dataset containing the merged data for a single location in space.
    """
    datasets: list[xr.Dataset] = []
    for file in paths:
        ds = xr.open_dataset(file)
        #  Drop attributes to avoid combine conflicts
        ds.attrs = ""  # type: ignore
        datasets.append(ds.sel({lat_key: lat, lon_key: lon}, method="nearest"))
    return xr.combine_by_coords(datasets)  # type: ignore


def _read_lambda_coef(
    lambda_directory: Path, lat: float, lon: float, depth_indices: list[int]
) -> dict:
    """Read the lambda coefficient files and return the data in a dict.

    Args:
        lambda_directory: Path to the directory which contains the lambda data.
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)
        depth_indices: List of which indices (0 - 7) should be selected from the
            lambda variable dataset.

    Returns:
        dict: Dictionary containing the lambda coefficient data.
    """
    if not np.all([d in range(8) for d in depth_indices]):
        raise ValueError("Incorrect depth indices provided. Indices range from 0 to 7")

    lambda_files = sorted(lambda_directory.glob("lambda_l*.nc"))

    ds = _open_multifile_datasets(lambda_files, lat, lon)

    # which depth indices the STEMMUS_SCOPE model expects
    ds = ds.sortby("depth")  # make sure that the depths are sorted in increasing order
    coef_lambda = ds["lambda"].isel(depth=depth_indices).values

    return {"Coef_Lamda": coef_lambda}


def _read_soil_composition(
    soil_data_path: Path, lat: float, lon: float, depth_indices: list[int]
) -> dict:
    """Read the soil composition files and return them in a dict.

    Args:
        soil_data_path: Path to the directory which contains the soil data.
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)
        depth_indices: List of which indices (0 - 7) should be selected from the
            soil composition dataset.

    Returns:
        Dictionary containing the soil composition data.
    """
    soil_comp_fnames = [
        "CLAY1.nc",
        "CLAY2.nc",
        "OC1.nc",
        "OC2.nc",
        "SAND1.nc",
        "SAND2.nc",
        "SILT1.nc",
        "SILT2.nc",
    ]

    soil_comp_paths = [soil_data_path / fname for fname in soil_comp_fnames]

    ds = _open_multifile_datasets(soil_comp_paths, lat, lon)

    if not np.all([d in range(8) for d in depth_indices]):
        raise ValueError("Incorrect depth indices provided. Indices range from 0 to 7")

    ds = ds.sortby("depth")  # make sure that the depths are sorted in increasing order
    ds = ds.isel(depth=depth_indices)

    clay_fraction = ds["CLAY"].values / 100  # convert % to fraction
    sand_fraction = ds["SAND"].values / 100  # convert % to fraction
    organic_fraction = ds["OC"].values / 10000  # convert from 1/100th % to fraction.

    return {"FOC": clay_fraction, "FOS": sand_fraction, "MSOC": organic_fraction}


def _read_hydraulic_parameters(
    soil_data_path: Path, lat: float, lon: float, depths: list[int]
) -> dict:
    """Read the soil hydraulic parameters from the Schaap dataset and return a dict.

    Args:
        soil_data_path: Path to the directory which contains the soil data.
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)
        depths: List of depths which should be selected from the dataset. The
            valid depths are: 0, 5, 15, 30, 60, 100 and 200 cm.

    Returns:
        dict: Dictionary containing the hydraulic parameters.
    """
    ptf_files = sorted((soil_data_path / "Schaap").glob("PTF_*.nc"))
    ds = _open_multifile_datasets(
        ptf_files, lat, lon, lat_key="latitude", lon_key="longitude"
    )

    valid_depths = [0, 5, 15, 30, 60, 100, 200]
    if not np.all([d in valid_depths for d in depths]):
        raise ValueError(
            "Incorrect depth value(s) provided. Available depths are" f"{valid_depths}"
        )

    schaap_vars = ["alpha", "Ks", "thetas", "thetar", "n"]
    schaap_data = {key: np.zeros(len(depths)) for key in schaap_vars}

    for i, depth in enumerate(depths):
        for var in schaap_vars:
            schaap_data[var][i] = ds[f"{var}_{depth}cm"]

    fieldmc = vc.field_moisture_content(
        schaap_data["thetar"],
        schaap_data["thetas"],
        schaap_data["alpha"],
        schaap_data["n"],
    )

    return {
        "SaturatedMC": schaap_data["thetas"],
        "ResidualMC": schaap_data["thetar"],
        "Coefficient_n": schaap_data["n"],
        "Coefficient_Alpha": schaap_data["alpha"],
        "porosity": schaap_data["thetas"],
        "Ks0": schaap_data["Ks"][0],
        "SaturatedK": schaap_data["Ks"] / (24 * 3600),  # convert 1/day -> 1/s
        "fieldMC": fieldmc,
        "theta_s0": schaap_data["thetas"][0],
    }


def _read_surface_data(soil_data_path: Path, lat: float, lon: float) -> dict:
    """Read the fmax variable from the surface dataset and return it in a dict.

    Args:
        soil_data_path: Path to the directory which contains the surface data.
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing the `fmax` value (maximum fractional saturated area)
    """
    ds = xr.open_dataset(soil_data_path / "surfdata.nc")
    lat, lon = utils.convert_to_lsm_coordinates(lat, lon)
    ds = ds.sel(lsmlat=lat, lsmlon=lon)

    fmax = ds["FMAX"].values

    return {"fmax": fmax}


def _collect_soil_data(soil_data_path: Path, lat: float, lon: float) -> dict:
    """Call and merge all individual data collectors into a single write-ready dict.

    Args:
        soil_data_path: Path to the directory which contains the soil data.
        lat: Latitude of the site of interest (in degrees North)
        lon: Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing all the processed soil property data.
    """
    lambda_directory = soil_data_path / "lambda"

    schaap_depths = [0, 5, 30, 60, 100, 200]
    depth_indices = [0, 2, 4, 5, 6, 7]

    matfiledata = _read_lambda_coef(lambda_directory, lat, lon, depth_indices)
    matfiledata.update(
        _read_hydraulic_parameters(soil_data_path, lat, lon, schaap_depths)
    )
    matfiledata.update(_read_soil_composition(soil_data_path, lat, lon, depth_indices))
    matfiledata.update(_read_surface_data(soil_data_path, lat, lon))

    return matfiledata


def _retrieve_latlon(file: Path) -> tuple[float, float]:
    """Retrieve the latitude and longitude coordinates from the dataset file.

    Args:
        file: Full path to the netCDF file containing the site latitude and longitude.

    Returns:
        The latitude and longitude values. Latitude in degrees N,
            longitude in degrees E.
    """
    ds = xr.open_dataset(file)
    lon = ds.longitude.values.flatten()
    lat = ds.latitude.values.flatten()
    return lat, lon


def prepare_soil_data(config: dict) -> None:
    """Prepare the soil input data for the STEMMUS_SCOPE model.

    The data for the input location is parsed, and written to a file that can be easily
    read in by Matlab.

    Args:
        config: The PyStemmusScope configuration dictionary.
    """
    loc, fmt = utils.check_location_fmt(config["Location"])

    if fmt == "site":
        forcing_file = utils.get_forcing_file(config)
        # Data missing at ID-Pag site. See github.com/EcoExtreML/STEMMUS_SCOPE/issues/77
        if config["Location"].startswith("ID"):
            lat, lon = -1.0, 112.0
        else:
            lat, lon = _retrieve_latlon(forcing_file)

    elif fmt == "latlon":
        lat = loc[0]  # type: ignore
        lon = loc[1]  # type: ignore
    else:
        raise NotImplementedError

    matfiledata = _collect_soil_data(Path(config["SoilPropertyPath"]), lat, lon)

    hdf5storage.savemat(
        Path(config["InputPath"]) / "soil_parameters.mat",
        mdict=matfiledata,
        appendmat=False,
    )
    utils.remove_dates_from_header(Path(config["InputPath"]) / "soil_parameters.mat")


def prepare_soil_init(config: dict) -> None:
    """Prepare the soil inital conditions data for the STEMMUS_SCOPE model.

    The data for the input location is parsed, and written to a file that can be easily
    read in by Matlab.

    Args:
        config: The PyStemmusScope configuration dictionary.
    """
    loc, fmt = utils.check_location_fmt(config["Location"])

    if fmt == "site":
        matfiledata = _read_soil_initial_conditions_plumber2(
            soil_init_path=Path(config["InitialConditionPath"]),
            sitename=loc,  # type: ignore
        )
    elif fmt == "latlon":
        matfiledata = _read_soil_initial_conditions_global(
            soil_init_path=Path(config["InitialConditionPath"]),
            lat=loc[0],  # type: ignore
            lon=loc[1],  # type: ignore
            start_time=config["StartTime"],
        )
    else:
        raise NotImplementedError

    hdf5storage.savemat(
        Path(config["InputPath"]) / "soil_init.mat",
        mdict=matfiledata,
        appendmat=False,
    )
    utils.remove_dates_from_header(Path(config["InputPath"]) / "soil_init.mat")


def _extract_soil_initial_variables(soil_init_ds: xr.Dataset):
    """Extract the soil intial variables from the soil init dataset.

    Args:
        soil_init_ds: Dataset containing the following era5-land variables;
            skin_temperature,
            soil_temperature_level_1, soil_temperature_level_2,
            soil_temperature_level_3, soil_temperature_level_4,
            volumetric_soil_water_layer_1, volumetric_soil_water_layer_2,
            volumetric_soil_water_layer_3, volumetric_soil_water_layer_4

    Returns:
        Dictionary containing the STEMMUS_SCOPE variable names (keys) and their intial
            soil condition values.
    """
    return {
        "Tss": float(soil_init_ds["skt"].values) - 273.15,
        "InitT0": float(soil_init_ds["skt"].values) - 273.15,
        "InitT1": float(soil_init_ds["stl1"].values) - 273.15,
        "InitT2": float(soil_init_ds["stl2"].values) - 273.15,
        "InitT3": float(soil_init_ds["stl3"].values) - 273.15,
        "InitT4": float(soil_init_ds["stl4"].values) - 273.15,
        "InitT5": float(soil_init_ds["stl4"].values) - 273.15,
        "InitT6": float(soil_init_ds["stl4"].values) - 273.15,
        "InitX0": float(soil_init_ds["swvl1"].values),
        "InitX1": float(soil_init_ds["swvl1"].values),
        "InitX2": float(soil_init_ds["swvl2"].values),
        "InitX3": float(soil_init_ds["swvl3"].values),
        "InitX4": float(soil_init_ds["swvl4"].values),
        "InitX5": float(soil_init_ds["swvl4"].values),
        "InitX6": float(soil_init_ds["swvl4"].values),
        "BtmX": float(soil_init_ds["swvl4"].values),
    }


def _read_soil_initial_conditions_plumber2(
    soil_init_path: Path,
    sitename: str,
) -> dict[str, float]:
    ds = xr.open_mfdataset(str(soil_init_path / f"{sitename}*.nc"))
    ds = ds.squeeze()  # Remove lat, lon, time dims.
    ds.compute()

    return _extract_soil_initial_variables(ds)


def _read_soil_initial_conditions_global(
    soil_init_path: Path,
    lat: float,
    lon: float,
    start_time: np.datetime64,
) -> dict[str, float]:
    """Read soil initial conditions from era5-land data.

    Args:
        soil_init_path (Path): Path to the global soil init data directory.
        lat (float): Latitude of the location of interest.
        lon (float): Longitude of the location of interest.
        start_time (np.datetime64): Start time of the model.

    Returns:
        Dictionary containing the STEMMUS_SCOPE variable names (keys) and their intial
            soil condition values.
    """
    ds = xr.open_mfdataset(str(soil_init_path / "*.nc"))
    ds = ds.sel(latitude=lat, longitude=lon, method="nearest")
    ds = ds.sel(time=start_time, method="nearest")
    ds.compute()

    return _extract_soil_initial_variables(ds)

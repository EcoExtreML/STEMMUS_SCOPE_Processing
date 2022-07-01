from pathlib import Path
import hdf5storage
import numpy as np
import xarray as xr
from . import variable_conversion as vc


def _open_multifile_datasets(paths, lat, lon):
    """Internal function to open multifile netCDF files, and selects the lat & lon
    before merging them by coordinates. xarray's open_mfdataset does not support this
    type of functionality.

    Args:
        paths (iterable): Iterable containing the paths to the netCDF files
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)

    Returns:
        xarray.Dataset: Dataset containing the merged data for a single location in
            space.
    """
    datasets = []
    for file in paths:
        ds = xr.open_dataset(file)
        datasets.append(ds.sel(lat=lat, lon=lon, method='nearest'))
    ds = xr.combine_by_coords(datasets)

    return ds


def _read_lambda_coef(lambda_directory, lat, lon):
    """Internal function that reads the lambda coefficient files and returns the data
    of interest in a dictionary.

    Args:
        lambda_directory (Path): Path to the directory which contains the lambda data.
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing the lambda coefficient data.
    """
    lambda_files = sorted(lambda_directory.glob("lambda_l*.nc"))

    ds = _open_multifile_datasets(lambda_files, lat, lon)

    # which depth indices the STEMMUS_SCOPE model expects
    indices = [0, 2, 4, 5, 6, 7]
    coef_lambda = ds['lambda'].isel(depth=indices).values

    lambda_matfile = {'Coef_Lamda': coef_lambda}

    return lambda_matfile


def _read_soil_composition(soil_data_path, lat, lon):
    """Internal function that reads the soil composition files and returns them in a
    dictionary.

    Args:
        soil_data_path (Path): Path to the directory which contains the soil data.
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing the soil composition data.
    """
    soil_comp_fnames = ['CLAY1.nc', 'CLAY2.nc', 'OC1.nc', 'OC2.nc', 'SAND1.nc',
                        'SAND2.nc', 'SILT1.nc', 'SILT2.nc']

    soil_comp_paths = [soil_data_path / fname for fname in soil_comp_fnames]

    ds = _open_multifile_datasets(soil_comp_paths, lat, lon)

    depths_indices = [0, 2, 4, 5, 6, 7]
    ds = ds.isel(depth=depths_indices)

    clay_fraction = vc.percent_to_fraction(ds['CLAY'].values)
    sand_fraction = vc.percent_to_fraction(ds['SAND'].values)
    organic_fraction = vc.hundredth_percent_to_fraction(ds['OC'].values)

    soil_comp_matfiledata = {
        'FOC': clay_fraction,
        'FOS': sand_fraction,
        'MSOC': organic_fraction,
    }

    return soil_comp_matfiledata


def _read_hydraulic_parameters(soil_data_path, lat, lon):
    """Internal function that reads the soil hydraulic parameters from the Schaap
    dataset and returns them in a dictionary.

    Args:
        soil_data_path (Path): Path to the directory which contains the soil data.
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing the hydraulic parameters.
    """
    depths = [0, 5, 30, 60, 100, 200]
    indices = [1, 2, 4, 5, 6, 7]

    alpha = np.zeros(len(depths))
    Ks = np.zeros(len(depths))
    theta_s = np.zeros(len(depths))
    theta_r = np.zeros(len(depths))
    coef_n = np.zeros(len(depths))

    for i, depth in enumerate(depths):
        ds = xr.open_dataset(soil_data_path /
                             f'Hydraul_Param_SoilGrids_Schaap_sl{indices[i]}.nc')
        ds = ds.sel(latitude=lat, longitude=lon, method='nearest')
        alpha[i] = ds[f"alpha_fit_{depth}cm"]
        Ks[i] = ds[f"mean_Ks_{depth}cm"]
        theta_s[i] = ds[f"mean_theta_s_{depth}cm"]
        theta_r[i] = ds[f"mean_theta_r_{depth}cm"]
        coef_n[i] = ds[f"n_fit_{depth}cm"]

    hydraulic_matfiledata = {
        'SaturatedMC': theta_s,
        'ResidualMC': theta_r,
        'Coefficient_n': coef_n,
        'Coefficient_Alpha': alpha,
        'porosity': theta_s,
        'SaturatedK': vc.per_day_to_per_second(Ks),
        'fieldMC': vc.field_moisture_content(theta_r, theta_s, alpha, coef_n)
    }

    return hydraulic_matfiledata


def _collect_soil_data(soil_data_path, lat, lon):
    """Internal function that calls the individual data collectors and merges them into
    a single dictionary ready to be written.

    Args:
        soil_data_path (Path): Path to the directory which contains the soil data.
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)

    Returns:
        dict: Dictionary containing all the processed soil property data.
    """

    matfiledata = {}

    lambda_directory = soil_data_path / 'lambda'

    matfiledata.update(_read_lambda_coef(lambda_directory, lat, lon))
    matfiledata.update(_read_hydraulic_parameters(soil_data_path, lat, lon))
    matfiledata.update(_read_soil_composition(soil_data_path, lat, lon))

    return matfiledata


def prepare_soil_data(soil_data_dir, matfile_path, lat, lon):
    """Function that prepares the soil input data for the STEMMUS_SCOPE model. It parses
    the data for the input location, and writes a file that can be easily read in by
    Matlab.

    Args:
        soil_data_dir (Path): Path to the directory which contains the soil data.
        lat (float): Latitude of the site of interest (in degrees North)
        lon (float): Longitude of the site of interest (in degrees East)
    """

    soil_data_path = Path(soil_data_dir)

    matfiledata = _collect_soil_data(soil_data_path, lat, lon)

    hdf5storage.savemat(
        matfile_path, mdict=matfiledata, appendmat=False,
    )

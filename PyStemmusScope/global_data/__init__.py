"""Module for operations related to the 'global' datasets."""
from PyStemmusScope.global_data import cams_co2
from PyStemmusScope.global_data import cci_landcover
from PyStemmusScope.global_data import copernicus_lai
from PyStemmusScope.global_data import era5
from PyStemmusScope.global_data import eth_canopy_height
from PyStemmusScope.global_data import prism_dem
from PyStemmusScope.global_data import utils
from PyStemmusScope.global_data.global_data_selection import collect_datasets


__all__ = [
    "collect_datasets",
    "utils",
    "era5",
    "eth_canopy_height",
    "prism_dem",
    "cams_co2",
    "copernicus_lai",
    "cci_landcover",
]

"""Module for operations related to the 'global' datasets."""
from PyStemmusScope.global_data import era5
from PyStemmusScope.global_data import eth_canopy_height
from PyStemmusScope.global_data import prism_dem
from . import global_data_selection


__all__ = ["global_data_selection", "era5", "eth_canopy_height", "prism_dem"]

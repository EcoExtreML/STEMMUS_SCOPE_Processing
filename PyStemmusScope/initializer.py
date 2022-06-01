from asyncio.log import logger
from pathlib import Path
import logging


class InputDir:
    """Create input directories and copy required data."""

    def __init__(self, path_to_config_file: str = "config_file_snellius.txt",
        path_to_model: str = "path_to_STEMMUS_SCOPE_repository"
    ):
        """Instantiate a handler for working directories

        Specify path STEMMUS SCOPE repository and load the config file.

        """
    
        self.config = self._read_config(path_to_config_file)

    def _read_config(self, path_to_config_file):
        """Read config from given config file."""
        config = {}
        with open(path_to_config_file, "r") as f:
            for line in f:
                (key, val) = line.split("=")
                config[key] = val.rstrip('\n')

        return config

    def _copy_data():
        """Copy required data to the work directory."""
        # check all files/folders
        #logger
        # required data i.e. directional, fluspect_parameters, leafangles, radiationdata, soil_spectra, and input_data.xlsx

    
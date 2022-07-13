"""PyStemmusScope wrapper around Stemmus_Scope."""

import os
import logging
from pathlib import Path
from typing import Tuple, Iterable, Any
import subprocess
from . import forcing_io
from . import config_io
from . import soil_io
from . import utils

logger = logging.getLogger(__name__)


class StemmusScope():

    def __init__(self, config_file: str, exe_file: str):
        # make sure paths are abolute and path objects
        config_file = utils.to_absolute_path(config_file)
        self.exe_file = utils.to_absolute_path(exe_file)

        # read config template
        self.config = config_io.read_config(config_file)

    def setup(
        self,
        WorkDir: str = None,
        SoilPropertyPath: str = None,
        ForcingPath: str = None,
        ForcingFileName: str = None,
        directional: str = None,
        fluspect_parameters: str = None,
        leafangles: str = None,
        radiationdata: str = None,
        soil_spectrum: str = None,
        InitialConditionPath: str = None,
        input_data: str = None,
        NumberOfTimeSteps: str = None,
    ) -> Tuple[str, str, str]:
        """Configure model run.

        1. Creates config file and input/output directories based on the config template.
        2. Prepare forcing and soil data

        Args:
            WorkDir: path to a directory where input/output directories should be created.
            SoilPropertyPath: path to a soil property data directory.
            ForcingPath: path to a forcing data directory.
            ForcingFileName: forcing file name. Forcing file should be in netcdf format.
            directional: path to a directional data directory.
            fluspect_parameters: path to a fluspect parameters directory.
            leafangles: path to a leafangles data directory.
            radiationdata: path to a radiation data directory.
            soil_spectrum:  path to a soil spectrum data directory.
            InitialConditionPath: path to a soil initial condition directory.
            input_data: path to input_data file in excel format.
            NumberOfTimeSteps: total number of time steps in which model runs. It can be
                `NA` or a number. Example `10` runs the model for 10 time steps.

        Returns:
            Paths to config file and input/output directories
        """
        # update config template if needed
        arguments = vars().copy()
        arguments.pop('self')
        for key, val in arguments.items():
            if val is not None:
                 self.config[key] = val


        input_dir, output_dir, cfg_file = config_io.create_io_dir(self.config["ForcingFileName"], self.config)

        # read the run config file
        self.config = config_io.read_config(cfg_file)

        return str(input_dir), str(output_dir), str(cfg_file)


    @property
    def configs(self) -> Iterable[Tuple[str, Any]]:
        """Return the configurations for this model."""
        return self.config


"""PyStemmusScope wrapper around Stemmus_Scope."""

import logging
import os
import subprocess
from typing import Dict
from . import config_io
from . import forcing_io
from . import soil_io
from . import utils


logger = logging.getLogger(__name__)


class StemmusScope():

    def __init__(self, config_file: str, exe_file: str):
        # make sure paths are abolute and path objects
        config_file = utils.to_absolute_path(config_file)
        self.exe_file = utils.to_absolute_path(exe_file)

        # read config template
        self._configs = config_io.read_config(config_file)

    def setup(
        self,
        WorkDir: str = None,
        ForcingFileName: str = None,
        NumberOfTimeSteps: str = None,
    ) -> str:
        """Configure model run.

        1. Creates config file and input/output directories based on the config template.
        2. Prepare forcing and soil data

        Args:
            WorkDir: path to a directory where input/output directories should be created.
            ForcingFileName: forcing file name. Forcing file should be in netcdf format.
            NumberOfTimeSteps: total number of time steps in which model runs. It can be
                `NA` or a number. Example `10` runs the model for 10 time steps.

        Returns:
            Paths to config file and input/output directories
        """
        # update config template if needed
        if WorkDir:
            self._configs["WorkDir"] = WorkDir

        if ForcingFileName:
            self._configs["ForcingFileName"] = ForcingFileName

        if NumberOfTimeSteps:
            self._configs["NumberOfTimeSteps"] = NumberOfTimeSteps

        # create customized config file and input/output directories for model run
        _, _, self.cfg_file = config_io.create_io_dir(
            self._configs["ForcingFileName"], self._configs
            )

        # read the run config file
        self._configs = config_io.read_config(self.cfg_file)

        # prepare forcing data
        forcing_io.prepare_forcing(self._configs)

        # prepare soil data
        soil_io.prepare_soil_data(self._configs)

        # set matlab log dir
        os.environ['MATLAB_LOG_DIR'] = str(self._configs["InputPath"])

        return str(self.cfg_file)

    def run(self) -> str:
        """Run model using executable.

        Args:

        Returns:
            Tuple with stdout and stderr
        """

        # run the model
        args = [f"{self.exe_file} {self.cfg_file}"]
        result = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True,
        )
        stdout = result.stdout

        # TODO return log info line by line!
        logger.info("%s", stdout)

        return stdout


    @property
    def config(self) -> Dict:
        """Return the configurations for this model."""
        return self._configs

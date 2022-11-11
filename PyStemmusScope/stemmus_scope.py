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
    """PyStemmusScope wrapper around Stemmus_Scope model.
    see https://gmd.copernicus.org/articles/14/1379/2021/

    It sets the model with a configuration file and executable file.
    It also prepares forcing and soil data for model run.

    Args:
        config_file(str): path to Stemmus_Scope configuration file. An example
        config_file can be found in tests/test_data in `STEMMUS_SCOPE_Processing
        repository <https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing>`_
        exe_file(str): path to Stemmus_Scope executable file.

    Example:
        See notebooks/run_model_in_notebook.ipynb in `STEMMUS_SCOPE_Processing
        repository <https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing>`_
    """

    def __init__(self, config_file: str, exe_file: str):
        # make sure paths are abolute and path objects
        config_file = utils.to_absolute_path(config_file)
        self.exe_file = utils.to_absolute_path(exe_file)

        # read config template
        self._configs = config_io.read_config(config_file)

    def setup(
        self,
        WorkDir: str = None,
        Location: str = None,
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

        if Location:
            self._configs["Location"] = Location

        if NumberOfTimeSteps:
            self._configs["NumberOfTimeSteps"] = NumberOfTimeSteps

        # get forcing files from location
        forcing_file_name = utils.get_forcing_file(self._configs)

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

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

        # create customized config file and input/output directories for model run
        self.input_dir, self.output_dir, self.cfg_file = config_io.create_io_dir(
            self.config["ForcingFileName"], self.config
            )

        # read the run config file
        self.config = config_io.read_config(self.cfg_file)

        # prepare forcing data
        forcing_io.prepare_forcing(self.config)

        # prepare soil data
        soil_io.prepare_soil_data(self.config)

        return str(self.input_dir), str(self.output_dir), str(self.cfg_file)

    def run(self) -> Tuple[str, str, str]:
        """Run model using executable.

        Args:

        Returns:
            Tuple with stdout and stderr
        """
        # set matlab log dir
        os.environ['MATLAB_LOG_DIR'] = str(self.config["InputPath"])

        # run the model
        args = [f"{self.exe_file} {self.cfg_file}"]
        result = subprocess.Popen(
            args, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        exit_code = result.wait()
        stdout, stderr = result.communicate()
        logger.info("%s", stdout)

        if exit_code != 0:
            raise subprocess.CalledProcessError(
                returncode=exit_code, cmd=args, stderr=stderr, output=stdout
            )

        return stdout

    # TODO
    def _check_matlab_runtime_environment():
        """"Check if MCR/MATLAB_Runtime is in LD_LIBRARY_PATH."""
        exist = False
        if "MCR" in os.environ['LD_LIBRARY_PATH']:
            exist = True
        if "MATLAB_Runtime" in os.environ['LD_LIBRARY_PATH']:
            exist = True
        return exist

    # def _set_matlab_paths():
    #     """Sets up the MATLAB Runtime environment for the current $ARCH."""
    #     # matlab_path = whereis MATLAB
    #     matlab_path = matlab_path.s.split(": ")[1]
    #     os.environ['LD_LIBRARY_PATH'] = (
    #         f"{matlab_path}/MATLAB_Runtime/v910/runtime/glnxa64:"
    #         f"{matlab_path}/MATLAB_Runtime/v910/bin/glnxa64:"
    #         f"{matlab_path}/MATLAB_Runtime/v910/sys/os/glnxa64:"
    #         f"{matlab_path}/MATLAB_Runtime/v910/extern/bin/glnxa64:"
    #         f"{matlab_path}/MATLAB_Runtime/v910/sys/opengl/lib/glnxa64")

    def _whereis(app):
        # which on wondows, whereis on unix
        command = 'which' if os.name != 'nt' else 'whereis'
        result = subprocess.check_output(f'{command} {app}', stderr=subprocess.STDOUT)

        exit_code = result.wait()
        if exit_code != 0:
            raise subprocess.CalledProcessError(returncode=exit_code)

        return result.decode().split()


    @property
    def configs(self) -> Iterable[Tuple[str, Any]]:
        """Return the configurations for this model."""
        return self.config


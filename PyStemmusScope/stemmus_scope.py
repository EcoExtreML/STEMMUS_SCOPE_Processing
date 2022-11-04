"""PyStemmusScope wrapper around Stemmus_Scope."""

import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict
from . import config_io
from . import forcing_io
from . import soil_io
from . import utils


logger = logging.getLogger(__name__)

def _is_model_src_exe(model_src_path: Path):
    #TODO add docstring

    #TODO add documentation links in msg below
    if model_src_path.is_file():
        msg = ("The model executable file can be used on a Unix system "
            "where MCR is installed, see the documentaion.")
        logger.info("%s", msg)
        return True
    if model_src_path.is_dir():
        return False
    msg = (
        "Provide a valid path to an executable file or "
        "to a directory containing model source codes, "
        "see the documentaion.")
    raise ValueError(msg)


def _check_interpreter(interpreter: str):
    if interpreter not in {"Octave" , "Matlab"}:
        msg = (
            "Set `interpreter` as Octave or Matlab to run the model using source codes."
            "Otherwise set `model_src_path` to the model executable file, "
            "see the documentaion.")
        raise ValueError(msg)


def _run_sub_process(args: list, cwd):
    # pylint: disable=consider-using-with
    result = subprocess.Popen(
        args, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
    )
    exit_code = result.wait()
    stdout, stderr = result.communicate()
    #TODO handle stderr properly
    # when using octave, exit_code might be 139
    # see issue STEMMUS_SCOPE_Processing/issues/46
    if exit_code not in [0, 139]:
        raise subprocess.CalledProcessError(
            returncode=exit_code, cmd=args, stderr=stderr, output=stdout
        )
    if exit_code == 139:
        logger.warning(stderr)

    # TODO return log info line by line!
    logger.info(stdout)
    return stdout.decode('utf-8')


class StemmusScope():
    """PyStemmusScope wrapper around Stemmus_Scope model.
    see https://gmd.copernicus.org/articles/14/1379/2021/

   Configures the model and prepares forcing and soil data for the model run.

    Args:
        config_file(str): path to Stemmus_Scope configuration file. An example
        config_file can be found in tests/test_data in `STEMMUS_SCOPE_Processing
        repository <https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing>`_
        model_src_path(str): path to Stemmus_Scope executable file or to a
        directory containing model source codes.
        interpreter(str, optional): use `Matlab` or `Octave`. Only required if
        `model_src_path` is a path to model source codes.

    Example:
        See notebooks/run_model_in_notebook.ipynb in `STEMMUS_SCOPE_Processing
        repository <https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing>`_
    """

    def __init__(self, config_file: str, model_src_path: str, interpreter: str = None):
        # make sure paths are abolute and path objects
        config_file = utils.to_absolute_path(config_file)
        model_src_path = utils.to_absolute_path(model_src_path)

        # check the path to model source
        self.exe_file = None
        if _is_model_src_exe(model_src_path):
            self.exe_file = model_src_path
        else:
            _check_interpreter(interpreter)

        self.model_src = model_src_path
        self.interpreter = interpreter

        # read config template
        self._config = config_io.read_config(config_file)

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
            self._config["WorkDir"] = WorkDir

        if ForcingFileName:
            self._config["ForcingFileName"] = ForcingFileName

        if NumberOfTimeSteps:
            self._config["NumberOfTimeSteps"] = NumberOfTimeSteps

        # create customized config file and input/output directories for model run
        _, _, self.cfg_file = config_io.create_io_dir(
            self._config["ForcingFileName"], self._config
            )

        # read the run config file
        self._config = config_io.read_config(self.cfg_file)

        # prepare forcing data
        forcing_io.prepare_forcing(self._config)

        # prepare soil data
        soil_io.prepare_soil_data(self._config)

        return str(self.cfg_file)

    def run(self) -> str:
        """Run model using executable.

        Args:

        Returns:
            string, the model log
        """
        if self.exe_file:
            # run using MCR
            args = [f"{self.exe_file} {self.cfg_file}"]
            # set matlab log dir
            os.environ['MATLAB_LOG_DIR'] = str(self._config["InputPath"])
            result = _run_sub_process(args, None)
        if self.interpreter=="Matlab":
            # set Matlab arguments
            path_to_config = f"'{self.cfg_file}'"
            eval_code= f'STEMMUS_SCOPE_exe({path_to_config});exit;'
            args = ["matlab", "-r", eval_code, "-nodisplay", "-nosplash", "-nodesktop"]
            # seperate args dont work on linux!
            if utils.os_name() !="nt":
                args = shlex.join(args)
            result = _run_sub_process(args, self.model_src)
        if self.interpreter=="Octave":
            # set Octave arguments
            # use subprocess instead of oct2py,
            # see issue STEMMUS_SCOPE_Processing/issues/46
            path_to_config = f"'{self.cfg_file}'"
            # fix for windows
            path_to_config = path_to_config.replace("\\", "/")
            eval_code = f'STEMMUS_SCOPE_exe({path_to_config});exit;'
            args = ["octave", "--eval", eval_code, "--no-gui", "--silent"]
            # seperate args dont work on linux!
            if utils.os_name() !="nt":
                args = shlex.join(args)
            result = _run_sub_process(args, self.model_src)
        return result


    @property
    def config(self) -> Dict:
        """Return the configurations for this model."""
        return self._config

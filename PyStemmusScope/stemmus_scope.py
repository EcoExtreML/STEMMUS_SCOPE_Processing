"""PyStemmusScope wrapper around Stemmus_Scope."""

import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional
from typing import Union
from . import config_io
from . import forcing_io
from . import soil_io
from . import utils


logger = logging.getLogger(__name__)


def _is_model_src_exe(model_src_path: Path) -> bool:
    """Check if input exists.

    Returns True if input is a file and False if it is a directory.

    Args:
        model_src_path(Path): path to Stemmus_Scope executable file or to a
        directory containing model source codes.
    """
    if model_src_path.is_file():
        msg = (
            "The model executable file can be used on a Unix system "
            "where MCR is installed, see the "
            "`documentation<https://pystemmusscope.readthedocs.io/>`_."
        )
        logger.info("%s", msg)
        return True
    if model_src_path.is_dir():
        return False
    msg = (
        "Provide a valid path to an executable file or "
        "to a directory containing model source codes, "
        "see the `documentation<https://pystemmusscope.readthedocs.io/>`_."
    )
    raise ValueError(msg)


def _check_interpreter(interpreter: Union[None, str]) -> None:
    if interpreter not in {"Octave", "Matlab"}:
        msg = (
            "Set `interpreter` as Octave or Matlab to run the model using source codes."
            "Otherwise set `model_src_path` to the model executable file, "
            "see the `documentation<https://pystemmusscope.readthedocs.io/>`_."
        )
        raise ValueError(msg)


def _run_sub_process(args: Union[str, list[str]], cwd: Optional[Path] = None) -> str:
    """Run subprocess' Popen, using a list of arguments.

    Args:
        args: Arguments to be run
        cwd: Desired working directory

    Raises:
        subprocess.CalledProcessError: If Popen returns an error code other than 0 or
            139.

    Returns:
        str: Captured stdout.
    """
    result = subprocess.Popen(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    exit_code = result.wait()
    stdout, stderr = result.communicate()
    # TODO handle stderr properly
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
    return stdout.decode("utf-8")


class StemmusScope:
    """PyStemmusScope wrapper around Stemmus_Scope model."""

    def __init__(
        self,
        config_file: Union[str, Path],
        model_src_path: Union[str, Path],
        interpreter: Optional[str] = None,
    ):
        """PyStemmusScope wrapper around Stemmus_Scope model.

        For a detailed model description, look at
        [this publication](https://gmd.copernicus.org/articles/14/1379/2021/).

        Configures the model and prepares forcing and soil data for the model run.

        Arguments:
            config_file: Path to Stemmus_Scope configuration file. An example
                config_file can be found in tests/test_data in [STEMMUS_SCOPE_Processing
                repository](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing).
            model_src_path: Path to Stemmus_Scope executable file or to a
                directory containing model source codes.
            interpreter (optional): Use `Matlab` or `Octave`. Only required if
                `model_src_path` is a path to model source codes.

        Example:
            See notebooks/run_model_in_notebook.ipynb at the [STEMMUS_SCOPE_Processing
            repository](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing)
        """
        # make sure paths are abolute and path objects
        config_path = utils.to_absolute_path(config_file)
        model_src = utils.to_absolute_path(model_src_path)

        # check the path to model source
        self.exe_file = None
        if _is_model_src_exe(model_src):
            self.exe_file = model_src
        else:
            _check_interpreter(interpreter)

        self.model_src = model_src
        self.interpreter = interpreter

        # read config template
        self._config = config_io.read_config(config_path)

    def setup(
        self,
        WorkDir: Optional[str] = None,
        Location: Optional[str] = None,
        StartTime: Optional[str] = None,
        EndTime: Optional[str] = None,
    ) -> str:
        """Configure the model run.

        1. Creates config file and input/output directories based on the config template
        2. Prepare forcing and soil data

        Args:
            WorkDir: path to a directory where input/output directories should be
                created.
            Location: Location of the model run. Can be a site ("FI-Hyy") or lat/lon,
                e.g., "(52.0, 4.05)".
            ForcingFileName: forcing file name. Forcing file should be in netcdf format.
            StartTime: Start time of the model run. It must be in
                ISO format (e.g. 2007-01-01T00:00).
            EndTime: End time of the model run. It must be in ISO format
                (e.g. 2007-01-01T00:00).

        Returns:
            Path to the config file
        """
        # update config template if needed
        if WorkDir:
            self._config["WorkDir"] = WorkDir

        if Location:
            self._config["Location"] = Location

        if StartTime:
            self._config["StartTime"] = StartTime

        if EndTime:
            self._config["EndTime"] = EndTime

        # validate config *before* directory creation
        config_io.validate_config(self._config)

        # create customized config file and input/output directories for model run
        _, _, self.cfg_file = config_io.create_io_dir(self._config)

        self._config = config_io.read_config(self.cfg_file)

        forcing_io.prepare_forcing(self._config)
        soil_io.prepare_soil_data(self._config)
        soil_io.prepare_soil_init(self._config)

        return str(self.cfg_file)

    def run(self) -> str:
        """Run model using executable.

        Returns:
            The model log.
        """
        if self.exe_file:
            # run using MCR
            args = [f"{self.exe_file} {self.cfg_file}"]
            # set matlab log dir
            os.environ["MATLAB_LOG_DIR"] = str(self._config["InputPath"])
            result = _run_sub_process(args, None)
        if self.interpreter == "Matlab":
            # set Matlab arguments
            path_to_config = f"'{self.cfg_file}'"
            eval_code = f"STEMMUS_SCOPE_exe({path_to_config});exit;"
            args = ["matlab", "-r", eval_code, "-nodisplay", "-nosplash", "-nodesktop"]

            # seperate args dont work on linux!
            result = _run_sub_process(
                args if utils.os_name() == "nt" else shlex.join(args), self.model_src
            )
        if self.interpreter == "Octave":
            # set Octave arguments
            # use subprocess instead of oct2py,
            # see issue STEMMUS_SCOPE_Processing/issues/46
            path_to_config = f"'{self.cfg_file}'"
            # fix for windows
            path_to_config = path_to_config.replace("\\", "/")
            eval_code = f"STEMMUS_SCOPE_exe({path_to_config});exit;"
            args = ["octave", "--eval", eval_code, "--no-gui", "--silent"]

            # seperate args dont work on linux!
            result = _run_sub_process(
                args if utils.os_name() == "nt" else shlex.join(args), self.model_src
            )
        return result

    @property
    def config(self) -> dict:
        """Return the configurations for this model."""
        return self._config

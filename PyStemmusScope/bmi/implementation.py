"""BMI wrapper for the STEMMUS_SCOPE model."""
import os
from pathlib import Path
from typing import Literal
from typing import Protocol
from typing import Union
import h5py
import numpy as np
from bmipy.bmi import Bmi
from PyStemmusScope.bmi.utils import InapplicableBmiMethods
from PyStemmusScope.config_io import read_config


MODEL_INPUT_VARNAMES: tuple[str, ...] = ("soil_temperature",)

MODEL_OUTPUT_VARNAMES: tuple[str, ...] = (
    "soil_temperature",
    "respiration",
)

MODEL_VARNAMES: tuple[str, ...] = tuple(
    set(MODEL_INPUT_VARNAMES + MODEL_OUTPUT_VARNAMES)
)

VARNAME_UNITS: dict[str, str] = {"respiration": "unknown", "soil_temperature": "degC"}

VARNAME_DTYPE: dict[str, str] = {
    "respiration": "float64",
    "soil_temperature": "float64",
}

VARNAME_GRID: dict[str, int] = {
    "respiration": 0,
    "soil_temperature": 1,
}

NO_STATE_MSG = (
    "The model state is not available. Please run `.update()` before requesting "
    "\nthis model info. If you did run .update() before, something seems to have "
    "\ngone wrong and you have to restart the model."
)

NO_CONFIG_MSG = (
    "The model has not been initialized with a configuration file yet. Please first run"
    "\n.initialize() before requesting this model info."
)


def load_state(config: dict) -> h5py.File:
    """Load the STEMMUS_SCOPE model state.

    Args:
        config: BMI configuration, containing the path to the output directory.

    Returns:
        Model state, as a dict.
    """
    matfile = Path(config["OutputPath"]) / "STEMMUS_SCOPE_state.mat"
    return h5py.File(matfile, mode="a")


def get_variable(state: h5py.File, varname: str) -> np.ndarray:
    """Get a variable from the model state.

    Args:
        state: STEMMUS_SCOPE model state
        varname: Variable name
    """
    if varname == "respiration":
        return state["fluxes"]["Resp"][0]
    elif varname == "soil_temperature":
        return state["TT"][0, :-1]
    else:
        if varname in MODEL_VARNAMES:
            msg = "Varname is missing in get_variable! Contact devs."
        else:
            msg = "Unknown variable name"
        raise ValueError(msg)


def set_variable(
    state: h5py.File,
    varname: str,
    value: np.ndarray,
    inds: Union[np.ndarray, None] = None,
) -> dict:
    """Set a variable in the model state.

    Args:
        state: Model state.
        varname: Variable name.
        value: New value for the variable.
        inds: (Optional) at which indices you want to set the variable values.

    Returns:
        Updated model state.
    """
    if inds is not None:
        vals = get_variable(state, varname)
        vals[inds] = value
    else:
        vals = value

    if varname == "soil_temperature":
        state["TT"][0, :-1] = vals
    else:
        if varname in MODEL_OUTPUT_VARNAMES and varname not in MODEL_INPUT_VARNAMES:
            msg = "This variable is a model output variable only. You cannot set it."
        elif varname in MODEL_VARNAMES:
            msg = "Varname is missing in set_variable! Contact devs."
        else:
            msg = "Uknown variable name"
        raise ValueError(msg)
    return state


def get_run_mode(config: dict) -> Literal["exe", "docker"]:
    """Get the run mode (docker or EXE) from the config file.

    Args:
        config: Config dictionary

    Returns:
        Run mode (either "exe" or "docker").
    """
    if "ExeFilePath" in config:
        return "exe"
    elif "DockerImage" in config:
        return "docker"
    elif os.getenv("STEMMUS_SCOPE") is not None:
        return "exe"
    else:
        msg = (
            "No valid config found, or the STEMMUS_SCOPE environment variable is "
            "not set.\nPlease use the ExeFilePath or DockerImage configuration entry, "
            "or set the STEMMUS_SCOPE environment variable."
        )
        raise ValueError(msg)


def check_writable(file: Path) -> None:
    """Check if this process has write access to a file."""
    if not os.access(file, os.W_OK):
        msg = (
            f"The file '{file}' already exists, and this process has no"
            " write access to it."
        )
        raise PermissionError(msg)


class StemmusScopeProcess(Protocol):
    """Protocol for communicating with the model process."""

    def __init__(self, cfg_file: str) -> None:
        """Initialize the process class (e.g. create the container)."""
        ...

    def is_alive(self) -> bool:
        """Return if the process is alive."""
        ...

    def initialize(self) -> None:
        """Initialize the model and wait for it to be ready."""
        ...

    def update(self) -> None:
        """Update the model and wait for it to be ready."""
        ...

    def finalize(self) -> None:
        """Finalize the model."""
        ...


def start_process(mode: Literal["exe", "docker"], cfg_file: str) -> StemmusScopeProcess:
    """Start the right STEMMUS_SCOPE process."""
    if mode == "docker":
        try:
            from PyStemmusScope.bmi.docker_process import StemmusScopeDocker

            return StemmusScopeDocker(cfg_file=cfg_file)
        except ImportError as err:
            msg = (
                "The docker python package is not available."
                " Please install before continuing."
            )
            raise ImportError(msg) from err
    elif mode == "exe":
        from PyStemmusScope.bmi.local_process import LocalStemmusScope

        return LocalStemmusScope(cfg_file=cfg_file)
    else:
        msg = "Unknown mode."
        raise ValueError(msg)


class StemmusScopeBmi(InapplicableBmiMethods, Bmi):
    """STEMMUS_SCOPE Basic Model Interface."""

    config_file: str = ""
    config: dict = {}
    state: Union[h5py.File, None] = None
    state_file: Union[Path, None] = None

    _run_mode: Union[str, None] = None
    _process: Union[StemmusScopeProcess, None] = None

    def initialize(self, config_file: str) -> None:
        """Perform startup tasks for the model.

        Args:
            config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.config = read_config(config_file)

        Path(self.config["OutputPath"]).mkdir(parents=True, exist_ok=True)
        self.state_file = Path(self.config["OutputPath"]) / "STEMMUS_SCOPE_state.mat"
        if self.state_file.exists():
            check_writable(self.state_file)
        else:
            self.state_file.touch()  # Prevent docker messing up file permission.

        self._run_mode = get_run_mode(self.config)

        self._process = start_process(self._run_mode, config_file)
        self._process.initialize()

    def update(self) -> None:
        """Advance the model state by one time step."""
        if self.state is not None:
            self.state = self.state.close()  # Close file to allow matlab to write

        if self._process is not None:
            self._process.update()
        else:
            msg = "The STEMMUS_SCOPE process is not running/connected. Can't update!"
            raise ValueError(msg)

        self.state = load_state(self.config)

    def update_until(self, time: float) -> None:
        """Advance model state until the given time.

        Args:
            time: A model time later than the current model time.
        """
        while time > self.get_current_time():
            self.update()

    def finalize(self) -> None:
        """Finalize the STEMMUS_SCOPE model."""
        if self._process is not None:
            self._process.finalize()
        else:
            msg = "The STEMMUS_SCOPE process is not running/connected. Can't finalize!"
            raise ValueError(msg)

    def get_component_name(self) -> str:
        """Name of the component.

        Returns:
            Name of the component (STEMMUS_SCOPE).
        """
        return "STEMMUS_SCOPE"

    ### VARIABLE INFO METHODS ###
    def get_input_item_count(self) -> int:
        """Get the number of model input variables.

        Returns:
            The number of input variables.
        """
        return len(MODEL_INPUT_VARNAMES)

    def get_output_item_count(self) -> int:
        """Get the number of model output variables.

        Returns:
            The number of output variables.
        """
        return len(MODEL_OUTPUT_VARNAMES)

    # The types of the following two methods are wrong in python-bmi
    # see: https://github.com/csdms/bmi-python/issues/38
    def get_input_var_names(self) -> tuple[str, ...]:  # type: ignore
        """List of the model's input variables (as CSDMS Standard Names)."""
        return MODEL_INPUT_VARNAMES

    def get_output_var_names(self) -> tuple[str, ...]:  # type: ignore
        """List of the model's output variables (as CSDMS Standard Names)."""
        return MODEL_OUTPUT_VARNAMES

    def get_var_grid(self, name: str) -> int:
        """Get grid identifier for the given variable."""
        return VARNAME_GRID[name]

    def get_var_type(self, name: str) -> str:
        """Get data type of the given variable."""
        return VARNAME_DTYPE[name]

    def get_var_units(self, name: str) -> str:
        """Get units of the given variable."""
        return VARNAME_UNITS[name]

    def get_var_itemsize(self, name: str) -> int:
        """Get memory use for each array element in bytes."""
        return np.array([], dtype=VARNAME_DTYPE[name]).itemsize

    def get_var_nbytes(self, name: str) -> int:
        """Get size, in bytes, of the given variable."""
        return self.get_grid_size(self.get_var_grid(name)) * self.get_var_itemsize(name)

    ### TIME METHODS ###
    def get_current_time(self) -> float:
        """Get the current time of the model."""
        if self.state is None:
            raise ValueError(NO_STATE_MSG)

        return self.get_start_time() + np.sum(self.state["TimeStep"][0])

    def get_start_time(self) -> float:
        """Start time of the model."""
        if len(self.config) == 0:
            raise ValueError(NO_CONFIG_MSG)

        return (
            np.datetime64(self.config["StartTime"])
            .astype("datetime64[s]")
            .astype("float")
        )

    def get_end_time(self) -> float:
        """End time of the model."""
        if len(self.config) == 0:
            raise ValueError(NO_CONFIG_MSG)

        return (
            np.datetime64(self.config["EndTime"])
            .astype("datetime64[s]")
            .astype("float")
        )

    def get_time_units(self) -> str:
        """Time units of the model."""
        return "seconds since 1970-01-01 00:00:00.0 +0000"

    def get_time_step(self) -> float:
        """Return the current time step of the model."""
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        return float(self.state["TimeStep"][0][0])

    ### GETTERS AND SETTERS ###
    def get_value(self, name: str, dest: np.ndarray) -> np.ndarray:
        """Get a copy of values of the given variable.

        Args:
            name: input or output variable name, a CSDMS Standard Name.
            dest: numpy array into which to place the values.

        Returns:
            The same numpy array that was passed as an input buffer.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        dest[:] = get_variable(self.state, name)
        return dest

    def get_value_ptr(self, name: str) -> np.ndarray:
        """Get a reference to values of the given variable.

        Note: not possible due to the Matlab<>Python coupling.
        """
        raise NotImplementedError()

    def get_value_at_indices(
        self, name: str, dest: np.ndarray, inds: np.ndarray
    ) -> np.ndarray:
        """Get values at particular indices.

        Args:
            name: Input or output variable name, a CSDMS Standard Name.
            dest: numpy array into which to place the values.
            inds: The indices into the variable array.

        Returns:
            Value of the model variable at the given location.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        dest[:] = get_variable(self.state, name)[inds]
        return dest

    def set_value(self, name: str, src: np.ndarray) -> None:
        """Specify a new value for a model variable.

        Args:
            name: Input or output variable name, a CSDMS Standard Name.
            src: The new value for the specified variable.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        self.state = set_variable(self.state, name, src)

    def set_value_at_indices(
        self, name: str, inds: np.ndarray, src: np.ndarray
    ) -> None:
        """Specify a new value for a model variable at particular indices.

        Parameters
        ----------
        name : str
            An input or output variable name, a CSDMS Standard Name.
        inds : array_like
            The indices into the variable array.
        src : array_like
            The new value for the specified variable.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        self.state = set_variable(self.state, name, src, inds)

    ### GRID INFO ###
    def get_grid_rank(self, grid: int) -> int:
        """Get number of dimensions of the computational grid.

        Args:
            grid: A grid identifier.

        Returns:
            Rank of the grid.
        """
        if grid == 0:
            return 2
        if grid == 1:
            return 3
        msg = f"Invalid grid identifier '{grid}'"
        raise ValueError(msg)

    def get_grid_size(self, grid: int) -> int:
        """Get the total number of elements in the computational grid.

        Args:
            grid: A grid identifier.

        Returns:
            Size of the grid.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)

        if grid == 0:
            return 1
        if grid == 1:
            return int(self.state["ModelSettings"]["mN"][0]) - 1

        msg = f"Invalid grid identifier '{grid}'"
        raise ValueError(msg)

    def get_grid_type(self, grid: int) -> str:
        """Get the grid type as a string.

        Args:
            grid: A grid identifier.

        Returns:
            Type of grid as a string.
        """
        return "rectilinear"

    def get_grid_x(self, grid: int, x: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the x direction.

        Args:
            grid: grid identifier.
            x: numpy array to hold the x-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column x-coordinates.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        x[:] = self.state["SiteProperties"]["longitude"][0]
        return x

    def get_grid_y(self, grid: int, y: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the y direction.

        Args:
            grid: grid identifier.
            y: numpy array to hold the y-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column y-coordinates.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        y[:] = self.state["SiteProperties"]["latitude"][0]
        return y

    def get_grid_z(self, grid: int, z: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the z direction.

        Args:
            grid: grid identifier.
            z: numpy array to hold the z-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column z-coordinates.
        """
        if self.state is None:
            raise ValueError(NO_STATE_MSG)
        if grid == 1:
            z[:] = (
                -np.hstack(
                    (
                        self.state["ModelSettings"]["DeltZ_R"][:, 0].cumsum()[::-1],
                        np.array([0.0]),
                    )
                )
                / 100
            )
            return z
        else:
            raise ValueError(f"Grid {grid} has no dimension `z`.")

    def get_grid_shape(self, grid: int, shape: np.ndarray) -> np.ndarray:
        """Get dimensions of the computational grid."""
        if grid not in [0, 1]:
            msg = f"Unknown grid identifier '{grid}'"
            raise ValueError(msg)

        shape[-1] = 1  # Last element is x
        shape[-2] = 1  # Semi-last element is y
        if grid == 1:
            shape[-3] = self.get_grid_size(grid)  # First element is z
        return shape

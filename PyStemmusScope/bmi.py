"""BMI wrapper for the STEMMUS_SCOPE model."""
import os
import sys
from pathlib import Path
from subprocess import run
from typing import Any
import hdf5storage
import numpy as np
from bmipy.bmi import Bmi
from PyStemmusScope.config_io import read_config


MODEL_INPUT_VARNAMES: tuple[str] = ("soil_temperature",)

MODEL_OUTPUT_VARNAMES: tuple[str] = (
    "soil_temperature",
    "respiration",
)

MODEL_VARNAMES: tuple[str] = tuple(set(MODEL_INPUT_VARNAMES + MODEL_OUTPUT_VARNAMES))

VARNAME_UNITS: dict[str, str] = {"respiration": "unknown", "soil_temperature": "degC"}

VARNAME_DTYPE: dict[str, str] = {
    "respiration": "float64",
    "soil_temperature": "float64",
}

VARNAME_GRID: dict[str, int] = {
    "respiration": 0,
    "soil_temperature": 1,
}


def ipython_info():
    """Get ipython info: if the code is being run from notebook or terminal."""
    ip = False
    if "ipykernel" in sys.modules:
        ip = "notebook"
    elif "IPython" in sys.modules:
        ip = "terminal"
    return ip


def run_cmd(args):
    """Run a command (i.e. run the matlab model executable).

    Args:
        args: Arguments to run.
    """
    if ipython_info() == "notebook":
        result = run(args, shell=True)
    else:
        result = run(args)
    result.check_returncode()


def load_state(config: dict) -> dict[str, Any]:
    """Load the STEMMUS_SCOPE model state.

    Args:
        config: BMI configuration, containing the path to the output directory.

    Returns:
        Model state, as a dict.
    """
    matfile = Path(config["OutputPath"]) / "STEMMUS_SCOPE_state.mat"
    return hdf5storage.loadmat(matfile, appendmat=False)


def get_variable(state: dict, varname: str) -> None:
    """Get a variable from the model state.

    Args:
        state: STEMMUS_SCOPE model state
        varname: Variable name
    """
    match varname:
        case "respiration":
            return state["fluxes"]["Resp"].flatten()
        case "soil_temperature":
            return state["TT"].flatten()[:-1]
        case _:
            if varname in MODEL_VARNAMES:
                msg = "Varname is missing in get_variable! Contact devs."
            else:
                msg = "Uknown variable name"
            raise ValueError(msg)


def set_variable(state: dict, varname: str, value: np.ndarray) -> dict:
    """Set a variable in the model state.

    Args:
        state: Model state.
        varname: Variable name.
        value: New value for the variable.

    Returns:
        Updated model state.
    """
    match varname:
        case "respiration":
            state["fluxes"]["Resp"][0][0][0] = value
        case "soil_temperature":
            state["TT"][:-1, 0] = value
        case _:
            if varname in MODEL_VARNAMES:
                msg = "Varname is missing in get_variable! Contact devs."
            else:
                msg = "Uknown variable name"
            raise ValueError(msg)
    return state


class StemmusScopeBmi(Bmi):
    """STEMMUS_SCOPE Basic Model Interface."""

    config_file: str = ""
    config: dict = {}
    state: dict = {}
    state_file: Path

    def initialize(self, config_file: str) -> None:
        """Perform startup tasks for the model.

        Args:
            config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.config = read_config(config_file)
        self.exe_file = self.config["ExeFilePath"]
        self.state_file = Path(self.config["OutputPath"]) / "STEMMUS_SCOPE_state.mat"

        args = f"{self.exe_file} {self.config_file} initialize"

        # set matlab log dirc
        os.environ["MATLAB_LOG_DIR"] = str(self.config["InputPath"])

        run_cmd(args)

    def update(self) -> None:
        """Advance the model state by one time step."""
        if self.state != {}:
            hdf5storage.savemat(self.state_file, self.state, appendmat=False)
        args = f"{self.exe_file} {self.config_file} update"
        run_cmd(args)

        self.state = load_state(self.config)

    def update_until(self, time: float) -> None:
        """Advance model state until the given time.

        Args:
            time: A model time later than the current model time.
        """
        raise NotImplementedError()

    def finalize(self) -> None:
        """Finalize the STEMMUS_SCOPE model."""
        args = f"{self.exe_file} {self.config_file} finalize"
        run_cmd(args)

    def get_component_name(self) -> str:
        """Name of the component.

        Returns:
            Name of the component (STEMMUS_SCOPE).
        """
        return "STEMMUS_SCOPE"

    def get_input_item_count(self) -> int:
        """Number of model input variables.

        Returns:
            The number of input variables.
        """
        return len(MODEL_INPUT_VARNAMES)

    def get_output_item_count(self) -> int:
        """Number of model output variables.

        Returns:
            The number of output variables.
        """
        return len(MODEL_OUTPUT_VARNAMES)

    def get_input_var_names(self) -> list[str]:
        """List of the model's input variables (as CSDMS Standard Names)."""
        return list(MODEL_INPUT_VARNAMES.keys())

    def get_output_var_names(self) -> list[str]:
        """List of the model's output variables (as CSDMS Standard Names)."""
        return list(MODEL_OUTPUT_VARNAMES.keys())

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
        raise NotImplementedError()

    def get_var_nbytes(self, name: str) -> int:
        """Get size, in bytes, of the given variable."""
        raise NotImplementedError()

    def get_current_time(self) -> float:
        """Current time of the model."""
        raise NotImplementedError()

    def get_start_time(self) -> float:
        """Start time of the model."""
        raise NotImplementedError()

    def get_end_time(self) -> float:
        """End time of the model."""
        raise NotImplementedError()

    def get_time_units(self) -> str:
        """Time units of the model."""
        "* days since *"
        raise NotImplementedError()

    def get_time_step(self) -> float:
        """Return the current time step of the model."""
        return self.state["KT"][0][0].flatten().astype("float")

    def get_value(self, name: str, dest: np.ndarray) -> np.ndarray:
        """Get a copy of values of the given variable.

        Args:
            name: input or output variable name, a CSDMS Standard Name.
            dest: numpy array into which to place the values.

        Returns:
            The same numpy array that was passed as an input buffer.
        """
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
        raise NotImplementedError()

    def set_value(self, name: str, src: np.ndarray) -> None:
        """Specify a new value for a model variable.

        Args:
            name: Input or output variable name, a CSDMS Standard Name.
            src: The new value for the specified variable.
        """
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
        raise NotImplementedError()

    # Grid information
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

    def get_grid_size(self, grid: int) -> int:
        """Get the total number of elements in the computational grid.

        Args:
            grid: A grid identifier.

        Returns:
            Size of the grid.
        """
        if grid == 0:
            return 1
        if grid == 1:
            return int(self.state["ModelSettings"]["mN"].flatten()[0]) - 1

    def get_grid_type(self, grid: int) -> str:
        """Get the grid type as a string.

        Args:
            grid: A grid identifier.

        Returns:
            Type of grid as a string.
        """
        return "rectilinear"

    # Non-uniform rectilinear, curvilinear
    def get_grid_x(self, grid: int, x: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the x direction.

        Args:
            grid: grid identifier.
            x: numpy array to hold the x-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column x-coordinates.
        """
        x[:] = self.state["SiteProperties"]["latitude"][0][0].flatten().astype("float")
        return x

    def get_grid_y(self, grid: int, y: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the y direction.

        Args:
            grid: grid identifier.
            y: numpy array to hold the y-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column y-coordinates.
        """
        y[:] = self.state["SiteProperties"]["latitude"].flatten().astype("float")
        return y

    def get_grid_z(self, grid: int, z: np.ndarray) -> np.ndarray:
        """Get coordinates of grid nodes in the z direction.

        Args:
            grid: grid identifier.
            z: numpy array to hold the z-coordinates of the grid node columns.

        Returns:
            The input numpy array that holds the grid's column z-coordinates.
        """
        if grid == 1:
            z[:] = (
                -np.hstack(
                    (
                        np.array([0.0]),
                        self.state["ModelSettings"]["DeltZ_R"].flatten().cumsum(),
                    )
                )
                / 100
            )
            return z
        else:
            raise ValueError()

    # Uniform rectilinear
    def get_grid_shape(self, grid: int, shape: np.ndarray) -> np.ndarray:
        """Get dimensions of the computational grid."""
        raise NotImplementedError()

    def get_grid_spacing(self, grid: int, spacing: np.ndarray) -> np.ndarray:
        """Get distance between nodes of the computational grid."""
        raise NotImplementedError()

    def get_grid_origin(self, grid: int, origin: np.ndarray) -> np.ndarray:
        """Get coordinates for the lower-left corner of the computational grid."""
        raise NotImplementedError()

    # Unstructured grids:
    def get_var_location(self, name: str) -> str:
        """Get the grid element type that the a given variable is defined on."""
        raise NotImplementedError()

    def get_grid_node_count(self, grid: int) -> int:
        """Get the number of nodes in the grid."""
        raise NotImplementedError()

    def get_grid_edge_count(self, grid: int) -> int:
        """Get the number of edges in the grid."""
        raise NotImplementedError()

    def get_grid_face_count(self, grid: int) -> int:
        """Get the number of faces in the grid."""
        raise NotImplementedError()

    def get_grid_edge_nodes(self, grid: int, edge_nodes: np.ndarray) -> np.ndarray:
        """Get the edge-node connectivity."""
        raise NotImplementedError()

    def get_grid_face_edges(self, grid: int, face_edges: np.ndarray) -> np.ndarray:
        """Get the face-edge connectivity."""
        raise NotImplementedError()

    def get_grid_face_nodes(self, grid: int, face_nodes: np.ndarray) -> np.ndarray:
        """Get the face-node connectivity."""
        raise NotImplementedError()

    def get_grid_nodes_per_face(
        self, grid: int, nodes_per_face: np.ndarray
    ) -> np.ndarray:
        """Get the number of nodes for each face."""
        raise NotImplementedError()

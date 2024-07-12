import platform
from distutils.dir_util import copy_tree
from pathlib import Path
import docker
import docker.errors
import numpy as np
import pytest
import requests
from PyStemmusScope import config_io
from PyStemmusScope import forcing_io
from PyStemmusScope import soil_io
from PyStemmusScope.bmi.docker_utils import pull_image
from PyStemmusScope.bmi.implementation import StemmusScopeBmi
from . import data_folder


SCOPE_INPUTDATA_v2_1 = "https://github.com/Christiaanvandertol/SCOPE/raw/2.1/input/"
SCOPE_INPUTDATA_v1_7 = (
    "https://github.com/Christiaanvandertol/SCOPE/raw/1.73/data/input/"
)


# fmt: off
SOIL_GRID = np.array([
    -5.   , -4.8  , -4.6  , -4.4  , -4.2  , -4.   , -3.8  , -3.6  ,
    -3.4  , -3.2  , -3.   , -2.8  , -2.6  , -2.45 , -2.3  , -2.2  ,
    -2.1  , -2.   , -1.9  , -1.8  , -1.7  , -1.6  , -1.5  , -1.4  ,
    -1.3  , -1.2  , -1.1  , -1.   , -0.9  , -0.8  , -0.7  , -0.6  ,
    -0.55 , -0.5  , -0.45 , -0.4  , -0.35 , -0.325, -0.3  , -0.275,
    -0.25 , -0.23 , -0.21 , -0.19 , -0.17 , -0.15 , -0.13 , -0.11 ,
    -0.09 , -0.07 , -0.05 , -0.03 , -0.02 , -0.01 , -0.,
])

INVALID_METHODS = (
    "get_grid_spacing", "get_grid_origin", "get_var_location", "get_grid_node_count",
    "get_grid_edge_count", "get_grid_face_count", "get_grid_edge_nodes",
    "get_grid_face_edges", "get_grid_face_nodes", "get_grid_nodes_per_face"
)
# fmt: on


def docker_available():
    try:
        docker.APIClient()

        # Github Actions windows runners couldn't pull the image:
        if platform.system() == "Windows":
            pull_image("ghcr.io/ecoextreml/stemmus_scope:1.5.0")

        return True
    except docker.errors.DockerException as err:
        if "Error while fetching server API version" in str(err):
            return False
        if "404 Client Error" in str(err):  # Can't find image
            return False
        else:
            raise err  # Unknown error.


cfg_file = data_folder / "config_file_docker.txt"
vegetation_property_dir = (
    data_folder / "directories" / "model_parameters" / "vegetation_property"
)


def write_config_file(cfg: dict, file: Path) -> None:
    with file.open("w") as f:
        for key, val in cfg.items():
            f.write(f"{key}={val}\n")


@pytest.fixture(scope="session")
def prep_input_data():
    optipar_path = (
        vegetation_property_dir / "fluspect_parameters" / "Optipar2017_ProspectD.mat"
    )
    if not optipar_path.exists():
        r = requests.get(  # Older version due to v2 compatibility issues
            SCOPE_INPUTDATA_v1_7 + "fluspect_parameters/Optipar2017_ProspectD.mat"
        )
        assert r.status_code == 200
        optipar_path.open("wb").write(r.content)

    flex_s3_path = vegetation_property_dir / "radiationdata" / "FLEX-S3_std.atm"
    if not flex_s3_path.exists():
        r = requests.get(SCOPE_INPUTDATA_v2_1 + "radiationdata/FLEX-S3_std.atm")
        assert r.status_code == 200
        flex_s3_path.open("wb").write(r.content)

    soil_path = vegetation_property_dir / "soil_spectrum" / "soilnew.txt"
    if not soil_path.exists():
        r = requests.get(SCOPE_INPUTDATA_v2_1 + "soil_spectra/soilnew.txt")
        assert r.status_code == 200
        soil_path.open("wb").write(r.content)


@pytest.fixture(scope="session")
def prepare_data_config(tmpdir_factory, prep_input_data) -> Path:
    tempdir = Path(tmpdir_factory.mktemp("tempdir"))
    output_dir = tempdir / "output_dir"
    input_dir = tempdir / "input_dir"
    output_dir.mkdir()
    input_dir.mkdir()
    config = config_io.read_config(cfg_file)
    config["OutputPath"] = str(output_dir) + "/"
    config["InputPath"] = str(input_dir) + "/"

    forcing_io.prepare_forcing(config)
    soil_io.prepare_soil_data(config)
    soil_io.prepare_soil_init(config)

    copy_tree(src=str(vegetation_property_dir), dst=str(input_dir))

    config_dir = tempdir / "config.txt"
    write_config_file(config, config_dir)

    return config_dir


@pytest.fixture(scope="class")
def uninitialized_model():
    model = StemmusScopeBmi()
    yield model
    try:
        model.finalize()
    except:  # noqa
        pass


@pytest.fixture(scope="class")
def initialized_model(uninitialized_model, prepare_data_config):
    model: StemmusScopeBmi = uninitialized_model
    model.initialize(str(prepare_data_config))
    yield model
    model.finalize()


@pytest.fixture(scope="class")
def updated_model(uninitialized_model, prepare_data_config):
    model: StemmusScopeBmi = uninitialized_model
    model.initialize(str(prepare_data_config))
    model.update()
    yield model
    model.finalize()


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
class TestUninitialized:
    def test_component_name(self, uninitialized_model):
        assert uninitialized_model.get_component_name() == "STEMMUS_SCOPE"

    def test_invalid_update(self, uninitialized_model):
        with pytest.raises(ValueError, match="STEMMUS_SCOPE process is not running"):
            uninitialized_model.update()

    def test_get_ptr(self, uninitialized_model):
        with pytest.raises(NotImplementedError):
            uninitialized_model.get_value_ptr("soil_temperature")

    @pytest.mark.parametrize("method_name", INVALID_METHODS)
    def test_not_implemented(self, uninitialized_model, method_name):
        method = getattr(uninitialized_model, method_name)
        nargs = method.__code__.co_argcount - 1  # remove "self"
        with pytest.raises(NotImplementedError):
            method(*(nargs * [0]))

    def test_initialize(self, uninitialized_model, prepare_data_config):
        uninitialized_model.initialize(str(prepare_data_config))


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
class TestInitializedModel:
    def test_input_item(self, initialized_model):
        assert isinstance(initialized_model.get_input_item_count(), int)

    def test_output_item(self, initialized_model):
        assert isinstance(initialized_model.get_output_item_count(), int)

    def test_input_var(self, initialized_model):
        assert "soil_temperature" in initialized_model.get_input_var_names()

    def test_output_var(self, initialized_model):
        assert "respiration" in initialized_model.get_output_var_names()

    def test_var_grid(self, initialized_model):
        assert initialized_model.get_var_grid("respiration") == 0
        assert initialized_model.get_var_grid("soil_temperature") == 1

    def test_var_type(self, initialized_model):
        assert initialized_model.get_var_type("soil_temperature") == "float64"

    def test_grid_type(self, initialized_model):
        assert initialized_model.get_grid_type(0) == "rectilinear"
        assert initialized_model.get_grid_type(1) == "rectilinear"

    def test_var_units(self, initialized_model):
        assert initialized_model.get_var_units("soil_temperature") == "degC"

    def test_grid_rank(self, initialized_model):
        grid_resp = initialized_model.get_var_grid("respiration")
        grid_t = initialized_model.get_var_grid("soil_temperature")
        assert initialized_model.get_grid_rank(grid_resp) == 2
        assert initialized_model.get_grid_rank(grid_t) == 3

    def test_get_time_units(self, initialized_model):
        assert (
            initialized_model.get_time_units()
            == "seconds since 1970-01-01 00:00:00.0 +0000"
        )

    def test_get_start_time(self, initialized_model):
        assert initialized_model.get_start_time() == 820454400.0  # 1996-01-01 00:00:00

    def test_get_end_time(self, initialized_model):
        assert initialized_model.get_end_time() == 820461600.0  # 1996-01-01 02:00:00

    def test_model_update(self, initialized_model):
        initialized_model.update()


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
class TestUpdatedModel:
    # Many of these should be available after init
    def test_get_current_time(self, updated_model):
        assert updated_model.get_current_time() == (
            updated_model.get_start_time() + updated_model.get_time_step()
        )

    def test_get_time_step(self, updated_model):
        assert updated_model.get_time_step() == 1800

    def test_grid_coords(self, updated_model):
        dest = np.zeros(updated_model.get_grid_size(0))
        np.testing.assert_almost_equal(
            updated_model.get_grid_x(0, x=dest), np.array([-107.80752563])
        )
        np.testing.assert_almost_equal(
            updated_model.get_grid_y(0, y=dest), np.array([37.93380356])
        )

    def test_invalid_dimension(self, updated_model):
        dest = np.zeros(updated_model.get_grid_size(0))
        with pytest.raises(ValueError, match="has no dimension `z`"):
            updated_model.get_grid_z(0, z=dest)

    def test_grid_z(self, updated_model):
        grid = updated_model.get_var_grid("soil_temperature")
        dest = np.zeros(updated_model.get_grid_size(grid))
        updated_model.get_grid_z(grid, z=dest)
        np.testing.assert_array_equal(dest, SOIL_GRID)

    def test_grid_shape(self, updated_model):
        grid = updated_model.get_var_grid("soil_temperature")
        shape = np.zeros(updated_model.get_grid_rank(grid), dtype=int)
        updated_model.get_grid_shape(grid, shape)
        np.testing.assert_array_equal(shape, np.array([55, 1, 1], dtype=int))

    def test_get_value(self, updated_model):
        dest = np.zeros(1)
        updated_model.get_value("respiration", dest)
        assert dest[0] != 0.0

    def test_set_output_var(self, updated_model):
        src = np.zeros(1)
        with pytest.raises(ValueError, match="output variable"):
            updated_model.set_value("respiration", src)

    def test_get_wrong_value(self, updated_model):
        dest = np.zeros(1)
        with pytest.raises(ValueError, match="Unknown variable"):
            updated_model.get_value("nonsense_variable", dest)

    def test_set_value(self, updated_model):
        gridsize = updated_model.get_grid_size(
            updated_model.get_var_grid("soil_temperature")
        )
        src = np.zeros(gridsize) + 10.0
        dest = np.zeros(gridsize)
        updated_model.set_value("soil_temperature", src)
        updated_model.get_value("soil_temperature", dest)
        np.testing.assert_array_equal(src, dest)

    def test_set_value_inds(self, updated_model):
        dest = np.zeros(1)
        updated_model.set_value_at_indices(
            "soil_temperature",
            inds=np.array([0]),
            src=np.array([0.0]),
        )
        updated_model.get_value_at_indices("soil_temperature", dest, inds=np.array([0]))
        assert dest[0] == 0.0

    def test_itemsize(self, updated_model):
        assert updated_model.get_var_itemsize("soil_temperature") == 8  # ==64 bits

    def test_get_var_nbytes(self, updated_model):
        assert updated_model.get_var_nbytes("soil_temperature") == 8 * 55

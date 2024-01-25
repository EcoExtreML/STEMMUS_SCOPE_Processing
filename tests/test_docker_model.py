from distutils.dir_util import copy_tree
from pathlib import Path
import docker
import docker.errors
import pytest
import requests
from PyStemmusScope import config_io
from PyStemmusScope import forcing_io
from PyStemmusScope import soil_io
from PyStemmusScope.bmi.implementation import StemmusScopeBmi
from . import data_folder


SCOPE_INPUTDATA_v2_1 = "https://github.com/Christiaanvandertol/SCOPE/raw/2.1/input/"
SCOPE_INPUTDATA_v1_7 = (
    "https://github.com/Christiaanvandertol/SCOPE/raw/1.73/data/input/"
)


def docker_available():
    try:
        docker.APIClient()
        return True
    except docker.errors.DockerException as err:
        if "Error while fetching server API version" in err.value:
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


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
def test_initialize(prepare_data_config):
    model = StemmusScopeBmi()
    model.initialize(str(prepare_data_config))
    model.update()
    model.finalize()

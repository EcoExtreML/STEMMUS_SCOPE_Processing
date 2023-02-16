from pathlib import Path
import pytest
from PyStemmusScope import config_io
from . import data_folder


class TestConfigIO:
    # define required input/expected values as fixtures
    @pytest.fixture()
    def dummy_config(self):
        dummy_config = {
            "WorkDir": "tests/test_data/directories/",
            "SoilPropertyPath": "tests/test_data/directories/model_parameters/soil_property/",
            "ForcingPath": "tests/test_data/directories/forcing/plumber2_data/",
            "Location": "XX-Xxx",
            "directional": "tests/test_data/directories/model_parameters/vegetation_property/directional/",
            "fluspect_parameters": "tests/test_data/directories/model_parameters/vegetation_property/fluspect_parameters/",
            "leafangles": "tests/test_data/directories/model_parameters/vegetation_property/leafangles/",
            "radiationdata": "tests/test_data/directories/model_parameters/vegetation_property/radiationdata/",
            "soil_spectrum": "tests/test_data/directories/model_parameters/vegetation_property/soil_spectrum/",
            "input_data": "tests/test_data/directories/model_parameters/vegetation_property/dummy_data.xlsx",
            "InitialConditionPath": "tests/test_data/directories/model_parameters/soil_initialcondition/",
            "StartTime": "1996-01-01T00:00",
            "EndTime": "1996-01-01T02:00",
            "InputPath": "",
            "OutputPath": "",
        }
        return dummy_config

    def test_read_config(self, dummy_config):
        path_to_config_file = data_folder / "config_file_test.txt"
        config = config_io.read_config(path_to_config_file)
        expected_config = dummy_config

        assert config == expected_config

    def test_create_io_dir(self):
        path_to_config_file = data_folder / "config_file_test.txt"
        config = config_io.read_config(path_to_config_file)
        input_dir, output_dir, config_path = config_io.create_io_dir(config)
        assert Path(input_dir).is_dir()
        assert Path(output_dir).is_dir()
        assert Path(config_path).exists()

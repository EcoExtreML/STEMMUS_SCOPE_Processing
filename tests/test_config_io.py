from pathlib import Path
import pytest
from PyStemmusScope import config_io
from . import data_folder


class TestConfigIO:
    # define required input/expected values as fixtures
    @pytest.fixture()
    def dummy_config(self):
        dummy_config = {
            'WorkDir': 'tests/test_data/directories/',
            'SoilPropertyPath': 'tests/test_data/directories/model_parameters/soil_property/',
            'ForcingPath': 'tests/test_data/directories/forcing/plumber2_data/',
            'ForcingFileName': 'XX-dummy_forcing_file.nc',
            'directional': 'tests/test_data/directories/model_parameters/vegetation_property/directional/',
            'fluspect_parameters': 'tests/test_data/directories/model_parameters/vegetation_property/fluspect_parameters/',
            'leafangles': 'tests/test_data/directories/model_parameters/vegetation_property/leafangles/',
            'radiationdata': 'tests/test_data/directories/model_parameters/vegetation_property/radiationdata/',
            'soil_spectrum': 'tests/test_data/directories/model_parameters/vegetation_property/soil_spectrum/',
            'input_data': 'tests/test_data/directories/model_parameters/vegetation_property/dummy_data.xlsx',
            'InitialConditionPath': 'tests/test_data/directories/model_parameters/soil_initialcondition/',
            'NumberOfTimeSteps': '17520',
            'InputPath': 'tests/test_data/directories/input/',
            'OutputPath': 'tests/test_data/directories/output/'
        }
        return dummy_config

    def test_read_config(self, dummy_config):
        path_to_config_file = data_folder / "config_file_test.txt"
        config = config_io.read_config(path_to_config_file)
        expected_config = dummy_config

        assert config == expected_config

    def test_create_io_dir(dummy_config):
        nc_file = "XX-dummy_forcing_file.nc"
        path_to_config_file = data_folder / "config_file_test.txt"
        config = config_io.read_config(path_to_config_file)
        input_dir, output_dir, config_path = config_io.create_io_dir(nc_file, config)
        assert Path(input_dir).is_dir()
        assert Path(output_dir).is_dir()
        assert Path(config_path).exists()

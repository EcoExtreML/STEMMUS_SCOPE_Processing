"""Tests for the s2s.initializer module.
"""
from pathlib import Path
import PyStemmusScope

from . import data_folder

class TestInputDir:
    def test_read_config(self):
        path_to_config_file = data_folder / "config_file_test.txt"
        config = PyStemmusScope.read_config(path_to_config_file)

        expected_config = {
            'WorkDir': 'tests/test_data/directories/',
            'SoilPropertyPath': 'tests/test_data/directories/model_parameters/soil_property/',
            'ForcingPath': 'tests/test_data/directories/forcing/plumber2_data/',
            'ForcingFileName': 'NL-dummy_1979-2021_FLUXNET2010_Met.nc',
            'Directional': 'tests/test_data/directories/model_parameters/vegetation_property/directional/',
            'FluspectParameters': 'tests/test_data/directories/model_parameters/vegetation_property/fluspect_parameters/',
            'Leafangles': 'tests/test_data/directories/model_parameters/vegetation_property/leafangles/',
            'Radiationdata': 'tests/test_data/directories/model_parameters/vegetation_property/radiationdata/',
            'SoilSpectra': 'tests/test_data/directories/model_parameters/vegetation_property/soil_spectrum/',
            'InputData': 'tests/test_data/directories/model_parameters/vegetation_property/dummy_data.xlsx',
            'InitialConditionPath': 'tests/test_data/directories/model_parameters/soil_initialcondition/',
            'NumberOfTimeSteps': '17520',
            'InputPath': 'tests/test_data/directories/input/',
            'OutputPath': 'tests/test_data/directories/output/'
        }

        assert config == expected_config

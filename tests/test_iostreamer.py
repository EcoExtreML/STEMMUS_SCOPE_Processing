"""Tests for the s2s.initializer module.
"""
from pathlib import Path
from PyStemmusScope.iostreamer import InputDir

from . import data_folder

class TestInputDir:
    def test_init(self):
        # path to executable
        path_to_model = Path("path_to_STEMMUS_SCOPE_repository")
        # path to config file
        path_to_config_file = data_folder / "config_file_test.txt"
        # Instantiate working directories handler from PyStemmusScope
        initializer = InputDir(path_to_config_file, path_to_model)

        assert isinstance(initializer, InputDir)

    def test_prepare_work_dir(self):
        # path to executable
        path_to_model = Path("path_to_STEMMUS_SCOPE_repository")
        # path to config file
        path_to_config_file = data_folder / "config_file_test.txt"
        # Instantiate working directories handler from PyStemmusScope
        initializer = InputDir(path_to_config_file, path_to_model)
        # specify the forcing filenames
        forcing_filenames_list = ["NL-dummy_1979-2021_FLUXNET2010_Met.nc"]
        # prepare work directory
        work_dir_dict, config_path_dict = initializer.prepare_work_dir(forcing_filenames_list)

        assert work_dir_dict["NL-dummy_1979-2021_FLUXNET2010_Met.nc"].is_dir()
        assert config_path_dict["NL-dummy_1979-2021_FLUXNET2010_Met.nc"].exists()


          
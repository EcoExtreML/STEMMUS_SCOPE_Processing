"""Tests for the s2s.initializer module.
"""
from pathlib import Path
from PyStemmusScope.initializer import InputDir

from . import data_folder

class TestInputDir:
    def test_init(self):
        # path to executable
        path_to_model = Path("path_to_STEMMUS_SCOPE_repository")
        # path to config file
        path_to_config_file = data_folder / "config_file_snellius.txt"
        # Instantiate working directories handler from PyStemmusScope
        initializer = InputDir(path_to_config_file, path_to_model)

        assert isinstance(initializer, InputDir)
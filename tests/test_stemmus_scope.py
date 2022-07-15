import time
from pathlib import Path
from unittest.mock import patch

import pytest
import xarray as xr
from numpy.testing import assert_almost_equal, assert_array_equal
from xarray.testing import assert_allclose

import os
import logging
from typing import Tuple, Iterable, Any
import subprocess
from PyStemmusScope import StemmusScope
from . import data_folder


class TestWithDefaults:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMUUS_SCOPE"
        m = StemmusScope(config_file, exe_file)
        yield m

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            input_dir, output_dir, cfg_file = model.setup()
            return input_dir, output_dir, cfg_file

    def test_setup(self, model_with_setup):
        input_dir, output_dir, cfg_file = model_with_setup

        actual_input_dir = f"{data_folder}/directories/input/XX-dummy_2022-07-11-1200"
        actual_output_dir = f"{data_folder}/directories/output/XX-dummy_2022-07-11-1200"
        actual_cfg_file = f"{actual_input_dir}/XX-dummy_2022-07-11-1200_config.txt"

        assert actual_input_dir == input_dir
        assert actual_output_dir == output_dir
        assert actual_cfg_file == cfg_file



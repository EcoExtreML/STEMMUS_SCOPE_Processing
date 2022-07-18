from pathlib import Path
from unittest.mock import patch

import pytest

import os
import subprocess
from PyStemmusScope import StemmusScope
from PyStemmusScope import config_io
from . import data_folder


class TestWithDefaults:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMUUS_SCOPE"
        # create dummy exe file
        f = open(exe_file, "x")
        yield StemmusScope(config_file, exe_file)

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            input_dir, output_dir, cfg_file = model.setup()
            return model, input_dir, output_dir, cfg_file

    def test_setup(self, model_with_setup):
        _, input_dir, output_dir, cfg_file = model_with_setup

        actual_input_dir = f"{data_folder}/directories/input/XX-dummy_2022-07-11-1200"
        actual_output_dir = f"{data_folder}/directories/output/XX-dummy_2022-07-11-1200"
        actual_cfg_file = f"{actual_input_dir}/XX-dummy_2022-07-11-1200_config.txt"

        assert actual_input_dir == input_dir
        assert actual_output_dir == output_dir
        assert actual_cfg_file == cfg_file

    @patch("subprocess.Popen")
    def test_run(self, mocked_popen, model_with_setup):
        model, _, _, _ = model_with_setup

        actual_cfg_file = f"{data_folder}/directories/input/XX-dummy_2022-07-11-1200_config.txt"
        output = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )
        mocked_popen.return_value.communicate.return_value = (output, "error")
        mocked_popen.return_value.wait.return_value = 0

        result = model.run()

        expected = [f"{model.exe_file} {model.cfg_file}"]
        mocked_popen.assert_called_with(
        expected, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        # output of subprocess
        assert result == output
        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])


class TestWithCustomSetup:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMUUS_SCOPE"
        yield StemmusScope(config_file, exe_file)

    @pytest.fixture
    def model_with_setup(self, model, tmp_path):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"
            input_dir, output_dir, cfg_file = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "5",
            )
        return model, input_dir, output_dir, cfg_file

    def test_setup(self, model_with_setup, tmp_path):
        model, input_dir, output_dir, cfg_file = model_with_setup

        actual_input_dir = f"{tmp_path}/input/dummy_2022-07-11-1200"
        actual_output_dir = f"{tmp_path}/output/dummy_2022-07-11-1200"
        actual_cfg_file = f"{actual_input_dir}/dummy_2022-07-11-1200_config.txt"

        assert actual_input_dir == input_dir
        assert actual_output_dir == output_dir
        assert actual_cfg_file == cfg_file
        assert model.config["NumberOfTimeSteps"] == "5"

    def test_configs(self, model_with_setup):
        model, _, _, cfg_file = model_with_setup
        actual = config_io.read_config(cfg_file)
        assert actual == model.configs

    @patch("subprocess.Popen")
    def test_run(self, mocked_popen, model_with_setup, tmp_path):
        actual_cfg_file = f"{tmp_path}/input/dummy_2022-07-11-1200_config.txt"
        output = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )
        mocked_popen.return_value.communicate.return_value = (output, "error")
        mocked_popen.return_value.wait.return_value = 0

        model, _, _, _ = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {model.cfg_file}"]
        mocked_popen.assert_called_with(
        expected, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        # output of subprocess
        assert result == output
        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])

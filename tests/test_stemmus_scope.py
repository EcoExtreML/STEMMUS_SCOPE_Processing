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
        with open(exe_file, "x", encoding="utf8") as dummy_file:
            dummy_file.close()

        yield StemmusScope(config_file, exe_file)

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            cfg_file = model.setup()
            return model, cfg_file

    def test_setup(self, model_with_setup):
        model, cfg_file = model_with_setup

        actual_input_dir = data_folder / "directories" / "input" / "XX-dummy_2022-07-11-1200"
        actual_output_dir = data_folder / "directories" / "output" / "XX-dummy_2022-07-11-1200"
        actual_cfg_file = str(actual_input_dir / "XX-dummy_2022-07-11-1200_config.txt")

        assert actual_input_dir == Path(model.config["InputPath"])
        assert actual_output_dir == Path(model.config["OutputPath"])
        assert actual_cfg_file == cfg_file

        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])

    @patch("subprocess.run")
    def test_run(self, mocked_run, model_with_setup):

        actual_cfg_file = data_folder / "directories" / "input" / "XX-dummy_2022-07-11-1200_config.txt"
        output = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )

        mocked_run.return_value.stdout = output

        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked_run.assert_called_with(
        expected, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True,
        )

        # output of subprocess
        assert result == output


class TestWithCustomSetup:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMUUS_SCOPE"

        # create dummy exe file
        with open(exe_file, "x", encoding="utf8") as dummy_file:
            dummy_file.close()
        yield StemmusScope(config_file, exe_file)

    @pytest.fixture
    def model_with_setup(self, model, tmp_path):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"
            cfg_file = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "5",
            )
        return model, cfg_file

    def test_setup(self, model_with_setup, tmp_path):
        model, cfg_file = model_with_setup

        actual_input_dir = tmp_path / "input" / "dummy_2022-07-11-1200"
        actual_output_dir = tmp_path / "output" / "dummy_2022-07-11-1200"
        actual_cfg_file = str(actual_input_dir / "dummy_2022-07-11-1200_config.txt")

        assert actual_input_dir == Path(model.config["InputPath"])
        assert actual_output_dir == Path(model.config["OutputPath"])
        assert actual_cfg_file == cfg_file
        assert model.config["NumberOfTimeSteps"] == "5"

        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])

    def test_config(self, model_with_setup):
        model, cfg_file = model_with_setup
        actual = config_io.read_config(cfg_file)
        assert actual == model.config

    @patch("subprocess.run")
    def test_run(self, mocked_run, model_with_setup, tmp_path):

        actual_cfg_file = tmp_path / "input" / "dummy_2022-07-11-1200_config.txt"
        output = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )

        mocked_run.return_value.stdout = output

        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked_run.assert_called_with(
        expected, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True,
        )

        # output of subprocess
        assert result == output

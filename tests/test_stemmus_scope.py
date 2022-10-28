from pathlib import Path
from unittest.mock import patch

import pytest

import os
import subprocess
from PyStemmusScope import StemmusScope
from PyStemmusScope import config_io
from . import data_folder


class TestInit:
    def test_model_without_exe(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMMUS_SCOPE"
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path=exe_file)
        assert "Provide a valid path to an executable file" in str(excinfo.value)

    def test_model_without_src(self):
        config_file = str(data_folder / "config_file_test.txt")
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path="src")
        assert "Provide a valid path to an executable file" in str(excinfo.value)

    def test_model_without_subprocess(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path=tmp_path)
        assert "Set `sub_process` as Octave or Matlab" in str(excinfo.value)

    def test_model_wrong_subprocess(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path=tmp_path, sub_process="Nothing")
        assert "Set `sub_process` as Octave or Matlab" in str(excinfo.value)


class TestWithDefaults:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMMUS_SCOPE"

        # create dummy exe file
        with open(exe_file, "x", encoding="utf8") as dummy_file:
            dummy_file.close()

        yield StemmusScope(config_file, model_src_path=exe_file)

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

    @patch("subprocess.run")
    def test_run_exe_file(self, mocked__run_sub_process, model_with_setup):

        actual_cfg_file = data_folder / "directories" / "input" / "XX-dummy_2022-07-11-1200" / "XX-dummy_2022-07-11-1200_config.txt"
        actual_log = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )

        mocked__run_sub_process.return_value.stdout = actual_log

        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked__run_sub_process.assert_called_with(
        expected, cwd=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True,
        )

        # output of subprocess
        expected_log = (
            f"b'Reading config from {cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )
        assert result == expected_log
        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])


class TestWithCustomSetup:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMUUS_SCOPE"

        # create dummy exe file
        with open(exe_file, "x", encoding="utf8") as dummy_file:
            dummy_file.close()
        yield StemmusScope(config_file, model_src_path=exe_file)

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

    def test_config(self, model_with_setup):
        model, cfg_file = model_with_setup
        actual = config_io.read_config(cfg_file)
        assert actual == model.config

    @patch("subprocess.run")
    def test_run_exe_file(self, mocked__run_sub_process, model_with_setup, tmp_path):

        actual_cfg_file = tmp_path / "input" / "dummy_2022-07-11-1200" / "dummy_2022-07-11-1200_config.txt"
        actual_log = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )

        mocked__run_sub_process.return_value.stdout = actual_log

        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked__run_sub_process.assert_called_with(
        expected, cwd=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True,
        )

        # output of subprocess
        expected_log = (
            f"b'Reading config from {cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )
        assert result == expected_log
        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])


# class TestWithMatlab:
#     @pytest.fixture
#     def model(self, tmp_path):
#         config_file = str(data_folder / "config_file_test.txt")
#         yield StemmusScope(config_file, model_src_path=tmp_path, sub_process="Matlab")

#     @pytest.fixture
#     def model_with_setup(self, model):
#         with patch("time.strftime") as mocked_time:
#             mocked_time.return_value = "2022-07-11-1200"

#             cfg_file = model.setup()
#             return model, cfg_file

#     @patch("subprocess.run")
#     def test_run_matlab(self, mocked__run_sub_process, model_with_setup, tmp_path):

#         actual_cfg_file = data_folder / "directories" / "input" / "XX-dummy_2022-07-11-1200_config.txt"
#         output = (
#             f"Reading config from {actual_cfg_file}\n\n "
#             "The calculations start now\n The calculations end now\n"
#             )

#         mocked__run_sub_process.return_value.stdout = output

#         model, _ = model_with_setup
#         result = model.run()

#         path_to_config = f"'{actual_cfg_file}'"
#         command_line = f'matlab -r "STEMMUS_SCOPE_exe({path_to_config});exit;"'
#         expected = [command_line, "-nodisplay", "-nosplash", "-nodesktop"]

#         mocked__run_sub_process.assert_called_with(
#         expected, cwd=tmp_path,
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#         shell=True, check=True,
#         )

#         # output of subprocess
#         assert output in result

import os
import shlex
import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest
from PyStemmusScope import StemmusScope
from PyStemmusScope import config_io
from PyStemmusScope import utils
from . import data_folder


class TestInit:
    def test_model_without_exe(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMMUS_SCOPE"
        if utils.os_name() == 'nt':
            with pytest.raises(FileNotFoundError):
                StemmusScope(config_file, model_src_path=exe_file)
        else:
            with pytest.raises(ValueError) as excinfo:
                StemmusScope(config_file, model_src_path=exe_file)
            assert "Provide a valid path to an executable file" in str(excinfo.value)

    def test_model_without_src(self):
        config_file = str(data_folder / "config_file_test.txt")
        if utils.os_name() == 'nt':
            with pytest.raises(FileNotFoundError):
                StemmusScope(config_file, model_src_path="src")
        else:
            with pytest.raises(ValueError) as excinfo:
                StemmusScope(config_file, model_src_path="src")
            assert "Provide a valid path to an executable file" in str(excinfo.value)

    def test_model_without_interpreter(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path=tmp_path)
        assert "Set `interpreter` as Octave or Matlab" in str(excinfo.value)

    def test_model_wrong_interpreter(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        with pytest.raises(ValueError) as excinfo:
            StemmusScope(config_file, model_src_path=tmp_path, interpreter="Nothing")
        assert "Set `interpreter` as Octave or Matlab" in str(excinfo.value)


class TestWithDefaults:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = Path(tmp_path) / "STEMMUS_SCOPE"

        # create dummy exe file
        with open(exe_file, "x", encoding="utf8") as dummy_file:
            dummy_file.close()

        yield StemmusScope(config_file=config_file, model_src_path=exe_file)

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            cfg_file, _ = model.setup()
            return model, cfg_file

    def test_setup(self, model_with_setup):
        model, cfg_file = model_with_setup

        actual_input_dir = data_folder / "directories" / "input" / "XX-Xxx_2022-07-11-1200"
        actual_output_dir = data_folder / "directories" / "output" / "XX-Xxx_2022-07-11-1200"
        actual_cfg_file = str(actual_input_dir / "XX-Xxx_2022-07-11-1200_config.txt")

        assert actual_input_dir == Path(model.config["InputPath"])
        assert actual_output_dir == Path(model.config["OutputPath"])
        assert actual_cfg_file == cfg_file

    @patch("subprocess.Popen")
    def test_run_exe_file(self, mocked_popen, model_with_setup):

        actual_cfg_file = data_folder / "directories" / "input" / "XX-Xxx_2022-07-11-1200" / "XX-Xxx_2022-07-11-1200_config.txt"
        actual_log = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            ).encode()
        mocked_popen.return_value.communicate.return_value = (actual_log, "error")
        mocked_popen.return_value.wait.return_value = 0

        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked_popen.assert_called_with(
        expected, cwd=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True,
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
            cfg_file, _ = model.setup(
                WorkDir = str(tmp_path),
                Location="XX-Xxx",
                StartTime="1996-01-01T00:00",
                EndTime="1996-01-01T02:00",
            )
        return model, cfg_file

    def test_setup(self, model_with_setup, tmp_path):
        model, cfg_file = model_with_setup

        actual_input_dir = tmp_path / "input" / "XX-Xxx_2022-07-11-1200"
        actual_output_dir = tmp_path / "output" / "XX-Xxx_2022-07-11-1200"
        actual_cfg_file = str(actual_input_dir / "XX-Xxx_2022-07-11-1200_config.txt")

        assert actual_input_dir == Path(model.config["InputPath"])
        assert actual_output_dir == Path(model.config["OutputPath"])
        assert actual_cfg_file == cfg_file
        assert model.config["StartTime"] == "1996-01-01T00:00"
        assert model.config["EndTime"] == "1996-01-01T02:00"

    def test_config(self, model_with_setup):
        model, cfg_file = model_with_setup
        actual = config_io.read_config(cfg_file)
        assert actual == model.config

    @patch("subprocess.Popen")
    def test_run_exe_file(self, mocked_popen, model_with_setup, tmp_path):

        actual_cfg_file = tmp_path / "input" / "XX-Xxx_2022-07-11-1200" / "XX-Xxx_2022-07-11-1200_config.txt"
        actual_log = (
            f"b'Reading config from {actual_cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            ).encode()
        mocked_popen.return_value.communicate.return_value = (actual_log, "error")
        mocked_popen.return_value.wait.return_value = 0


        model, cfg_file = model_with_setup
        result = model.run()

        expected = [f"{model.exe_file} {cfg_file}"]
        mocked_popen.assert_called_with(
        expected, cwd=None,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
        )

        # output of subprocess
        expected_log = (
            f"b'Reading config from {cfg_file}\n\n "
            "The calculations start now \r\n The calculations end now \r'"
            )
        assert result == expected_log
        # matlab log dir
        assert os.environ['MATLAB_LOG_DIR'] == str(model.config["InputPath"])


class TestWithMatlab:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        yield StemmusScope(config_file, model_src_path=tmp_path, interpreter="Matlab")

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            cfg_file, _ = model.setup()
            return model, cfg_file

    @patch("subprocess.Popen")
    def test_run_matlab(self, mocked_popen, model_with_setup, tmp_path):

        actual_cfg_file = data_folder / "directories" / "input" / "XX-Xxx_2022-07-11-1200" / "XX-Xxx_2022-07-11-1200_config.txt"
        actual_log = (
            "b'MATLAB is selecting SOFTWARE OPENGL rendering.\n..."
            f"\nReading config from {actual_cfg_file}\n"
            "The calculations start now\n The calculations end now\n'"
            ).encode()
        mocked_popen.return_value.communicate.return_value = (actual_log, "error")
        mocked_popen.return_value.wait.return_value = 0

        model, cfg_file = model_with_setup
        result = model.run()

        path_to_config = f"'{actual_cfg_file}'"
        eval_code= f'STEMMUS_SCOPE_exe({path_to_config});exit;'
        args = ["matlab", "-r", eval_code, "-nodisplay", "-nosplash", "-nodesktop"]
        # seperate args dont work on linux!
        if utils.os_name() !="nt":
            args = shlex.join(args)

        mocked_popen.assert_called_with(
        args, cwd=tmp_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
        )

        # output of subprocess
        expected_log =  (
            "b'MATLAB is selecting SOFTWARE OPENGL rendering.\n..."
            f"\nReading config from {cfg_file}\n"
            "The calculations start now\n The calculations end now\n'"
            )

        assert result == expected_log


class TestWithOctave:
    @pytest.fixture
    def model(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        yield StemmusScope(config_file, model_src_path=tmp_path, interpreter="Octave")

    @pytest.fixture
    def model_with_setup(self, model):
        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-07-11-1200"

            cfg_file, _ = model.setup()
            return model, cfg_file

    @patch("subprocess.Popen")
    def test_run_matlab(self, mocked_popen, model_with_setup, tmp_path):

        actual_cfg_file = data_folder / "directories" / "input" / "XX-Xxx_2022-07-11-1200" / "XX-Xxx_2022-07-11-1200_config.txt"
        actual_log = (
            f"b'Reading config from {actual_cfg_file}\n"
            "The calculations start now\n The calculations end now \n'"
            ).encode()
        mocked_popen.return_value.communicate.return_value = (actual_log, "error")
        mocked_popen.return_value.wait.return_value = 0

        model, cfg_file = model_with_setup
        result = model.run()

        path_to_config = f"'{actual_cfg_file}'"
        # fix for windows
        path_to_config = path_to_config.replace("\\", "/")
        eval_code = f'STEMMUS_SCOPE_exe({path_to_config});exit;'
        args = ["octave", "--eval", eval_code, "--no-gui", "--silent"]
        # seperate args dont work on linux!
        if utils.os_name() !="nt":
            args = shlex.join(args)

        mocked_popen.assert_called_with(
        args, cwd=tmp_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
        )

        # output of subprocess
        expected_log =  (
            f"b'Reading config from {cfg_file}\n"
            "The calculations start now\n The calculations end now \n'"
            )

        assert result == expected_log


from pathlib import Path
from unittest.mock import patch
import pytest
from PyStemmusScope import config_io
from PyStemmusScope import utils
from . import data_folder

# TODO add test for convert_to_lsm_coordinates


def test_to_absolute_path():
    input_path = "~/input_dir"
    expected = Path.home() / "input_dir"

    # care for windows, see issue 22
    Path(expected).mkdir(exist_ok=True)

    parsed = utils.to_absolute_path(input_path)

    assert parsed == expected


@patch("PyStemmusScope.utils.os_name")
def test_to_absolute_path_must_exist(mocked_osname):
    input_path = "~/nonexistent_file.txt"
    mocked_osname.return_value = "nt"
    with pytest.raises(FileNotFoundError):
        utils.to_absolute_path(input_path)


def test_to_absolute_path_with_absolute_input_and_parent(tmp_path):
    input_path = tmp_path / "nonexistent_file.txt"
    parsed = utils.to_absolute_path(str(input_path), parent=tmp_path)
    assert parsed == input_path


def test_to_absolute_path_with_relative_input_and_parent(tmp_path):
    input_path = "nonexistent_file.txt"
    parsed = utils.to_absolute_path(input_path, parent=tmp_path)
    expected = tmp_path / "nonexistent_file.txt"
    assert parsed == expected


def test_to_absolute_path_with_relative_input_and_no_parent():
    input_path = "./input_dir"

    # care for windows, see issue 22
    Path(input_path).mkdir(exist_ok=True)

    parsed = utils.to_absolute_path(input_path)
    expected = Path.cwd() / "input_dir"
    assert parsed == expected


def test_to_absolute_path_with_relative_input_and_relative_parent():
    input_path = "./input_dir"

    # care for windows, see issue 22
    Path(input_path).mkdir(exist_ok=True)

    parsed = utils.to_absolute_path(input_path, parent=Path("."))
    expected = Path.cwd() / "input_dir"
    assert parsed == expected


def test_to_absolute_path_with_absolute_input_and_nonrelative_parent(tmp_path):
    parent = tmp_path / "parent_dir"
    input_path = tmp_path / "nonexistent_file.txt"

    with pytest.raises(ValueError) as excinfo:
        utils.to_absolute_path(str(input_path), parent=parent)

    assert "is not a subpath of parent" in str(excinfo.value)


class TestLocation:
    def test_check_location_fmt_site(self):
        test_location = "DE-Kli"
        location, fmt = utils.check_location_fmt(test_location)
        assert location == "DE-Kli"
        assert fmt == "site"

    def test_check_location_fmt_latlon(self):
        test_location = "(56.4, 112.0)"
        location, fmt = utils.check_location_fmt(test_location)
        assert location == (56.4, 112.0)
        assert fmt == "latlon"

    def test_check_location_fmt_bbox(self):
        test_location = "[19.5,20.5], [125.5,130.0]"
        location, fmt = utils.check_location_fmt(test_location)
        assert location == [[19.5, 125.5], [19.5, 130.0], [20.5, 125.5], [20.5, 130.0]]
        assert fmt == "bbox"

    def test_check_location_fmt_site_wrongfmt(self):
        test_location = "FI-Hyy_1996-2014_FLUXNET2015_Met.nc"
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)
   
        test_location = "FI-Hy"
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)

    def test_check_location_fmt_latlon_wrongfmt(self):
        test_location = "[56.4, 112.0]"
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)

    def test_check_location_fmt_bbox_wrongfmt(self):
        test_location = "[19.5, 125.5], [19.5, 130.0], [20.5, 125.5], [20.5, 130.0]"
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)

        test_location = "(19.5, 125.5), (19.5, 130.0)"
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)


class TestTime:
    @pytest.fixture
    def config_file(self):
        config_file = str(data_folder / "config_file_test.txt")
        config_ditc = config_io.read_config(config_file)
        return config_ditc

    def test_time_fmt_not_iso(self, config_file):
        config = config_file
        config["StartTime"] = "03/02/1978 12:35"
        with pytest.raises(ValueError):
            utils.check_time_fmt(config)


    def test_time_fmt_error_timerange(self, config_file):
        config = config_file
        config["StartTime"] = "2026-01-01T00:00"
        config["EndTime"] = "1926-01-01T00:00"
        with pytest.raises(ValueError):
            utils.check_time_fmt(config_file)

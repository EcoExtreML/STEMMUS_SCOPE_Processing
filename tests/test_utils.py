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

    parsed = utils.to_absolute_path(input_path, parent=Path.cwd())
    expected = Path.cwd() / "input_dir"
    assert parsed == expected


def test_to_absolute_path_with_absolute_input_and_nonrelative_parent(tmp_path):
    parent = tmp_path / "parent_dir"
    input_path = tmp_path / "nonexistent_file.txt"

    with pytest.raises(ValueError) as excinfo:
        utils.to_absolute_path(str(input_path), parent=parent)

    assert "is not a subpath of parent" in str(excinfo.value)


class TestLocation:
    valid_input = [
        # input, expected_loc, expected_fmt
        ("DE-Kli", "DE-Kli", "site"),
        ("AU-ASM", "AU-ASM", "site"),
        ("AU-GWW", "AU-GWW", "site"),
        ("CA-SF1", "CA-SF1", "site"),
        ("(56.4, 112.0)", (56.4, 112.0), "latlon"),
        ("(+56.4, -10)", (56.4, -10), "latlon"),
        ("((19.5, 125.5), (20.5, 130.0))", ((19.5, 125.5), (20.5, 130.0)), "bbox"),
        ("((19.5, -125.5), (20.5, -120.0))", ((19.5, -125.5), (20.5, -120.0)), "bbox"),
    ]

    invalid_input = [
        ("FI-Hyy_1996-2014_FLUXNET2015_Met.nc"),
        ("FI-Hy"),
        ("[56.4, 112.0]"),
        ("[19.5, 125.5], [19.5, 130.0], [20.5, 125.5], [20.5, 130.0]"),
        ("(19.5, 125.5), (19.5, 130.0)"),
        ("(19.5, 125.5), (19.5, 130.0), (20.5, 125.5), (20.5, 130.0)"),
    ]

    @pytest.mark.parametrize("input_loc, expected_loc, expected_fmt", valid_input)
    def test_check_location_fmt(self, input_loc, expected_loc, expected_fmt):
        test_location = input_loc
        location, fmt = utils.check_location_fmt(test_location)
        assert location == expected_loc
        assert fmt == expected_fmt

    @pytest.mark.parametrize("input_loc", invalid_input)
    def test_check_location_invalid_fmt(self, input_loc):
        test_location = input_loc
        with pytest.raises(ValueError):
            utils.check_location_fmt(test_location)

    def _check_lat_lon(self):
        coordinates = ((19.5, 125.5), (19.5, 130.0), (20.5, 125.5), (20.5, 130.0))
        with pytest.raises(NotImplementedError):
            utils.check_location_fmt(coordinates)


class TestTime:
    @pytest.fixture
    def config_file(self):
        config_file = str(data_folder / "config_file_test.txt")
        config_ditc = config_io.read_config(config_file)
        return config_ditc

    def test_time_fmt_NA(self, config_file):
        config = config_file
        config["StartTime"] = "NA"
        config["StartTime"] = "NA"
        utils.check_time_fmt(config["StartTime"], config["EndTime"])

    def test_time_fmt_not_iso(self, config_file):
        config = config_file
        config["StartTime"] = "03/02/1978 12:35"
        with pytest.raises(ValueError):
            utils.check_time_fmt(config["StartTime"], config["EndTime"])

    def test_time_fmt_error_timerange(self, config_file):
        config = config_file
        config["StartTime"] = "2026-01-01T00:00"
        config["EndTime"] = "1926-01-01T00:00"
        with pytest.raises(ValueError):
            utils.check_time_fmt(config["StartTime"], config["EndTime"])

    def test_time_fmt_error_invalid_mins(self, config_file):
        config = config_file
        config["StartTime"] = "1996-01-01T00:10"
        config["EndTime"] = "1996-01-02T00:00"
        with pytest.raises(ValueError):
            utils.check_time_fmt(config["StartTime"], config["EndTime"])


class TestGetForcingFile:
    @pytest.fixture
    def config_file(self):
        config_file = str(data_folder / "config_file_test.txt")
        config_ditc = config_io.read_config(config_file)
        return config_ditc

    def test_get_forcing_file_site(self, config_file):
        config = config_file
        config["Location"] = "FI-Hyy"
        forcing_file = utils.get_forcing_file(config_file)

        assert forcing_file.name == "FI-Hyy_1996-2014_FLUXNET2015_Met.nc"

    def test_get_forcing_file_site_not_found(self, config_file):
        config = config_file
        config["Location"] = "AA-Aaa"
        with pytest.raises(ValueError):
            utils.get_forcing_file(config_file)

    def test_get_forcing_file_latlon(self, config_file):
        config = config_file
        config["Location"] = "(56.4, 112.0)"
        with pytest.raises(NotImplementedError):
            utils.get_forcing_file(config_file)

    def test_get_forcing_file_bbox(self, config_file):
        config = config_file
        config["Location"] = "((19.5,125.5), (20.5,130.0))"
        with pytest.raises(NotImplementedError):
            utils.get_forcing_file(config_file)

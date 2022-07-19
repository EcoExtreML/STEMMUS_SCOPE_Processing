
from pathlib import Path
from unittest.mock import patch

import pytest
from PyStemmusScope import utils

# TODO add test for convert_to_lsm_coordinates


def test_to_absolute_path():
    input_path = "~/nonexistent_file.txt"
    parsed = utils.to_absolute_path(input_path)
    expected = Path.home() / "nonexistent_file.txt"
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

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from PyStemmusScope import config_io
from PyStemmusScope import forcing_io
from . import data_folder


numbers = "0123456789"

forcing_data_folder = data_folder / "directories" / "forcing" / "plumber2_data"


def eval_element(el):
    assert el[0] in [" ", "-"]
    assert el[1] in numbers
    assert el[2] == "."
    assert [n in numbers for n in el[3:10]]
    assert el[10] == "e"
    assert el[11] in ["+", "-"]
    assert [n in numbers for n in el[12:14]]
    assert len(el) == 14
    return True


def eval_str(fdata):
    for line in fdata.split("\n"):
        _ = [eval_element(e) for e in line.split("  ")[1:]]
    return True


@pytest.fixture(scope="session", autouse=True)
def forcing_data():
    forcing_file = forcing_data_folder / "FI-Hyy_1996-2014_FLUXNET2015_Met.nc"
    return forcing_io.read_forcing_data_plumber2(
        forcing_file, "1996-01-01T00:00", "1996-01-01T02:00"
    )


@pytest.fixture(scope="session", autouse=True)
def mdata_file(tmpdir_factory, forcing_data):
    fn_out = tmpdir_factory.mktemp("data").join("Mdata.txt")
    forcing_io.write_meteo_file(forcing_data, fn_out)
    return str(fn_out)


@pytest.fixture(scope="session", autouse=True)
def lai_file(tmpdir_factory, forcing_data):
    fn_out = tmpdir_factory.mktemp("data").join("LAI_.dat")
    forcing_io.write_lai_file(forcing_data, fn_out)
    return str(fn_out)


@pytest.fixture(scope="session", autouse=True)
def dat_files(tmpdir_factory, forcing_data):
    fnames = [
        "t_.dat",
        "Ta_.dat",
        "Rin_.dat",
        "Rli_.dat",
        "p_.dat",
        "u_.dat",
        "CO2_.dat",
        "ea_.dat",
        "year_.dat",
    ]
    write_dir = tmpdir_factory.mktemp("data")
    forcing_io.write_dat_files(forcing_data, write_dir)
    return fnames, write_dir


def test_mdata(mdata_file):
    fn_expected = forcing_data_folder / "Mdata.txt"

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(mdata_file)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


# Verifying that the actual data file passes the evaluation
def test_true_mdata_format():
    with open(forcing_data_folder / "Mdata.txt", encoding="utf-8") as f:
        content_exp = f.read()
    assert eval_str(content_exp)


# Apply the data format evaluation to the python-generated file
def test_mdata_format(mdata_file):
    with open(mdata_file, encoding="utf-8") as f:
        content = f.read()
    assert eval_str(content)


def test_lai_file(lai_file):
    fn_expected = forcing_data_folder / "LAI_.dat"

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(lai_file)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


def test_lai_file_format(lai_file):
    with open(lai_file, encoding="utf-8") as f:
        content = f.read()
    assert eval_str(content)


def test_dat_files(dat_files):
    expected_path = forcing_data_folder

    fnames, write_dir = dat_files

    for fname in fnames:
        df_expected = pd.read_fwf(Path(expected_path) / fname)
        df_written = pd.read_fwf(Path(write_dir) / fname)
        # Relatively high tolerance due to small changes in constants
        np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-3)


def test_dat_file_format(dat_files):
    fnames, write_dir = dat_files
    for fname in fnames:
        with open(Path(write_dir) / fname, encoding="utf-8") as f:
            eval_str(f.read())


def test_forcing_slice_NA():
    forcing_file = forcing_data_folder / "FI-Hyy_1996-2014_FLUXNET2015_Met.nc"
    forcing_io.read_forcing_data_plumber2(forcing_file, "NA", "NA")


def test_full_routine(tmp_path, dat_files):
    # create dummy config
    cfg_file = data_folder / "config_file_test.txt"
    config = config_io.read_config(cfg_file)
    config["Location"] = "FI-Hyy"
    config["InputPath"] = str(tmp_path)

    forcing_io.prepare_forcing(config)
    fnames, _ = dat_files
    expected_files = fnames + ["LAI_.dat", "Mdata.txt", "forcing_globals.mat"]
    for file in expected_files:
        assert (Path(tmp_path) / file).exists()

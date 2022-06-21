import os
import pytest
import numpy as np
import pandas as pd
from PyStemmusScope import forcing_io


@pytest.fixture(autouse=True)
def forcing_data():
    forcing_file = './tests/test_data/FI-Hyy_1996-2014_FLUXNET2015_Met.nc'
    return forcing_io.read_forcing_data(forcing_file)


def eval_dat():
    return 0


def test_mdata(tmp_path, forcing_data):
    fn_out = os.path.join(tmp_path, 'Mdata.txt')
    fn_expected = './tests/test_data/Mdata.txt'

    forcing_io.write_meteo_file(forcing_data, fn_out)

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(fn_out)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


def test_lai_file(tmp_path, forcing_data):
    fn_out = os.path.join(tmp_path, 'LAI_.dat')
    fn_expected = './tests/test_data/LAI_.dat'

    forcing_io.write_lai_file(forcing_data, fn_out)

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(fn_out)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


def test_dat_files(tmp_path, forcing_data):
    expected_path = './tests/test_data/'
    files = ['t_.dat', 'Ta_.dat', 'Rin_.dat',
            'Rli_.dat', 'p_.dat', 'u_.dat',
            'CO2_.dat', 'ea_.dat', 'year_.dat']

    forcing_io.write_dat_files(forcing_data, tmp_path)

    for fname in files:
        df_expected = pd.read_fwf(os.path.join(expected_path, fname))
        df_written = pd.read_fwf(os.path.join(tmp_path, fname))
        np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)

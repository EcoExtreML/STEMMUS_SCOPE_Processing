import os
import pytest
import numpy as np
import xarray as xr
import pandas as pd
from PyStemmusScope import read_forcing


def test_mdata(tmp_path):
    forcing_file = './tests/test_data/FI-Hyy_1996-2014_FLUXNET2015_Met.nc'
    fn_out = os.path.join(tmp_path, 'Mdata.txt')
    fn_expected = './tests/test_data/Mdata.txt'

    dat = read_forcing.read_forcing_data(forcing_file)

    read_forcing.write_meteo_file(dat, fn_out)

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(fn_out)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


def test_lai_file(tmp_path):
    forcing_file = './tests/test_data/FI-Hyy_1996-2014_FLUXNET2015_Met.nc'
    fn_out = os.path.join(tmp_path, 'LAI_.dat')
    fn_expected = './tests/test_data/LAI_.dat'

    dat = read_forcing.read_forcing_data(forcing_file)

    read_forcing.write_lai_file(dat, fn_out)

    df_expected = pd.read_fwf(fn_expected)
    df_written = pd.read_fwf(fn_out)

    np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-5)


def test_dat_files(tmp_path):
    forcing_file = './tests/test_data/FI-Hyy_1996-2014_FLUXNET2015_Met.nc'

    expected_path = './tests/test_data/'
    files = ['t_.dat', 'Ta_.dat', 'Rin_.dat',
            'Rli_.dat', 'p_.dat', 'u_.dat',
            'CO2_.dat', 'ea_.dat', 'year_.dat']

    dat = read_forcing.read_forcing_data(forcing_file)

    read_forcing.write_dat_files(dat, tmp_path)

    for fname in files:
        df_expected = pd.read_fwf(os.path.join(expected_path, fname))
        df_written = pd.read_fwf(os.path.join(tmp_path, fname))
        np.testing.assert_allclose(df_expected.values, df_written.values, rtol=1e-4)

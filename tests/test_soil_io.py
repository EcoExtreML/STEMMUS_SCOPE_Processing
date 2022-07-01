from pathlib import Path
import pytest
from PyStemmusScope import soil_io
from . import soil_data_folder


@pytest.fixture(autouse=True)
def coordinates():
    lat, lon = 37.933802, -107.807522 #Lat, lon of Telluride, CO
    return (lat, lon)


def test_full_routine(tmp_path, coordinates):
    lat, lon = coordinates

    matfile_path = Path(tmp_path) / 'soil_parameters.m'
    soil_io.prepare_soil_data(soil_data_folder, matfile_path, lat, lon)

    assert matfile_path.exists()

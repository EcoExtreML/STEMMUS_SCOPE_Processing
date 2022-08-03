from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import xarray as xr
from PyStemmusScope import StemmusScope
from PyStemmusScope import forcing_io
from PyStemmusScope import save
from . import data_folder


# create dummy exe file
def write_exe(in_dir):
    exe_file = Path(in_dir) / "STEMMUS_SCOPE"
    with open(exe_file, "x", encoding="utf8") as dummy_file:
        dummy_file.close()
    return exe_file

# create csv file
def write_csv(data, filename):
    with open(filename, "w", encoding="utf8") as file:
        for line in data:
            file.write(line)
            file.write('\n')


class TestSaveForcingData:
    @pytest.fixture
    def cf_convention(self, tmp_path):
        convention = [
            "short_name_alma,standard_name,long_name,definition,unit,File name,Variable name in STEMMUS-SCOPE" ,
            "LWdown_ec,surface_downwelling_longwave_flux_in_air,Downward long-wave radiation,,W/m2,ECdata.csv,Rli"
            ]

        cf_convention_file = Path(tmp_path) / "cf_convention.csv"
        write_csv(convention, cf_convention_file)
        return cf_convention_file

    @pytest.fixture
    def model_with_setup(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = write_exe(tmp_path)
        model = StemmusScope(config_file, exe_file)

        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-08-01-1200"

            _ = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "3", # less than forcing temporal range
                )
            return model

    def test_save_to_netcdf(self, cf_convention, model_with_setup):
        model = model_with_setup
        saved_nc_file = save.to_netcdf(model.config, cf_convention)

        expected_nc_file = (
            "tests/test_data/directories/output/dummy-2022-08-01-1200/dummy-2022-08-01-1200_STEMMUS_SCOPE.nc"
            )

        # check the forcing file name
        assert expected_nc_file, saved_nc_file

        # check content of netcf file
        dataset = xr.open_dataset(saved_nc_file)

        forcing_file = Path(model.config["ForcingPath"]) / model.config["ForcingFileName"]
        forcing_data = forcing_io.read_forcing_data(forcing_file)

        # check data values
        expected = forcing_data["lw_down"].values[:3]
        parsed = dataset["LWdown_ec"].values.flatten()
        np.testing.assert_array_equal( expected, parsed)
        # check size of time dimension
        assert dataset["time"].shape[0] == 3
        # check one of var attrs and if var exist
        assert dataset["LWdown_ec"].attrs["units"] == "W/m2"
        # check one of dataset attrs
        assert dataset.attrs["latitude"] == forcing_data["latitude"]
        # check one of coord attrs and if coord exist
        assert dataset["x"].attrs["long_name"] == "Gridbox longitude"
        # it shouldn't have z dimentsion
        assert "z" not in dataset


class TestSave3dData:
    @pytest.fixture
    def cf_convention(self, tmp_path):
        convention = [
            'short_name_alma,standard_name,long_name,definition,unit,File name,Variable name in STEMMUS-SCOPE',
            (
                'LWnet,surface_net_downward_longwave_flux,Net longwave radiation,'
                '"Incident longwave radiation less the simulated outgoing longwave radiation, '
                'averaged over a grid cell",W/m2,radiation.csv,Netlong'
            )
            ]

        cf_convention_file = Path(tmp_path) / "cf_convention.csv"
        write_csv(convention, cf_convention_file)
        return cf_convention_file

    @pytest.fixture
    def model_with_setup(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = write_exe(tmp_path)
        model = StemmusScope(config_file, exe_file)

        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-08-01-1200"

            _ = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "NA", # use temporal range of forcing data
                )
            return model

    @pytest.fixture(name="_make_csv_file")
    def fixture_make_csv_file(self, model_with_setup):
        model = model_with_setup
        data = [
            "simulation_number,year,DoY,Netlong",
            ",,,W m-2",
            "1,2010,0,-4.579605e+01",
            "2,2010,2.083333e-02,-4.441207e+01",
            "3,2010,4.166667e-02,-4.113654e+01",
            "4,2010,6.250000e-02,-4.351004e+01",
            "5,2010,8.333333e-02,-4.269192e+01",
        ]

        csv_file = Path(model.config["OutputPath"]) / "radiation.csv"
        write_csv(data, csv_file)

    def test_save_to_netcdf(self, cf_convention, _make_csv_file, model_with_setup):
        model = model_with_setup
        saved_nc_file = save.to_netcdf(model.config, cf_convention)

        expected_nc_file = (
            "tests/test_data/directories/output/dummy-2022-08-01-1200/dummy-2022-08-01-1200_STEMMUS_SCOPE.nc"
            )

        # check the forcing file name
        assert expected_nc_file, saved_nc_file

        # check content of netcf file
        dataset = xr.open_dataset(saved_nc_file)

        forcing_file = Path(model.config["ForcingPath"]) / model.config["ForcingFileName"]
        forcing_data = forcing_io.read_forcing_data(forcing_file)

        # check data values
        LWnet = np.array([-45.79605, -44.41207, -41.13654, -43.51004, -42.69192])
        np.testing.assert_allclose(
            LWnet, dataset["LWnet"].values.flatten(), rtol=1e-5,
            )
        # check size of time dimension
        assert dataset["time"].shape[0] == 5
        # check one of var attrs and if var exist
        assert dataset["LWnet"].attrs["units"] == "W/m2"
        # check one of dataset attrs
        assert dataset.attrs["latitude"] == forcing_data["latitude"]
        # check one of coord attrs and if coord exist
        assert dataset["x"].attrs["long_name"] == "Gridbox longitude"
        # it shouldn't have z dimentsion
        assert "z" not in dataset


class Test4dData:
    @pytest.fixture
    def cf_convention(self, tmp_path):
        convention = [
            'short_name_alma,standard_name,long_name,definition,unit,File name,Variable name in STEMMUS-SCOPE',
            (
            'SoilMoist,moisture_content_of_soil_layer,Average layer soil moisture,'
            '"Soil water content in each user-defined soil layer (3D variable). '
            'Includes the liquid, vapor and solid phases of water in the soil.",'
            'kg/m2,Sim_Theta.csv,'
            )
            ]

        cf_convention_file = Path(tmp_path) / "cf_convention.csv"
        write_csv(convention, cf_convention_file)
        return cf_convention_file

    @pytest.fixture
    def model_with_setup(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = write_exe(tmp_path)
        model = StemmusScope(config_file, exe_file)

        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-08-01-1200"

            _ = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "5",
                )
            return model

    @pytest.fixture(name="_make_csv_file")
    def fixture_make_csv_file(self, model_with_setup):
        model = model_with_setup
        data = [
            "1,2,3,5",
            "1,1,1,2",
            "m-3 m-3,m-3 m-3,m-3 m-3,m-3 m-3",
            "2.212770e-01,2.236381e-01,2.256538e-01,2.285554e-01",
            "2.218572e-01,2.235388e-01,2.251216e-01,2.276816e-01",
            "2.394262e-01,2.354697e-01,2.322302e-01,2.296094e-01",
            "2.344949e-01,2.336744e-01,2.324511e-01,2.301170e-01",
            "2.325498e-01,2.322243e-01,2.315773e-01,2.296829e-01",
        ]

        csv_file = Path(model.config["OutputPath"]) / "Sim_Theta.csv"
        write_csv(data, csv_file)

    def test_save_to_netcdf(self, cf_convention, _make_csv_file, model_with_setup):
        model = model_with_setup
        saved_nc_file = save.to_netcdf(model.config, cf_convention)

        expected_nc_file = (
            "tests/test_data/directories/output/dummy-2022-08-01-1200/dummy-2022-08-01-1200_STEMMUS_SCOPE.nc"
            )

        # check the forcing file name
        assert expected_nc_file, saved_nc_file
        # check content of netcf file
        dataset = xr.open_dataset(saved_nc_file)

        forcing_file = Path(model.config["ForcingPath"]) / model.config["ForcingFileName"]
        forcing_data = forcing_io.read_forcing_data(forcing_file)
        # check data values
        SoilMoist = np.array([2.21277, 2.236381, 2.256538, 4.571108])
        np.testing.assert_allclose(
            SoilMoist, dataset["SoilMoist"].isel(time=0).values.flatten(), rtol=1e-5,
            )
        # check size of time dimension
        assert dataset["time"].shape[0] == 5
        # check one of var attrs and if var exist
        assert dataset["SoilMoist"].attrs["units"] == "kg/m2"
        # check one of dataset attrs
        assert dataset.attrs["latitude"] == forcing_data["latitude"]
        # check one of coord attrs and if coord exist
        assert dataset["x"].attrs["long_name"] == "Gridbox longitude"
        # it should have z dimentsion
        assert "z" in dataset
        # check z attributes
        assert "layer_1: 0.0 - 1.0 cm" in dataset["z"].attrs["definition"]

class TestSaveToNetcdf:
    @pytest.fixture
    def cf_convention(self, tmp_path):
        convention = [
            'short_name_alma,standard_name,long_name,definition,unit,File name,Variable name in STEMMUS-SCOPE',
            (
                'LWnet,surface_net_downward_longwave_flux,Net longwave radiation,'
                '"Incident longwave radiation less the simulated outgoing longwave radiation, '
                'averaged over a grid cell",W/m2,radiation.csv,Netlong'
            ),
            (
                'SoilMoist,moisture_content_of_soil_layer,Average layer soil moisture,'
                '"Soil water content in each user-defined soil layer (3D variable). '
                'Includes the liquid, vapor and solid phases of water in the soil.",'
                'kg/m2,Sim_Theta.csv,'
            ),
            "LWdown_ec,surface_downwelling_longwave_flux_in_air,Downward long-wave radiation,,W/m2,ECdata.csv,Rli",
        ]

        cf_convention_file = Path(tmp_path) / "cf_convention.csv"
        write_csv(convention, cf_convention_file)
        return cf_convention_file

    @pytest.fixture
    def model_with_setup(self, tmp_path):
        config_file = str(data_folder / "config_file_test.txt")
        exe_file = write_exe(tmp_path)
        model = StemmusScope(config_file, exe_file)

        with patch("time.strftime") as mocked_time:
            mocked_time.return_value = "2022-08-01-1200"

            _ = model.setup(
                WorkDir = str(tmp_path),
                ForcingFileName = "dummy_forcing_file.nc",
                NumberOfTimeSteps = "NA",
                )
            return model

    @pytest.fixture(name="_make_csv_file")
    def fixture_make_csv_file(self, model_with_setup):
        model = model_with_setup
        data = [
            "1,2,3,5",
            "1,1,1,2",
            "m-3 m-3,m-3 m-3,m-3 m-3,m-3 m-3",
            "2.212770e-01,2.236381e-01,2.256538e-01,2.285554e-01",
            "2.218572e-01,2.235388e-01,2.251216e-01,2.276816e-01",
            "2.394262e-01,2.354697e-01,2.322302e-01,2.296094e-01",
            "2.344949e-01,2.336744e-01,2.324511e-01,2.301170e-01",
            "2.325498e-01,2.322243e-01,2.315773e-01,2.296829e-01",
        ]
        csv_file = Path(model.config["OutputPath"]) / "Sim_Theta.csv"
        write_csv(data, csv_file)

        data = [
            "simulation_number,year,DoY,Netlong",
            ",,,W m-2",
            "1,2010,0,-4.579605e+01",
            "2,2010,2.083333e-02,-4.441207e+01",
            "3,2010,4.166667e-02,-4.113654e+01",
            "4,2010,6.250000e-02,-4.351004e+01",
            "5,2010,8.333333e-02,-4.269192e+01",
        ]
        csv_file = Path(model.config["OutputPath"]) / "radiation.csv"
        write_csv(data, csv_file)

    def test_save_to_netcdf(self, cf_convention, _make_csv_file, model_with_setup):
        model = model_with_setup
        saved_nc_file = save.to_netcdf(model.config, cf_convention)

        expected_nc_file = (
            "tests/test_data/directories/output/dummy-2022-08-01-1200/dummy-2022-08-01-1200_STEMMUS_SCOPE.nc"
            )

        # check the forcing file name
        assert expected_nc_file, saved_nc_file

        # check content of netcf file
        dataset = xr.open_dataset(saved_nc_file)

        forcing_file = Path(model.config["ForcingPath"]) / model.config["ForcingFileName"]
        forcing_data = forcing_io.read_forcing_data(forcing_file)

        # check size of time dimension
        assert dataset["time"].shape[0] == forcing_data["time"].shape[0]
        # check one of var attrs and if var exist
        assert dataset["SoilMoist"].attrs["units"] == "kg/m2"
        assert dataset["LWnet"].attrs["units"] == "W/m2"
        assert dataset["LWdown_ec"].attrs["units"] == "W/m2"
        # check one of dataset attrs
        assert dataset.attrs["longitude"] == forcing_data["longitude"]
        # check one of coord attrs and if coord exist
        assert dataset["y"].attrs["long_name"] == "Gridbox latitude"
        # it should have z dimentsion
        assert "z" in dataset
        # check z attributes
        assert "layer_1: 0.0 - 1.0 cm" in dataset["z"].attrs["definition"]

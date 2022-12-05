import numpy as np
import pytest
from PyStemmusScope import variable_conversion as vc


def test_calculate_ea():

    t_air_celcius = np.array([-0.82, 42.16])
    rh = np.array([0.03, 76.35])
    calculated_ea = vc.calculate_ea(t_air_celcius, rh)

    expected_ea = np.array([1.72583644e-04, 6.31192282e+00])

    # check values
    np.testing.assert_almost_equal(expected_ea, calculated_ea)

    # check rh values
    rh = np.array([0.03, 101.35])
    with pytest.raises(ValueError) as excinfo:
        vc.calculate_ea(t_air_celcius, rh)
    assert "percentage" in str(excinfo.value)

    # check lengths
    rh = np.array([0.03])
    with pytest.raises(ValueError) as excinfo:
        vc.calculate_ea(t_air_celcius, rh)
    assert "shape" in str(excinfo.value)


def test_soil_moisture():
    volumetric_water_content = np.array([0.22, 0.65])
    thickness = np.array([1, 20])
    calculated_soil_moisture =vc.soil_moisture(volumetric_water_content, thickness)

    expected_soil_moisture = np.array([220., 13000.])
    np.testing.assert_almost_equal(expected_soil_moisture, calculated_soil_moisture)

    # check lengths
    thickness = np.array([1])
    with pytest.raises(ValueError) as excinfo:
        vc.soil_moisture(volumetric_water_content, thickness)
    assert "shape" in str(excinfo.value)

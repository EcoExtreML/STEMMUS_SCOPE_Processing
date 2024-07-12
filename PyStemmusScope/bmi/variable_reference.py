"""Variable reference to inform the BMI implementation."""
from dataclasses import dataclass


@dataclass
class BmiVariable:
    """Holds all info to inform the BMI implementation."""

    name: str
    dtype: str
    input: bool
    output: bool
    units: str
    grid: int
    loc: list[str]


VARIABLES: tuple[BmiVariable, ...] = (
    # atmospheric vars:
    BmiVariable(
        name="respiration",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["fluxes", "Resp"],
    ),
    BmiVariable(
        name="evaporation_total",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["EVAP"],
    ),
    # soil vars:
    BmiVariable(
        name="soil_temperature",
        dtype="float64",
        input=True,
        output=True,
        units="degC",
        grid=1,
        loc=["TT"],
    ),
    BmiVariable(
        name="soil_moisture",
        dtype="float64",
        input=True,
        output=True,
        units="m3 m-3",
        grid=1,
        loc=["SoilVariables", "Theta_U"],
    ),
    BmiVariable(
        name="soil_root_water_uptake",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["RWUs"],
    ),
    # surface runoff
    BmiVariable(
        name="surface_runoff_total",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["RS"],
    ),
    BmiVariable(
        name="surface_runoff_hortonian",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["ForcingData", "R_Dunn"],
    ),
    BmiVariable(
        name="surface_runoff_dunnian",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["ForcingData", "R_Hort"],
    ),
    # groundwater vars (STEMMUS_SCOPE)
    BmiVariable(
        name="groundwater_root_water_uptake",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["RWUg"],
    ),
    BmiVariable(
        name="groundwater_recharge",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        loc=["gwfluxes", "recharge"],
    ),
    # groundwater (coupling) vars
    BmiVariable(
        name="groundwater_coupling_enabled",
        dtype="bool",
        input=True,
        output=False,
        units="-",
        grid=0,
        loc=["GroundwaterSettings", "GroundwaterCoupling"],
    ),
    BmiVariable(
        name="groundwater_head_bottom_layer",
        dtype="float64",
        input=True,
        output=False,
        units="cm",
        grid=0,
        loc=["GroundwaterSettings", "headBotmLayer"],
    ),
    BmiVariable(
        name="groundwater_temperature",
        dtype="float64",
        input=True,
        output=False,
        units="degC",
        grid=0,
        loc=["GroundwaterSettings", "tempBotm"],
    ),
    BmiVariable(
        name="groundwater_elevation_top_aquifer",
        dtype="float64",
        input=True,
        output=False,
        units="cm",
        grid=0,
        loc=["GroundwaterSettings", "toplevel"],
    ),
)

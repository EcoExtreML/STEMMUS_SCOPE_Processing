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
    keys: list[str]
    all_timesteps: bool = False


VARIABLES: tuple[BmiVariable, ...] = (
    # atmospheric vars:
    BmiVariable(
        name="respiration",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["fluxes", "Resp"],
    ),
    BmiVariable(
        name="precipitation",
        dtype="float64",
        input=True,
        output=False,
        units="cm s-1",
        grid=0,
        keys=["ForcingData", "Precip_msr"],
        all_timesteps=True,
    ),
    BmiVariable(
        name="applied_infiltration",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["ForcingData", "applied_inf"],
        all_timesteps=True,
    ),
    BmiVariable(
        name="soil_evaporation",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["Evap"],
    ),
    BmiVariable(
        name="transpiration",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["Trap"],
    ),
    # soil vars:
    BmiVariable(
        name="soil_temperature",
        dtype="float64",
        input=True,
        output=True,
        units="degC",
        grid=1,
        keys=["TT"],
    ),
    BmiVariable(
        name="soil_moisture",
        dtype="float64",
        input=True,
        output=True,
        units="m3 m-3",
        grid=1,
        keys=["SoilVariables", "Theta_U"],
    ),
    BmiVariable(
        name="soil_root_water_uptake",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["RWUs"],
    ),
    # surface runoff
    BmiVariable(
        name="surface_runoff_total",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["RS"],
    ),
    BmiVariable(
        name="surface_runoff_hortonian",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["ForcingData", "R_Dunn"],
        all_timesteps=True,
    ),
    BmiVariable(
        name="surface_runoff_dunnian",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["ForcingData", "R_Hort"],
        all_timesteps=True,
    ),
    # groundwater vars (STEMMUS_SCOPE)
    BmiVariable(
        name="groundwater_root_water_uptake",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["RWUg"],
    ),
    BmiVariable(
        name="groundwater_recharge",
        dtype="float64",
        input=False,
        output=True,
        units="cm s-1",
        grid=0,
        keys=["gwfluxes", "recharge"],
    ),
    BmiVariable(
        name="groundwater_recharge_index",
        dtype="int64",
        input=False,
        output=True,
        units="-",
        grid=0,
        keys=["gwfluxes", "indxRchrg"],
    ),
    # groundwater (coupling) vars
    BmiVariable(
        name="groundwater_coupling_enabled",
        dtype="bool",
        input=True,
        output=False,
        units="-",
        grid=0,
        keys=["GroundwaterSettings", "GroundwaterCoupling"],
    ),
    BmiVariable(
        name="groundwater_head_bottom_layer",
        dtype="float64",
        input=True,
        output=False,
        units="cm",
        grid=0,
        keys=["GroundwaterSettings", "headBotmLayer"],
    ),
    BmiVariable(
        name="groundwater_temperature",
        dtype="float64",
        input=True,
        output=False,
        units="degC",
        grid=0,
        keys=["GroundwaterSettings", "tempBotm"],
    ),
    BmiVariable(
        name="groundwater_elevation_top_aquifer",
        dtype="float64",
        input=True,
        output=False,
        units="cm",
        grid=0,
        keys=["GroundwaterSettings", "topLevel"],
    ),
)

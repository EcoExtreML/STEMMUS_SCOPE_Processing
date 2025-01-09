# Global data for STEMMUS_SCOPE

This document outlines which, where and how we download the "global" input data for the
model.

## Download and prepare data

Tha python package [`zampy`](https://zampy.readthedocs.io/) can be used to
download and prepare the data.

## Data of Climate Data store (CDS)

Many of the forcing-related data is available in the era5 reanalysis data.

**era5 variables**:

- mean_total_precipitation_rate
- surface_thermal_radiation_downwards
- surface_solar_radiation_downwards
- surface_pressure
- 10m_u_component_of_wind
- 10m_v_component_of_wind

**era5-land variables**:

- 2m_temperature
- 2m_dewpoint_temperature

**era5-land soil initial conditions**:

For running STEMMUS-SCOPE, global data is also required for the soil initial conditions. These are retrieved from ERA5-land.

## CO2 data from Atmosphere Data Store (ADS)

CO2 data is available in the CAMS dataset. A simple check for the parsing of the
data is in `global_data/data_analysis_notebooks/parse_CO2_data.ipynb`.

## Canopy height data from ETH

The canopy height data is described in:
[https://langnico.github.io/globalcanopyheight/](https://langnico.github.io/globalcanopyheight/)
and available
[here](https://share.phys.ethz.ch/~pf/nlangdata/ETH_GlobalCanopyHeight_10m_2020_version1/3deg_cogs/).
A simple example for the parsing of the data is in
`global_data/data_analysis_notebooks/parse_canopy_height.ipynb`.

## DEM data from Copernicus

DEM data is provided by Copernicus, see
[here](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM).
A simple example for the parsing of the data is in
`global_data/data_analysis_notebooks/parse_dem.ipynb`.

## LAI from Climate Data Store (CDS)

LAI data was retrieved from the CDS. However, there are some downloading issues
with the `satellite-lai-fapar` dataset. A simple example for parsing the LAI
data is in `global_data/data_analysis_notebooks/parse_LAI.py`.

## Land cover from Climate Data Store (CDS)

Land cover data is available at [https://cds.climate.copernicus.eu/datasets/satellite-land-cover](https://cds.climate.copernicus.eu/datasets/satellite-land-cover).

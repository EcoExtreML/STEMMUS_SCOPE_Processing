# Global data for STEMMUS_SCOPE

This document outlines which, where and how we download the "global" input data for the
model.

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

CO2 data is available in the CAMS dataset. An ADS script that can download the
data is available at `download_scripts/download_CAMS_CO2.py`.

A simple check for the parsing of the data is in `data_analysis_notebooks/parse_CO2_data.ipynb`.

## Canopy height data from ETH

The canopy height data is described in: https://langnico.github.io/globalcanopyheight/

Get data from:
https://share.phys.ethz.ch/~pf/nlangdata/ETH_GlobalCanopyHeight_10m_2020_version1/3deg_cogs/
This can be done with, e.g. a wget command.

The valid filenames are all in `download_scripts/valid_eth_canopy_height_files.txt`.

A simple example for the parsing of the data is in `data_analysis_notebooks/parse_canopy_height.ipynb`.

## DEM data from Copernicus

To download the DEM data:
`wget https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-90-DGED__2021_1/Copernicus_DSM_30_N35_00_E012_00.tar`
unzip and extract tif file.

All valid DEM urls are in `download_scripts/valid_dem_urls.csv`.

A word doc for instructions is available [here](https://spacedata.copernicus.eu/documents/20123/121286/Copernicus+DEM+Open+HTTPS+Access.pdf/36c9adad-8488-f463-af43-573e68b7f481?t=1669283200177)

A simple example for the parsing of the data is in `data_analysis_notebooks/parse_dem.ipynb`.

## LAI from Climate Data Store (CDS)

LAI data was retrieved from the CDS. However, there are some downloading issues with
the `satellite-lai-fapar` dataset. A ticket has been opened at the ECMWF.

The download script for downloading the LAI data is available under `download_scripts/download_FAPAR_LAI.py`.

A simple example for parsing the LAI data is in `data_analysis_notebooks/parse_LAI.py`.

## Land cover from Climate Data Store (CDS)

Land cover data is available at [https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=overview](https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=overview).

## Download and prepare data

Tha python package [`zampy`](https://zampy.readthedocs.io/) can be used to
download and prepare the data.

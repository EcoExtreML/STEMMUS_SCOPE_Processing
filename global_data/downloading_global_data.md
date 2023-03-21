# Global data for STEMMUS_SCOPE
This document outlines which, where and how we download the "global" input data for the
model.

## Data downloaded through era5cli
Many of the forcing-related data is available in the era5 reanalysis data.

**era5 variables**:
 - mean_total_precipitation_rate
 - surface_thermal_radiation_downwards
 - surface_solar_radiation_downwards
 - surface_pressure
 - 10m_u_component_of_wind
 - 10m_v_component_of_wind

These can be downloaded using [era5cli](https://era5cli.readthedocs.io/) as:
```
era5cli hourly --variables 10m_u_component_of_wind 10m_v_component_of_wind mean_total_precipitation_rate surface_pressure surface_thermal_radiation_downwards surface_solar_radiation_downwards --startyear 2016 --endyear 2016 --levels surface --area 65 20 60 24
```

Note: the year range is set with `--startyear` and `--endyear`. The lat/lon bounding box is set with `--area`.

**era5-land variables**:
 - 2m_temperature
 - 2m_dewpoint_temperature

We would like to run the following command:
```
era5cli hourly --variables 2m_temperature  2m_dewpoint_temperature  --startyear 2016 --endyear 2016 --months 1 --land --levels surface --area 54 3 50 8
```
However, currently this raises a too-many-requests error. Until that is fixed, we can use
the cds. See `download_era5land_monthly.py`.

**era5-land soil initial conditions**

For running STEMMUS-SCOPE, global data is also required for the soil initial conditions. These are retrieved from ERA5-land, using the following command:
```
era5cli hourly --startyear 2014 --endyear 2014 --hours 0 --land --levels surface --area 65 20 60 24 --variables skin_temperature soil_temperature_level_1 soil_temperature_level_2 soil_temperature_level_3 soil_temperature_level_4 volumetric_soil_water_layer_1 volumetric_soil_water_layer_2 volumetric_soil_water_layer_3 volumetric_soil_water_layer_4
```

## CO2 data
CO2 data is available in the CAMS dataset. An ADS script that can download the data is
 available at `download_scripts/download_CAMS_CO2.py`.

A simple check for the parsing of the data is in `data_analysis_notebooks/parse_CO2_data.ipynb`.


## Canopy height data
The canopy height data is described in: https://langnico.github.io/globalcanopyheight/

Get data from:
https://share.phys.ethz.ch/~pf/nlangdata/ETH_GlobalCanopyHeight_10m_2020_version1/3deg_cogs/
This can be done with, e.g. a wget command.

The valid filenames are all in `download_scripts/valid_eth_canopy_height_files.txt`.

A simple example for the parsing of the data is in `data_analysis_notebooks/parse_canopy_height.ipynb`.


## DEM data
To download the DEM data:
`wget https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-90-DGED__2021_1/Copernicus_DSM_30_N35_00_E012_00.tar`
unzip and extract tif file.

All valid DEM urls are in `download_scripts/valid_dem_urls.csv`.

A word doc for instructions is available [here](https://spacedata.copernicus.eu/documents/20123/121286/Copernicus+DEM+Open+HTTPS+Access.pdf/36c9adad-8488-f463-af43-573e68b7f481?t=1669283200177)

A simple example for the parsing of the data is in `data_analysis_notebooks/parse_dem.ipynb`.


## LAI

LAI data was retrieved from the CDS. However, there are some downloading issues with
the `satellite-lai-fapar` dataset. A ticket has been opened at the ECMWF.

The download script for downloading the LAI data is available under `download_scripts/download_FAPAR_LAI.py`.

A simple example for parsing the LAI data is in `data_analysis_notebooks/parse_LAI.py`.

## Land cover

Land cover data is currently not implemented yet either.

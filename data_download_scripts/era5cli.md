
## Data downloaded through era5cli


era5-land variables:
 - 2m_temperature
 - 2m_dewpoint_temperature
```
era5cli hourly --variables 2m_temperature  2m_dewpoint_temperature  --startyear 2016 --endyear 2016 --months 1 --land --levels surface --area 54 3 50 8
```

----

era5 variables:
 - mean_total_precipitation_rate
 - surface_thermal_radiation_downwards
 - surface_solar_radiation_downwards
 - surface_pressure
 - 10m_u_component_of_wind
 - 10m_v_component_of_wind

```
era5cli hourly --variables 10m_u_component_of_wind 10m_v_component_of_wind mean_total_precipitation_rate surface_pressure surface_thermal_radiation_downwards surface_solar_radiation_downwards --startyear 2016 --endyear 2016 --levels surface --area 65 20 60 24
```

----
https://langnico.github.io/globalcanopyheight/
Get data from:
https://share.phys.ethz.ch/~pf/nlangdata/ETH_GlobalCanopyHeight_10m_2020_version1/3deg_cogs/

----DEM
wget https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-90-DGED__2021_1/Copernicus_DSM_30_N35_00_E012_00.tar
unzip and extract tif file.

word (?!) doc for instructions here: https://spacedata.copernicus.eu/documents/20123/121286/Copernicus+DEM+Open+HTTPS+Access.pdf/36c9adad-8488-f463-af43-573e68b7f481?t=1669283200177


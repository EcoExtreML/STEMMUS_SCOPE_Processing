
## Data downloaded through era5cli


era5-land variables:
 - 2m_temperature
 - 2m_dewpoint_temperature
 - 10m_u_component_of_wind
 - 10m_v_component_of_wind
```
era5cli hourly --variables 2m_temperature  2m_dewpoint_temperature 10m_u_component_of_wind 10m_v_component_of_wind --startyear 2016 --endyear 2016 --months 1 --land --levels surface --area 54 3 50 8
```

----

era5 variables:
 - mean_total_precipitation_rate
 - surface_thermal_radiation_downwards
 - surface_solar_radiation_downwards
 - surface_pressure

```
era5cli hourly --variables mean_total_precipitation_rate surface_pressure surface_thermal_radiation_downwards surface_solar_radiation_downwards --startyear 2016 --endyear 2016 --months 1 --levels surface --area 54 3 50 8
```


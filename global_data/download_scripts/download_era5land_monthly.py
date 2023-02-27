"""Download monthly ERA5-land data using the cdsapi."""
import itertools
from pathlib import Path
import cdsapi
import certifi
import urllib3


http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

with (Path.home() / ".cdsloginrc").open(encoding="utf8") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()

c = cdsapi.Client(
    url="https://cds.climate.copernicus.eu/api/v2",
    key=f"{uid}:{api_key}",
    verify=True,
)

variables = ["2m_dewpoint_temperature", "2m_temperature"]
years = [2014]
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

for var, year, month in itertools.product(variables, years, months):
    # fmt: off
    c.retrieve(
        "reanalysis-era5-land",
        {
            "variable": [var],
            "year": f"{year}",
            "month": month,
            "day": [
                "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
                "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
                "23", "24", "25", "26", "27", "28", "29", "30", "31",
            ],
            "time": [
                "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00",
                "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
                "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                "21:00", "22:00", "23:00",
            ],
            "area": [65, 20, 60, 24],
            "format": "netcdf",
        },
        f"era5-land_{var}_{year}-{month}_FI-Hyy.nc",
    )
    # fmt: on

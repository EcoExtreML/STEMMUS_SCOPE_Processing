"""Download CAMS data using the cdsapi."""
from pathlib import Path
import cdsapi
import certifi
import urllib3


# UID+api key is read here:
with (Path.home() / ".adsloginrc").open(encoding="utf8") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()

http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

c = cdsapi.Client(
    url="https://ads.atmosphere.copernicus.eu/api/v2",
    key=f"{uid}:{api_key}",
    verify=True,
)

c.retrieve(
    "cams-global-ghg-reanalysis-egg4",
    {
        "format": "netcdf",
        "model_level": "60",  # surface level data
        "date": "2003-01-02/2020-12-31",
        "step": ["0", "3", "6", "9", "12", "15", "18", "21"],
        "variable": "carbon_dioxide",
    },
    "CAMS_CO2_2003-2020.nc",
)

import cdsapi
import certifi
import urllib3
from pathlib import Path

# UID+api key is read here:
with open(Path.home() / ".adsloginrc") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

c = cdsapi.Client(
    url="https://ads.atmosphere.copernicus.eu/api/v2",
    key=f"{uid}:{api_key}",
    verify=True,
)

names = ("NE", "SE", "NW", "SW")
area_blocks = (
   #   N,    W,    S,    E
    [ 90,    0,    0,  180],
    [-0.1,   0,  -90,  180],
    [ 90,  -180,   0, -0.1],
    [-0.1, -180, -90, -0.1],
)

for name, area in zip(names, area_blocks):
    c.retrieve(
        "cams-global-ghg-reanalysis-egg4",
        {
            "format": "netcdf",
            "model_level": "60",  # surface level data
            "date": "2003-01-02/2020-12-31",
            "step": [
                "0", "3", "6", "9", "12", "15", "18", "21"
            ],
            "area": area,
            "variable": "carbon_dioxide",
        },
        f"CAMS_CO2_2003-2020_{name}.nc"
    )

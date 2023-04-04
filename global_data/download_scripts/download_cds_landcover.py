"""Download land cover data using the cdsapi."""
from pathlib import Path
import cdsapi


with (Path.home() / ".cdsloginrc").open(encoding="utf8") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()


c = cdsapi.Client(
    url="https://cds.climate.copernicus.eu/api/v2",
    key=f"{uid}:{api_key}",
    verify=True,
)


years = [2013]


for year in years:
    c.retrieve(
        "satellite-land-cover",
        {
            "variable": "all",
            "format": "zip",
            "year": f"{year}",
            "version": "v2.0.7cds",
        },
        f"cds_landcover_{year}.zip",
    )

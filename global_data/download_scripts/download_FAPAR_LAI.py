"""Download monthly ERA5-land data using the cdsapi."""
import itertools
from pathlib import Path
import cdsapi
from pathos.threading import ThreadPool as Pool


N_TRIES = 3


with (Path.home() / ".cdsloginrc").open(encoding="utf8") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()


def request_lai_data(year, month):
    """Request the LAI data from the CDS."""
    c = cdsapi.Client(
        url="https://cds.climate.copernicus.eu/api/v2",
        key=f"{uid}:{api_key}",
        verify=True,
        retry_max=1,
    )

    c.retrieve(
        "satellite-lai-fapar",
        {
            "format": "zip",
            "variable": "lai",
            "satellite": ("proba" if year >= 2014 else "spot"),
            "sensor": "vgt",
            "horizontal_resolution": "1km",
            "product_version": "V1",
            "year": f"{year}",
            "month": [
                f"{month}",
            ],
            "nominal_day": [
                "10",
                "20",
                "28",
                "30",
                "31",
            ],
        },
        f"LAI_fapar_vgt_{year}-{month}.zip",
    )


if __name__ == "__main__":
    years = list(range(2012, 2018))
    months = [str(x).rjust(2, "0") for x in range(1, 13)]

    _years, _months = map(list, zip(*itertools.product(years, months)))

    pool = Pool(nodes=2)
    pool.map(request_lai_data, _years, _months)

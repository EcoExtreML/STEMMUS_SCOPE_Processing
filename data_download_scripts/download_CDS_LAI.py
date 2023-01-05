import cdsapi
import certifi
import urllib3
from pathlib import Path

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

with open(Path.home() / ".cdsloginrc") as f:
    uid = f.readline().strip()
    api_key = f.readline().strip()

c = cdsapi.Client(
    url="https://cds.climate.copernicus.eu/api/v2",
    key=f"{uid}:{api_key}",
    verify=True,
)

years = [2016]

for year in years:
    c.retrieve(
        'satellite-lai-fapar',
        {
            'format': 'zip',
            'variable': 'lai',
            'sensor': 'vgt',
            'satellite': [
                'proba', 'spot',
            ],
            'horizontal_resolution': '1km',
            'product_version': 'V3',
            'year': [f"{year}"],
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'nominal_day': [
                '10', '20', '28',
                '29', '30', '31',
            ],
        },
        f'LAI_{year}.zip')

from pathlib import Path
import xarray as xr


folder = "C:/STEMMUS_SCOPE_data/global/dem"
fname = "Copernicus_DSM_30_N61_00_E024_00_DEM.tif"

lat = 61.8474
lon = 24.2948
file = Path(folder) / fname

ds = xr.open_dataarray(file, engine="rasterio")

elevation = ds.sel(x=lon, y=lat, method="nearest")
print(elevation.values[0])
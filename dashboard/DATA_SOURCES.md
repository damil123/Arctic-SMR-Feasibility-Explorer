# Data Sources for the Feasibility Model — Status & Roadmap

## What changed in this version
**Open-Meteo (ERA5 reanalysis) is now implemented** as the primary live data source.
The app fetches a real 10-year monthly climatology for the queried coordinate; NASA POWER
remains a cross-check; the ML surrogate is the instant/offline fallback. The generator can
also build the training grid from real Open-Meteo data (`python generate_training_data.py
--source openmeteo`) instead of the calibrated synthetic grid. The items below the
"Implemented" section are the recommended next integrations, prioritised by impact vs effort.

## Status summary

| Status | Source | Role | Access | Auth |
|---|---|---|---|---|
| **Implemented** | **Open-Meteo (ERA5)** | Primary live climate (solar/wind/temp) | REST JSON GET | None |
| Implemented | NASA POWER | Live cross-check + grid calibration | REST JSON GET | None |
| Implemented | ML surrogate | Instant/offline fallback | local model | — |
| Recommended | NRCan Remote Communities Energy DB | Real demand + diesel labels | ESRI REST + CSV | None |
| Recommended | Global Wind Atlas (EMD API) | Hub-height wind resource | REST (OpenAPI) | Free, rate-limited |
| Recommended | Permafrost — Obu et al. (APGC) | Real ground temp / permafrost | NetCDF/GeoTIFF | None |
| Recommended | Open-Meteo Elevation (GLO-90) | Terrain feature | REST JSON GET | None |
| Recommended | NSIDC sea-ice concentration | Resupply/logistics risk | OPeNDAP / ERDDAP | Earthdata (free) |

---

## Implemented

### Open-Meteo (ERA5) — `openmeteo.py`
Free, no API key, global; historical data is ERA5 reanalysis (0.25°, from 1940). Replaces
the single-point + synthetic assumption with **real** data for any coordinate.

- **Variables used:** `shortwave_radiation_sum` → solar (kWh/m²/day), `wind_speed_10m_max`
  → wind (m/s, gust→mean scaled), `temperature_2m_mean` → temp (°C).
- **Endpoint:** `https://archive-api.open-meteo.com/v1/archive`
- **Example:** `archive-api.open-meteo.com/v1/archive?latitude=68&longitude=-110&start_date=2015-01-01&end_date=2024-12-31&daily=shortwave_radiation_sum,wind_speed_10m_max,temperature_2m_mean&timezone=GMT`
- **How it's wired:** `openmeteo.fetch_climatology()` pulls daily ERA5, aggregates to a
  12-month climatology in the same schema as NASA POWER, caches to `cache/`, and returns
  `None` on failure so the app falls back. `app.py` tries Open-Meteo → NASA → surrogate.
  `generate_training_data.py --source openmeteo` builds the grid from real data, filling any
  unreachable point synthetically.
- **Caveat:** rate-limited for free use; the daily-max→mean wind conversion (`×0.70`) is a
  documented approximation — Global Wind Atlas (below) is the upgrade for bankable wind.

### NASA POWER — `nasa_power.py`
Retained as an independent live cross-check and as the calibration anchor for the synthetic
grid (`data/nasa_power_arctic_68N_110W.csv`). Docs: `power.larc.nasa.gov/docs/services/api/temporal/`.

---

## Recommended next (highest value first)

### 1. NRCan Remote Communities Energy Database (RCED) — real demand + labels
The only national public dataset of Canada's off-grid communities: location, population,
main power source, generation. This is the missing **ground truth**.
- **Access:** ESRI REST (JSON/GeoJSON) + CSV.
  - REST: `https://geoappext.nrcan.gc.ca/arcgis/rest/services/FGP/remote_communities_2018_en/MapServer/0`
  - Query: `.../0/query?where=1%3D1&outFields=*&f=geojson`
  - CSV/portal: `open.canada.ca/data/en/dataset/0e76433c-7aeb-46dc-a019-11db10ee28dd`
- **Use:** replace the per-person demand constant with real generation/population, and train
  the classifier on actual diesel-dependence — turning it from a rule-reproducer into a
  genuine supervised model. (Canada-only; pair with Open-Meteo for circumpolar scoring.)

### 2. Global Wind Atlas (EMD global-atlas-services API) — hub-height wind
Microscale wind at 50–200 m, far better than ERA5 10 m wind (the model's weakest term).
- **Access:** REST/OpenAPI (`help.emd.dk` → Global Atlas Services); Python client; free but
  **≤20 requests / rolling 10 min** — batch and cache.
- **Use:** add hub-height wind as a feature and to the wind-power term; cross-check ERA5.

### 3. Permafrost — Obu et al. Ground Temperature Map (APGC)
Replaces the air-temperature permafrost heuristic with modelled ground data.
- **Access:** download GeoTIFF/SHP/NetCDF (resampled ~5/10/25 km) from `apgc.awi.de/dataset/pex`;
  also NSIDC GGD318. Static raster — bundle a resampled copy and sample by lat/lon.
- **Use:** real permafrost probability + ground temperature in the siting score.

### 4. Elevation / terrain
- **Open-Meteo Elevation API** — `api.open-meteo.com/v1/elevation?latitude=68&longitude=-110`
  (Copernicus GLO-90, 90 m, free) or **OpenTopoData** (1000 calls/day).
- **Use:** terrain as a surrogate/siting feature; conditions wind and temperature.

### 5. NSIDC sea-ice concentration — logistics
Arctic resupply runs on a summer sealift window; ice duration is a real deployment-risk factor.
- **Access:** NSIDC Data Map Services API, OPeNDAP, ERDDAP, or NOAA PolarWatch ERDDAP mirror;
  Earthdata login (free) for some products.
- **Use:** derive an ice-free-months feature → logistics-risk flag.

### Reference / cross-validation
Copernicus CDS (raw ERA5 fields, needs free account) and PVGIS (solar/PV validation).

## Suggested build order
1. ✅ Open-Meteo real climate (done).
2. NRCan RCED → real demand + supervised diesel labels (retrain classifier).
3. Global Wind Atlas + Obu permafrost as features.
4. Elevation + sea-ice as terrain/logistics signals.

## Sources
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) · [Elevation API](https://open-meteo.com/en/docs/elevation-api)
- [NRCan Remote Communities Energy Database](https://open.canada.ca/data/en/dataset/0e76433c-7aeb-46dc-a019-11db10ee28dd) · [ESRI REST layer](https://geoappext.nrcan.gc.ca/arcgis/rest/services/FGP/remote_communities_2018_en/MapServer/0)
- [Global Wind Atlas](https://globalwindatlas.info/download/gis-files) · [EMD Global Atlas Services API](https://help.emd.dk/mediawiki/index.php/EMD-API_-_Global_Atlas_Services)
- [Permafrost — Obu et al. (APGC)](https://apgc.awi.de/dataset/pex) · [NSIDC GGD318](https://nsidc.org/data/ggd318/versions/2)
- [Open Topo Data](https://www.opentopodata.org/) · [NSIDC data access](https://nsidc.org/data/user-resources/help-center/can-i-access-nsidc-data-using-api-or-ftp) · [NOAA PolarWatch sea-ice](https://polarwatch.noaa.gov/catalog/ice-sq-nh-nsidc-cdr/download/)
- [NASA POWER Climatology API](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/)

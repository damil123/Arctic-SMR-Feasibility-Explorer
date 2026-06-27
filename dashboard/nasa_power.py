"""
nasa_power.py — Live client for the NASA POWER climatology API with on-disk
caching and graceful failure.

Endpoint: temporal/climatology/point returns 10-year monthly means for each
parameter as {'JAN': v, ..., 'DEC': v, 'ANN': v}. Parameters used:
  ALLSKY_SFC_SW_DWN  surface downwelling shortwave  (kWh/m^2/day, RE community)
  WS10M              10 m wind speed                (m/s)
  T2M                2 m air temperature            (deg C)

fetch_climatology() returns a 12-row DataFrame or None on any failure, so the
app can fall back to the ML surrogate without crashing.
"""
from __future__ import annotations
import os
import json
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
BASE = 'https://power.larc.nasa.gov/api/temporal/climatology/point'
MONTH_KEYS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


def _cache_path(lat, lon):
    return os.path.join(CACHE, f'power_{lat:.2f}_{lon:.2f}.csv')


def fetch_climatology(lat, lon, start=2015, end=2024, timeout=20, use_cache=True):
    """Return monthly climatology DataFrame [month, solar_kwh_m2_day, wind_ms,
    temp_c] from NASA POWER, or None if the request fails."""
    os.makedirs(CACHE, exist_ok=True)
    cp = _cache_path(lat, lon)
    if use_cache and os.path.exists(cp):
        try:
            return pd.read_csv(cp)
        except Exception:
            pass
    try:
        import requests  # imported lazily so the surrogate path needs no network stack
        params = {
            'parameters': 'ALLSKY_SFC_SW_DWN,WS10M,T2M',
            'community': 'RE', 'longitude': lon, 'latitude': lat,
            'start': start, 'end': end, 'format': 'JSON',
        }
        r = requests.get(BASE, params=params, timeout=timeout)
        r.raise_for_status()
        param = r.json()['properties']['parameter']
        rows = []
        for i, mk in enumerate(MONTH_KEYS, start=1):
            rows.append({
                'month': i,
                'solar_kwh_m2_day': param['ALLSKY_SFC_SW_DWN'][mk],
                'wind_ms': param['WS10M'][mk],
                'temp_c': param['T2M'][mk],
            })
        df = pd.DataFrame(rows)
        # POWER fill value for missing data is -999
        if (df[['solar_kwh_m2_day', 'wind_ms', 'temp_c']] < -900).any().any():
            return None
        df.to_csv(cp, index=False)
        return df
    except Exception:
        return None

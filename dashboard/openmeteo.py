"""
openmeteo.py — Live client for the Open-Meteo Historical Weather API (ERA5
reanalysis). Free, no API key. Returns the same 12-row monthly climatology schema
as nasa_power.py so the app and scoring are source-agnostic.

We pull daily ERA5 fields over a multi-year window and aggregate to a monthly
mean climatology:
  shortwave_radiation_sum (MJ/m^2)  -> solar_kwh_m2_day   (/3.6)
  wind_speed_10m_max (km/h)         -> wind_ms             (/3.6, *0.7 gust->mean)
  temperature_2m_mean (deg C)       -> temp_c

fetch_climatology() returns a 12-row DataFrame or None on any failure, so the app
falls back to NASA POWER or the ML surrogate without crashing.
"""
from __future__ import annotations
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
BASE = 'https://archive-api.open-meteo.com/v1/archive'
# ERA5 daily 10 m wind comes as a daily max in km/h; scale gust-ish max toward a
# representative mean wind speed. Tunable; documented as an approximation.
GUST_TO_MEAN = 0.70


def _cache_path(lat, lon):
    return os.path.join(CACHE, f'openmeteo_{lat:.2f}_{lon:.2f}.csv')


def fetch_climatology(lat, lon, start_year=2015, end_year=2024, timeout=30, use_cache=True):
    """Return monthly climatology [month, solar_kwh_m2_day, wind_ms, temp_c] from
    Open-Meteo ERA5, or None on failure."""
    os.makedirs(CACHE, exist_ok=True)
    cp = _cache_path(lat, lon)
    if use_cache and os.path.exists(cp):
        try:
            return pd.read_csv(cp)
        except Exception:
            pass
    try:
        import requests
        params = {
            'latitude': lat, 'longitude': lon,
            'start_date': f'{start_year}-01-01', 'end_date': f'{end_year}-12-31',
            'daily': 'shortwave_radiation_sum,wind_speed_10m_max,temperature_2m_mean',
            'timezone': 'GMT',
        }
        r = requests.get(BASE, params=params, timeout=timeout)
        r.raise_for_status()
        d = r.json()['daily']
        daily = pd.DataFrame({
            'date': pd.to_datetime(d['time']),
            'solar': d['shortwave_radiation_sum'],   # MJ/m^2/day
            'wind': d['wind_speed_10m_max'],          # km/h
            'temp': d['temperature_2m_mean'],         # deg C
        }).dropna()
        if daily.empty:
            return None
        daily['month'] = daily['date'].dt.month
        agg = daily.groupby('month').mean(numeric_only=True)
        out = pd.DataFrame({
            'month': range(1, 13),
            'solar_kwh_m2_day': (agg['solar'] / 3.6).reindex(range(1, 13)).values,
            'wind_ms': (agg['wind'] / 3.6 * GUST_TO_MEAN).reindex(range(1, 13)).values,
            'temp_c': agg['temp'].reindex(range(1, 13)).values,
        })
        if out[['solar_kwh_m2_day', 'wind_ms', 'temp_c']].isnull().any().any():
            return None
        out = out.round(3)
        out.to_csv(cp, index=False)
        return out
    except Exception:
        return None

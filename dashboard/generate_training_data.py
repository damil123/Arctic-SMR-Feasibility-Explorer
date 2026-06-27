"""
generate_training_data.py — Build a circumpolar Arctic climate grid for the ML
surrogate, calibrated to the real NASA POWER record at 68 N, 110 W.

Why synthetic-but-grounded: the live NASA POWER API serves one point per call,
so building a dense training grid by hammering the API is slow and rate-limited.
Instead we model the monthly climatology from first principles and calibrate it
to the one real 10-year record we already have:

  SOLAR  top-of-atmosphere insolation is exact from latitude + day-of-year
         (physics.monthly_mean_toa). We derive a per-month clearness index k_t
         from the real 68 N record (surface / TOA) and apply it everywhere, so
         solar is physically correct across all latitudes.
  TEMP   annual mean falls ~1.1 C per degree latitude; seasonal amplitude grows
         poleward; a longitude term adds maritime/continental contrast.
         Calibrated so 68 N reproduces the real monthly curve.
  WIND   climatological mean ~5 m/s, windier in winter and at high latitude;
         calibrated to the real 68 N seasonal swing.

Small Gaussian noise + a longitude continentality term give the ML model real
structure to learn. The app still calls the LIVE NASA POWER API at query time;
this grid powers the instant/offline surrogate and the feasibility classifier.

Output: dashboard/data/arctic_climate_grid.csv
"""
from __future__ import annotations
import os
import sys
import numpy as np
import pandas as pd
import physics as ph
import openmeteo as om

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_CSV = os.path.join(HERE, 'data', 'nasa_power_arctic_68N_110W.csv')
OUT_CSV = os.path.join(HERE, 'data', 'arctic_climate_grid.csv')
CAL_LAT = 68.0
RNG = np.random.default_rng(42)


def calibrate_clearness():
    """Per-month clearness index k_t = real_surface_solar / monthly-mean TOA at 68 N."""
    real = pd.read_csv(REAL_CSV)
    monthly = real.groupby('month')['solar_kwh_m2_day'].mean().reindex(range(1, 13))
    toa = np.array([ph.monthly_mean_toa(CAL_LAT, m) for m in range(1, 13)])
    kt = np.divide(monthly.values, toa, out=np.zeros(12), where=toa > 0.05)
    return np.clip(kt, 0.0, 0.80)


def temp_model(lat, month, lon):
    t_annual = 64.87 - 1.10 * lat                    # -9.93 C at 68 N
    amp = 22.7 + 0.45 * (lat - 68.0)                 # larger swing poleward
    seasonal = -amp * np.cos(2 * np.pi * (month - 1) / 12)   # coldest Jan
    cont = 3.0 * np.cos(np.radians(2 * (lon + 100)))
    cont_seasonal = cont * -np.cos(2 * np.pi * (month - 1) / 12) * 0.4
    return t_annual + seasonal + cont + cont_seasonal


def wind_model(lat, month, lon):
    w_annual = 5.20 + 0.045 * (lat - 68.0)
    seasonal = 1.10 * np.cos(2 * np.pi * (month - 1) / 12)   # winter-high
    lon_term = 0.4 * np.sin(np.radians(lon + 60))
    return max(w_annual + seasonal + lon_term, 1.0)


def build_grid():
    kt = calibrate_clearness()
    lats = np.arange(50.0, 84.0 + 0.001, 2.0)
    lons = np.arange(-180.0, 180.0, 15.0)
    rows = []
    for lat in lats:
        for lon in lons:
            for mi, month in enumerate(range(1, 13)):
                toa = ph.monthly_mean_toa(lat, month)
                solar = max(toa * kt[mi] + RNG.normal(0, 0.12), 0.0)
                temp = temp_model(lat, month, lon) + RNG.normal(0, 1.0)
                wind = max(wind_model(lat, month, lon) + RNG.normal(0, 0.35), 0.8)
                rows.append((round(lat, 2), round(lon, 2), month,
                             round(solar, 3), round(wind, 3), round(temp, 2)))
    return pd.DataFrame(rows, columns=['lat', 'lon', 'month',
                        'solar_kwh_m2_day', 'wind_ms', 'temp_c'])



def build_grid_openmeteo(step_lat=2.0, step_lon=15.0):
    """Build the grid from REAL Open-Meteo ERA5 data (one API call per point).
    Falls back to the synthetic value for any point the API can't return, so a
    partial outage still yields a complete grid. Slower and network-dependent;
    run once and commit the cached CSV."""
    kt = calibrate_clearness()
    lats = np.arange(50.0, 84.0 + 0.001, step_lat)
    lons = np.arange(-180.0, 180.0, step_lon)
    rows, n_real, n_syn = [], 0, 0
    for lat in lats:
        for lon in lons:
            d = om.fetch_climatology(round(float(lat), 2), round(float(lon), 2))
            if d is not None:
                n_real += 1
                for _, r in d.iterrows():
                    rows.append((round(lat, 2), round(lon, 2), int(r['month']),
                                 round(float(r['solar_kwh_m2_day']), 3),
                                 round(float(r['wind_ms']), 3), round(float(r['temp_c']), 2)))
            else:
                n_syn += 1
                for mi, month in enumerate(range(1, 13)):
                    toa = ph.monthly_mean_toa(lat, month)
                    rows.append((round(lat, 2), round(lon, 2), month,
                                 round(max(toa * kt[mi], 0.0), 3),
                                 round(wind_model(lat, month, lon), 3),
                                 round(temp_model(lat, month, lon), 2)))
    print(f"Open-Meteo grid: {n_real} points from API, {n_syn} filled synthetically")
    return pd.DataFrame(rows, columns=['lat', 'lon', 'month',
                        'solar_kwh_m2_day', 'wind_ms', 'temp_c'])


def main():
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    use_om = '--source' in sys.argv and 'openmeteo' in sys.argv
    df = build_grid_openmeteo() if use_om else build_grid()
    df.to_csv(OUT_CSV, index=False)
    n_pts = df[['lat', 'lon']].drop_duplicates().shape[0]
    print(f"Wrote {len(df):,} rows ({n_pts} grid points x 12 months) -> {OUT_CSV}")
    chk = df[df.lat == 68.0].groupby('month')[['solar_kwh_m2_day', 'wind_ms', 'temp_c']].mean().round(2)
    print("\nGenerated 68 N climatology (real: Jul solar ~7.6, Jan temp ~-32.7, wind ~5.2):")
    print(chk.to_string())


if __name__ == '__main__':
    main()
